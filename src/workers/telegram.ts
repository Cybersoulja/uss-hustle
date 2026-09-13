// USS Hustle Telegram Operations Gateway. The configured Telegram bot handles
// delivery; task writes require explicit approval.
import { sendDailyBriefing, sendNotifyPush, NotifyEnv } from './notify';

export interface Env extends NotifyEnv {
  DB: D1Database; STORY_KV: KVNamespace; TELEGRAM_BOT_TOKEN: string;
  TELEGRAM_WEBHOOK_SECRET?: string; ZAPIER_WEBHOOK_SECRET?: string;
  ZAPIER_JIRA_CREATE_WEBHOOK?: string; OPS_ADMIN_CHAT_ID?: string; AI: any;
}
type Draft = { id: string; chat_id: number; requested_by_telegram_id: number; title: string; description: string | null; priority: string; due_at: string | null; crew_code: string; teammate_id: string | null; state: string; jira_project_key: string | null; jira_issue_key: string | null; expires_at: string; };
const CREW: Record<string, { name: string; guidance: string }> = {
  nova: { name: 'Nova Starwind', guidance: 'Bug triage, fixes, and refactors.' }, orion: { name: 'Orion Codex', guidance: 'Deployments, reliability, and release checks.' }, vega: { name: 'Vega Quantum', guidance: 'Tests, QA, and edge-case validation.' }, zara: { name: 'Zara Nebula', guidance: 'Planning, backlog ordering, and coordination.' }, atlas: { name: 'Atlas Comet', guidance: 'Release execution and rollout management.' }, trill: { name: 'Trill Astro Buzz', guidance: 'General intake, briefs, and operations.' },
};

export default { async fetch(request: Request, env: Env): Promise<Response> {
  const url = new URL(request.url);
  if (request.method === 'GET' && url.pathname === '/') return text('USS Hustle Operations Gateway Online');
  if (request.method !== 'POST') return text('Not Found', 404);
  if (url.pathname === '/notify') {
    try { return json(await sendNotifyPush(env, await request.json<any>())); } catch (error: any) { return json({ error: error.message }, 500); }
  }
  if (url.pathname === '/briefing') {
    try { return json(await sendDailyBriefing(env, await request.json<any>().catch(() => ({})))); } catch (error: any) { return json({ error: error.message }, 500); }
  }
  if (url.pathname === '/zapier/jira-status') return handleZapierStatus(request, env);
  if (url.pathname === '/zapier/reminders') return handleReminderSweep(request, env);
  if (!verifySecret(request.headers.get('X-Telegram-Bot-Api-Secret-Token'), env.TELEGRAM_WEBHOOK_SECRET)) return text('Unauthorized', 401);
  try { const update = await request.json<any>(); if (update.message) await handleMessage(update.message, env); return text('OK'); } catch (error: any) { return json({ error: error.message }, 500); }
} };

async function handleMessage(msg: any, env: Env) {
  const chatId = Number(msg.chat.id), actorId = Number(msg.from?.id), command = (msg.text || '').trim();
  if (!command) return;
  if (command.startsWith('/start')) return sendTelegram(env, chatId, helpText());
  if (!(await isAdmin(env, actorId))) return sendTelegram(env, chatId, '🔒 Operations commands are restricted to allowlisted admins.');
  if (command.startsWith('/task')) return createDraft(command.slice(5).trim(), chatId, actorId, env);
  if (command.startsWith('/delegate')) return delegateDraft(command.slice(9).trim(), chatId, env);
  if (command.startsWith('/approve')) return approveDraft(command.slice(8).trim(), chatId, actorId, env);
  if (command.startsWith('/cancel')) return cancelDraft(command.slice(7).trim(), chatId, actorId, env);
  if (command.startsWith('/status')) return status(command.slice(7).trim(), chatId, env);
  if (command.startsWith('/briefing')) return briefing(chatId, env);
  return sendTelegram(env, chatId, helpText());
}

