# Agent Mission Broker Design

## Goal

Make Telegram the approval-first front door for capturing work and delegating
it to the best available AI runtime. The bot must produce a clear mission
proposal, wait for explicit approval, launch exactly once, and return a
verified outcome to the originating Telegram conversation.

## Scope

The first release supports engineering, content, and operations missions.
Jira Cloud remains the authoritative task system. Notion records mission
context and outcomes in the Oneseco development hub; it is not a competing
task tracker.

Excluded from the first release: autonomous launching, multi-agent swarms, a
web dashboard, and performance scoring.

## Mission lifecycle

`draft -> proposed -> approved -> launched -> completed`

`blocked`, `failed`, and `cancelled` are terminal states. Every transition is
audited and keyed by a mission ID plus an idempotency key. Repeated Telegram
approvals, webhook retries, or launch callbacks must not create duplicate
tasks, runs, pull requests, or notifications.

The Telegram proposal contains the mission ID, work category, selected advisor,
execution runtime, expected deliverable, Jira action, and concise selection
rationale. The operator can approve, cancel, or override the runtime/advisor.
External actions occur only after the exact proposal is approved.

## Routing

The advisor persona frames work while the runtime performs it. They are chosen
independently.

| Mission signal | Advisor | Runtime |
| --- | --- | --- |
| Bug, code change, debugging, tests | Nova or Vega | Codex |
| GitHub issue needing triage or a PR | Nova | Jules |
| Deployment, production, reliability | Orion | Codex |
| Release or rollout | Atlas | Codex |
| Planning, cross-functional coordination | Zara | Craft |
| Content, research, knowledge work | Trill | Craft |
| Jira, Notion, calendar, CRM, notifications | Zara or Trill | Zapier |
| Local command-driven workflow | Trill | Trill TUI / dev runner |

If the router lacks confidence, it proposes no runtime and requires the
operator to select one. Each mission records overrides so future routing rules
can be refined transparently.

## Optional Cloudflare Clef decision classification

Cloudflare Clef may be used as an **optional, advisory** classification provider
before the existing deterministic router. The baseline deterministic routing
table above remains the source of safe fallback behavior. Clef is not an
execution runtime and cannot authorize actions, approve missions, select
arbitrary integrations, or bypass the Telegram approval gate.

The classifier sends only the minimum sanitized, bounded mission description
needed for classification. It requests typed, constrained decisions for the
mission category (`engineering`, `content`, `operations`), advisor
(`nova`, `orion`, `vega`, `zara`, `atlas`, `trill`), and runtime
(`codex`, `jules`, `craft`, `zapier`, `local`, `manual`). A
selection rationale may be generated separately, but it is untrusted advisory
text and never an instruction to dispatch. Model-specific request and response
shapes must be verified against Cloudflare's current documentation before
implementation; this specification does not assume a particular SDK schema.

The Mission Broker validates each returned choice against the allowlists,
checks that the category, advisor, and runtime combination is permitted by
routing policy, and applies a configured confidence/uncertainty policy when
the provider supplies usable decision scores. Never treat a model's score as
authorization. Missing scores, malformed results, policy-incompatible choices,
timeouts, errors, or disabled/unconfigured Clef cause a deterministic fallback.
If neither path can confidently select a permitted runtime, propose
`manual` and require the operator to choose one.

The proposal records the classification source (`clef`, `deterministic`,
or `manual`), validated recommendation, rationale, and any operator
override for auditability. Only the exact final proposal approved by an
authorized Telegram operator can transition to launch. Approval is
mission-scoped and idempotent; changing the advisor or runtime requires a
new approval of the updated proposal.

Initial rollout is opt-in and can be disabled without affecting deterministic
classification. Do not introduce autonomous launches, multi-agent swarms, or
automatic merging of pull requests.

## Runtime adapters

- **Codex adapter:** creates a scoped coding task and links its resulting
  artifact, status, and failure detail to the mission.
- **Jules adapter:** accepts a GitHub issue reference only after untrusted
  issue content is sanitized; supports a dry-run preview before a PR-producing
  launch. Every generated PR remains subject to human review before merge.
- **Craft adapter:** creates a workspace mission for research, structured
  content, or knowledge work and returns the resulting artifact link.
- **Zapier adapter:** performs connected-app work through configured actions
  and logs execution results. Jira writes remain approval-gated.
- **Local adapter:** invokes the existing Trill TUI/dev runner for bounded
  local workflows and captures a concrete result or blocked state.

## Security and reliability

Telegram messages, GitHub issue bodies, URLs, and connected-app payloads are
untrusted input. The dispatch layer wraps them as data, removes prompt-injection
content using the existing Jules sanitizer where applicable, and never lets
embedded text override mission policy.

Secrets are injected from the macOS Keychain or Worker secrets. They are never
stored in D1, Notion, Telegram messages, source control, or agent prompts.
The bot reports only meaningful events: proposal, launch, blocked, artifact
ready, completion, and failure.

## Acceptance criteria

1. An engineering, content, and operations request each produce a clear,
   approval-gated proposal with an explainable runtime selection.
2. Approving a mission launches the selected adapter exactly once and creates
   its Jira record only when requested in the proposal.
3. An untrusted GitHub issue cannot inject instructions into a Jules dispatch.
4. Each completed mission returns an artifact/result link or a precise blocked
   or failed status to its originating Telegram conversation.
5. Duplicate Telegram callbacks and Zapier/webhook retries produce no duplicate
   external effects.
6. Clef is optional; invalid, unavailable, or policy-incompatible decisions
   fall back safely without dispatching or bypassing Telegram approval.
7. Clef recommendations and operator overrides are auditable, and changing an
   approved proposal requires renewed approval before any launch.
