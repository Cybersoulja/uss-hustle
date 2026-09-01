// =============================================================================
// Cloudflare Worker: Space Age Hustle - Notify! (Pingie) Dispatcher
// =============================================================================

export interface NotifyEnv {
  NOTIFY_DEVICE_ID?: string;
  NOTIFY_TOKEN?: string;
  NOTIFY_ICON_URL?: string;
  ONESECO_AVATAR_URL?: string;
}

export interface NotifyPayload {
  text: string;
  title?: string;
  groupType?: string;
  iconUrl?: string;
  imageUrl?: string;
}

export interface SendNotifyOptions {
  deviceId?: string;
  token?: string;
  text: string;
  title?: string;
  groupType?: string;
  iconUrl?: string;
  imageUrl?: string;
}

const DEFAULT_PINGIE_API = "https://notify.pingie.com";
const DEFAULT_AVATAR = "https://raw.githubusercontent.com/cybersoulja/space-age-hustle/main/assets/oneseco-avatar.jpeg";

/**
 * Dispatch a push notification to Notify! (Pingie) API.
 */
export async function sendNotifyPush(env: NotifyEnv, options: SendNotifyOptions): Promise<any> {
  const targetId = options.deviceId || env.NOTIFY_DEVICE_ID;
  const token = options.token || env.NOTIFY_TOKEN;

  if (!targetId || !token) {
    throw new Error("Missing NOTIFY_DEVICE_ID or NOTIFY_TOKEN credentials.");
  }

  const iconUrl = options.iconUrl || env.NOTIFY_ICON_URL || env.ONESECO_AVATAR_URL || DEFAULT_AVATAR;

  const url = `${DEFAULT_PINGIE_API}/notify-json/${encodeURIComponent(targetId)}?token=${encodeURIComponent(token)}`;

  const body: NotifyPayload = {
    text: options.text,
  };

  if (options.title) body.title = options.title;
  if (options.groupType) body.groupType = options.groupType;
  if (iconUrl) body.iconUrl = iconUrl;
  if (options.imageUrl) body.imageUrl = options.imageUrl;

  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "User-Agent": "USS-Hustle-Worker/1.0",
    },
    body: JSON.stringify(body),
  });

  const responseText = await res.text();
  let parsed: any;
  try {
    parsed = JSON.parse(responseText);
  } catch {
    parsed = { raw: responseText, status: res.status };
  }

  if (!res.ok) {
    throw new Error(`Notify! API error (HTTP ${res.status}): ${JSON.stringify(parsed)}`);
  }

  return parsed;
}

/**
 * Send Daily Morning Briefing Push.
 */
export async function sendDailyBriefing(env: NotifyEnv, options?: {
  title?: string;
  priorities?: string[];
  quote?: string;
  deviceId?: string;
}): Promise<any> {
  const priorities = options?.priorities || [
    "Review open pull requests & active CI pipelines",
    "Check Jira sprint backlog & triage P1 bugs",
    "Sync agent states & claim daily login XP (+150 XP)"
  ];

  const priorityText = priorities.map((p, idx) => `  ${idx + 1}. ${p}`).join("\n");
  const quote = options?.quote || "Velocity is uncapped. Ship destiny today.";

  const text = [
    "🛸 Commander, gravity is offline and today's orbital cycle is live!",
    "",
    "🎯 Top Orbital Priorities:",
    priorityText,
    "",
    `⚡ Daily Motivation: "${quote}"`,
    "",
    "🛰️ Trill Astro Buzz standing by."
  ].join("\n");

  return sendNotifyPush(env, {
    deviceId: options?.deviceId,
    title: options?.title || "🌅 USS Hustle — Daily Morning Briefing",
    text,
    groupType: "daily-briefing",
  });
}

/**
 * Send Critical P1 Bug / Anomaly Alert.
 */
export async function sendCriticalAlert(env: NotifyEnv, options: {
  title?: string;
  text: string;
  imageUrl?: string;
  deviceId?: string;
}): Promise<any> {
  return sendNotifyPush(env, {
    deviceId: options.deviceId,
    title: options.title || "🚨 P1 ANOMALY DETECTED",
    text: options.text,
    groupType: "critical-alerts",
    imageUrl: options.imageUrl,
  });
}

/**
 * Send Deployment Status Push.
 */
export async function sendDeploymentAlert(env: NotifyEnv, options: {
  repo: string;
  status: "SUCCESS" | "FAILED" | "ROLLBACK";
  version?: string;
  text?: string;
  deviceId?: string;
}): Promise<any> {
  const text = options.text || `Orion Codex report: ${options.repo} deployment ${options.status.toLowerCase()} (version: ${options.version || "latest"}).`;
  return sendNotifyPush(env, {
    deviceId: options.deviceId,
    title: `🚀 Deployment ${options.status}: ${options.repo}`,
    text,
    groupType: "deployments",
  });
}