async function createDraft(input: string, chatId: number, actorId: number, env: Env) {
  if (!input) return sendTelegram(env, chatId, 'Usage: /task Title | optional description');
  const [rawTitle, rawDescription, rawDueAt] = input.split('|'), title = rawTitle.trim().slice(0, 240), description = rawDescription?.trim() || null;
  if (!title) return sendTelegram(env, chatId, 'A task title is required.');
  const dueAt = rawDueAt?.trim() || null;
  if (dueAt && Number.isNaN(Date.parse(dueAt))) return sendTelegram(env, chatId, 'Due date must be an ISO timestamp, for example 2026-09-10T17:00:00Z.');
  const id = crypto.randomUUID().slice(0, 8).toUpperCase(), crew = selectCrew(`${title} ${description || ''}`);
  await env.DB.prepare(`INSERT INTO operation_drafts (id, requested_by_telegram_id, chat_id, title, description, due_at, crew_code, idempotency_key, expires_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, datetime('now', '+30 minutes'))`).bind(id, actorId, chatId, title, description, dueAt, crew, crypto.randomUUID()).run();
  return sendTelegram(env, chatId, preview({ id, title, description, priority: 'Medium', due_at: dueAt, crew_code: crew, teammate_id: null, state: 'PENDING', jira_project_key: null, jira_issue_key: null, chat_id: chatId, requested_by_telegram_id: actorId, expires_at: '' }));
}

async function delegateDraft(input: string, chatId: number, env: Env) {
  const [draftId, teammateHandle, requestedCrew] = input.trim().split(/\s+/);
  if (!draftId || !teammateHandle) return sendTelegram(env, chatId, 'Usage: /delegate DRAFT-ID @teammate [nova|orion|vega|zara|atlas|trill]');
  const draft = await getDraft(env, draftId);
  if (!draft || draft.chat_id !== chatId || draft.state !== 'PENDING') return sendTelegram(env, chatId, 'That draft is unavailable or no longer pending.');
  const teammate = await env.DB.prepare('SELECT id, display_name FROM teammates WHERE is_active = 1 AND telegram_username = ?').bind(teammateHandle.replace(/^@/, '')).first<any>();
  if (!teammate) return sendTelegram(env, chatId, `Unknown teammate ${teammateHandle}. Add their mapped Telegram and Jira identity before delegation.`);
  const crew = requestedCrew?.toLowerCase(); if (crew && !CREW[crew]) return sendTelegram(env, chatId, 'Unknown crew role. Choose nova, orion, vega, zara, atlas, or trill.');
  await env.DB.prepare('UPDATE operation_drafts SET teammate_id = ?, crew_code = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?').bind(teammate.id, crew || draft.crew_code, draft.id).run();
  return sendTelegram(env, chatId, preview((await getDraft(env, draft.id))!, teammate.display_name));
}

