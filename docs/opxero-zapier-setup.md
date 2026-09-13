# @opxero Operations Setup

## 1. Deploy configuration

Set the Worker secrets `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`,
`ZAPIER_WEBHOOK_SECRET`, `ZAPIER_JIRA_CREATE_WEBHOOK`, and `OPS_ADMIN_CHAT_ID`.
Register Telegram's webhook with the same `TELEGRAM_WEBHOOK_SECRET` as its
`secret_token`. The Telegram bot already connected in Zapier is the production
delivery account for this framework.

Run the D1 schema migration, then seed `telegram_admins` with each operator's
numeric Telegram ID and `teammates` with their Telegram username, Telegram ID,
and Jira account ID.

## 2. Create the Jira creation Zap

Create a Zapier Catch Hook that receives the Worker approval payload. Add Jira
Cloud's **Create Issue** action and select the project and issue type in Zapier
so its dynamic field schema becomes available. Map the incoming title,
description, priority, due date, and mapped Jira assignee. Return JSON with
`issueKey` through a Zapier webhook response. Preserve the incoming
`X-Opxero-Idempotency-Key` in a deduplication step before Jira creation.

Copy the Catch Hook URL into `ZAPIER_JIRA_CREATE_WEBHOOK`.

## 3. Create status and reminder Zaps

- **Jira status change:** send `eventId`, `issueKey`, and `status` to
  `POST /zapier/jira-status`, including `X-Opxero-Zapier-Secret`.
- **Scheduled reminder:** run at the desired interval and send a unique
  `eventId` to `POST /zapier/reminders` with the same header.

The Worker stores each event ID, so Zapier retries cannot create duplicate
status messages or reminders.

## Command reference

`/task Title | description | 2026-09-10T17:00:00Z` creates a 30-minute draft.
`/delegate DRAFT-ID @teammate [crew]` assigns a mapped teammate and crew advisor.
`/approve DRAFT-ID PROJECTKEY` performs the single approved Jira write.
`/cancel DRAFT-ID`, `/status [JIRA-KEY]`, and `/briefing` do not write to Jira.