async function approveDraft(input: string, chatId: number, actorId: number, env: Env) {
  const [draftId, projectKey] = input.trim().split(/\s+/);
  if (!draftId || !projectKey) return sendTelegram(env, chatId, 'Usage: /approve DRAFT-ID PROJECTKEY');
  const draft = await getDraft(env, draftId);
  if (!draft || draft.chat_id !== chatId) return sendTelegram(env, chatId, 'Draft not found in this conversation.');
  if (draft.state === 'APPROVED') return sendTelegram(env, chatId, `Already approved as ${draft.jira_issue_key || 'a Jira issue'}.`);
  if (draft.state !== 'PENDING' || new Date(draft.expires_at).getTime() < Date.now()) return sendTelegram(env, chatId, 'This draft has expired or is no longer pending.');
  const claim = await env.DB.prepare(`UPDATE operation_drafts SET state = 'EXECUTING', jira_project_key = ?, approved_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE id = ? AND state = 'PENDING'`).bind(projectKey.toUpperCase(), draft.id).run();
  if (!claim.meta.changes) return sendTelegram(env, chatId, 'This draft is already being processed.');
  if (!env.ZAPIER_JIRA_CREATE_WEBHOOK) { await env.DB.prepare("UPDATE operation_drafts SET state = 'FAILED', updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(draft.id).run(); return sendTelegram(env, chatId, 'Jira automation is not configured. The draft was not created; connect the Zapier Jira creation webhook and retry.'); }
  try {
    const res = await fetch(env.ZAPIER_JIRA_CREATE_WEBHOOK, { method: 'POST', headers: { 'Content-Type': 'application/json', 'X-Opxero-Idempotency-Key': draft.id }, body: JSON.stringify({ draftId: draft.id, idempotencyKey: draft.id, projectKey: projectKey.toUpperCase(), title: draft.title, description: draft.description, priority: draft.priority, dueAt: draft.due_at, crew: CREW[draft.crew_code], requestedByTelegramId: actorId, teammateId: draft.teammate_id }) });
    if (!res.ok) throw new Error(`Zapier returned HTTP ${res.status}`);
    const body = await res.json<any>().catch(() => ({})), issueKey = body.issueKey || body.key || `draft-${draft.id}`;
    await env.DB.prepare("UPDATE operation_drafts SET state = 'APPROVED', jira_issue_key = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(issueKey, draft.id).run(); await sendAssignment(env, draft.id, issueKey);
    return sendTelegram(env, chatId, `✅ Approved. Jira issue ${issueKey} created for ${projectKey.toUpperCase()}.`);
  } catch (error: any) { await env.DB.prepare("UPDATE operation_drafts SET state = 'FAILED', updated_at = CURRENT_TIMESTAMP WHERE id = ?").bind(draft.id).run(); return sendTelegram(env, chatId, `⚠️ Jira creation failed safely: ${error.message}. No assignment was sent.`); }
}

async function cancelDraft(input: string, chatId: number, actorId: number, env: Env) { const draft = await getDraft(env, input.trim()); if (!draft || draft.chat_id !== chatId) return sendTelegram(env, chatId, 'Draft not found in this conversation.'); const result = await env.DB.prepare("UPDATE operation_drafts SET state = 'CANCELLED', updated_at = CURRENT_TIMESTAMP WHERE id = ? AND state = 'PENDING'").bind(draft.id).run(); if (!result.meta.changes) return sendTelegram(env, chatId, 'Only pending drafts can be cancelled.'); await audit(env, actorId, 'DRAFT_CANCELLED', { draftId: draft.id }); return sendTelegram(env, chatId, `Cancelled draft ${draft.id}. No external action was taken.`); }
async function status(input: string, chatId: number, env: Env) { const key = input.trim(); if (key) { const draft = await env.DB.prepare('SELECT * FROM operation_drafts WHERE jira_issue_key = ?').bind(key).first<Draft>(); return sendTelegram(env, chatId, draft ? `${draft.jira_issue_key}: ${draft.title}\nState: ${draft.state}\nCrew: ${CREW[draft.crew_code].name}` : 'No tracked operation matches that Jira key.'); } const rows = await env.DB.prepare("SELECT id, title, state, jira_issue_key FROM operation_drafts WHERE chat_id = ? ORDER BY created_at DESC LIMIT 10").bind(chatId).all<any>(); const lines = rows.results.map((d: any) => `• ${d.jira_issue_key || d.id} — ${d.state}: ${d.title}`); return sendTelegram(env, chatId, lines.length ? `🛰️ Recent operations\n${lines.join('\n')}` : 'No operations have been created here yet.'); }
async function briefing(chatId: number, env: Env) { const rows = await env.DB.prepare("SELECT state, COUNT(*) AS count FROM operation_drafts WHERE chat_id = ? AND created_at >= datetime('now', '-1 day') GROUP BY state").bind(chatId).all<any>(); const summary = rows.results.map((r: any) => `${r.count} ${String(r.state).toLowerCase()}`).join(', ') || 'no operations in the last day'; try { await sendDailyBriefing(env); } catch { /* Telegram briefing remains available when Notify is intentionally unconfigured. */ } return sendTelegram(env, chatId, `🌅 *Operations Briefing*\nLast 24 hours: ${summary}.\nUse /status for tracked items.`); }

async function handleZapierStatus(request: Request, env: Env): Promise<Response> { if (!verifySecret(request.headers.get('X-Opxero-Zapier-Secret'), env.ZAPIER_WEBHOOK_SECRET)) return text('Unauthorized', 401); const event = await request.json<any>(); if (!event.eventId || !event.issueKey || !event.status) return json({ error: 'eventId, issueKey, and status are required' }, 400); if (!(await recordWebhook(env, 'jira-status', event.eventId, event))) return json({ ok: true, duplicate: true }); const draft = await env.DB.prepare('SELECT * FROM operation_drafts WHERE jira_issue_key = ?').bind(event.issueKey).first<Draft>(); if (!draft) return json({ ok: true, tracked: false }); const teammate = draft.teammate_id ? await env.DB.prepare('SELECT telegram_id FROM teammates WHERE id = ?').bind(draft.teammate_id).first<any>() : null; if (teammate?.telegram_id) await deliver(env, draft.id, 'STATUS_UPDATE', `status:${event.eventId}`, teammate.telegram_id, `🛰️ ${event.issueKey} is now *${event.status}*.`); return json({ ok: true }); }
async function handleReminderSweep(request: Request, env: Env): Promise<Response> { if (!verifySecret(request.headers.get('X-Opxero-Zapier-Secret'), env.ZAPIER_WEBHOOK_SECRET)) return text('Unauthorized', 401); const event = await request.json<any>(); if (!event.eventId) return json({ error: 'eventId is required' }, 400); if (!(await recordWebhook(env, 'reminder-sweep', event.eventId, event))) return json({ ok: true, duplicate: true }); const due = await env.DB.prepare("SELECT d.*, t.telegram_id FROM operation_drafts d JOIN teammates t ON t.id = d.teammate_id WHERE d.state = 'APPROVED' AND d.due_at IS NOT NULL AND datetime(d.due_at) <= datetime('now')").all<any>(); for (const row of due.results) { await deliver(env, row.id, 'DUE_REMINDER', `due:${row.id}`, row.telegram_id, `⏰ ${row.jira_issue_key || row.id} is due. Please update its Jira status or notify an admin.`); if (env.OPS_ADMIN_CHAT_ID && new Date(row.due_at).getTime() + 86400000 <= Date.now()) await deliver(env, row.id, 'ESCALATION', `escalation:${row.id}`, Number(env.OPS_ADMIN_CHAT_ID), `🚨 ${row.jira_issue_key || row.id} remains overdue after 24 hours.`); } return json({ ok: true, examined: due.results.length }); }
async function sendAssignment(env: Env, draftId: string, issueKey: string) { const draft = await getDraft(env, draftId); if (!draft?.teammate_id) return; const teammate = await env.DB.prepare('SELECT telegram_id FROM teammates WHERE id = ?').bind(draft.teammate_id).first<any>(); if (teammate?.telegram_id) await deliver(env, draft.id, 'ASSIGNMENT', `assignment:${draft.id}`, teammate.telegram_id, `🛸 *New assignment: ${issueKey}*\n${draft.title}\n\nAdvisor: *${CREW[draft.crew_code].name}* — ${CREW[draft.crew_code].guidance}`); }
async function deliver(env: Env, draftId: string, kind: string, key: string, target: number, message: string) { const id = crypto.randomUUID(), saved = await env.DB.prepare('INSERT OR IGNORE INTO operation_deliveries (id, draft_id, kind, idempotency_key, target_telegram_id) VALUES (?, ?, ?, ?, ?)').bind(id, draftId, kind, key, target).run(); if (!saved.meta.changes) return; try { const sent = await sendTelegram(env, target, message); await env.DB.prepare("UPDATE operation_deliveries SET status = 'DELIVERED', provider_message_id = ?, delivered_at = CURRENT_TIMESTAMP WHERE id = ?").bind(String(sent?.message_id || ''), id).run(); } catch (error: any) { await env.DB.prepare("UPDATE operation_deliveries SET status = 'FAILED', error_message = ? WHERE id = ?").bind(error.message, id).run(); } }
async function sendTelegram(env: Env, chatId: number, body: string): Promise<any> { const res = await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ chat_id: chatId, text: body, parse_mode: 'Markdown', disable_web_page_preview: true }) }); const result = await res.json<any>(); if (!res.ok || !result.ok) throw new Error(result.description || `Telegram HTTP ${res.status}`); return result.result; }
async function isAdmin(env: Env, telegramId: number) { return !!(await env.DB.prepare('SELECT 1 FROM telegram_admins WHERE telegram_id = ? AND is_active = 1').bind(telegramId).first()); }
async function getDraft(env: Env, id: string) { return env.DB.prepare('SELECT * FROM operation_drafts WHERE id = ?').bind(id.toUpperCase()).first<Draft>(); }
async function recordWebhook(env: Env, source: string, eventId: string, payload: unknown) { const r = await env.DB.prepare('INSERT OR IGNORE INTO operation_webhook_events (id, source, external_event_id, payload) VALUES (?, ?, ?, ?)').bind(crypto.randomUUID(), source, eventId, JSON.stringify(payload)).run(); return !!r.meta.changes; }
async function audit(env: Env, actorId: number, eventType: string, payload: unknown) { await env.DB.prepare('INSERT INTO operation_audit_events (id, actor_telegram_id, event_type, payload) VALUES (?, ?, ?, ?)').bind(crypto.randomUUID(), actorId, eventType, JSON.stringify(payload)).run(); }
function selectCrew(text: string) { const t = text.toLowerCase(); if (/deploy|production|rollback/.test(t)) return 'orion'; if (/test|qa|coverage/.test(t)) return 'vega'; if (/sprint|plan|backlog|meeting/.test(t)) return 'zara'; if (/release train|rollout/.test(t)) return 'atlas'; if (/bug|fix|refactor|error/.test(t)) return 'nova'; return 'trill'; }
function preview(draft: Draft, teammate?: string) { const crew = CREW[draft.crew_code]; return `📝 *Pending task ${draft.id}*\n${draft.title}${draft.description ? `\n${draft.description}` : ''}\n\nProject: choose at approval\nDue: ${draft.due_at || 'not set'}\nOwner: ${teammate || 'unassigned'}\nAdvisor: *${crew.name}* — ${crew.guidance}\n\nApprove: \`/approve ${draft.id} PROJECTKEY\`\nDelegate: \`/delegate ${draft.id} @teammate [crew]\`\nCancel: \`/cancel ${draft.id}\`\nExpires in 30 minutes.`; }
function helpText() { return '🛸 *Opxero Operations*\n/task Title | description | 2026-09-10T17:00:00Z\n/delegate DRAFT-ID @teammate [crew]\n/approve DRAFT-ID PROJECTKEY — create after review\n/cancel DRAFT-ID\n/status [JIRA-KEY]\n/briefing'; }
function verifySecret(actual: string | null, expected?: string) { if (!expected || !actual || actual.length !== expected.length) return false; let diff = 0; for (let i = 0; i < actual.length; i++) diff |= actual.charCodeAt(i) ^ expected.charCodeAt(i); return diff === 0; }
function text(body: string, status = 200) { return new Response(body, { status }); }
function json(body: unknown, status = 200) { return new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } }); }
