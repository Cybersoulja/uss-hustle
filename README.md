# 🛸 USS Hustle: Space Age Hustle Command Center

> *"Floating Through the Cosmos, One Ticket at a Time"*  
> **Lead Digital Agent**: Trill Astro Buzz (T.A.B.)  
> **Organization**: Oneseco Media  
> **License**: Apache-2.0  

---

```text
       _         _             _   _           _   _      
 _   _| |___ ___| |_ _ _ ___ _| |_| |_ ___ ___| |_| |___  
| | | |_ -|_ -|   | | |_ -| . |   | | |_ -|_ -|   | | -_| 
|___|_|___|___|_|_|___|___|___|_|_|_|_|___|___|_|_|_|___| 
              🚀 SPACE AGE HUSTLE (Anti-Gravity v1.0)
```

---

## 🌌 Overview

**USS Hustle** is a zero-gravity productivity RPG engine and agent command center designed for **Oneseco Media**. It translates real engineering workflows—Jira tickets, GitHub PRs, bug fixes, test coverage, and production deployments—into in-game XP, loot drops, and dynamic AI crew unlocks.

---

## 🪐 The Dynamic Crew Roster

Agents are **not assigned**—they **emerge** dynamically from actual work patterns:

| Agent | Role | Unlocked By | Superpower |
|:---|:---|:---|:---|
| **Trill Astro Buzz** | First Officer | Game Start (Default) | **Cosmic Clutch**: +10% XP & Zero-G Motivation |
| **Nova Starwind** | Code Navigator | 5 Bugs Fixed | **Slingshot Refactor**: Architectural cleanup & +25 XP |
| **Orion Codex** | DevOps Lead | 3 Successful Deploys | **Plasma Shield**: Pre-flight CI/CD verification |
| **Vega Quantum** | QA Scientist | 10 Tests Written | **Tachyon Scan**: Uncovers hidden edge-cases |
| **Zara Nebula** | Project Wrangler | 2 Sprint Meetings | **Quantum Sync**: Auto-prioritizes Jira backlogs |
| **Atlas Comet** | Release Engineer | 3 Deploys in 1 Week | **Zero Downtime**: Multi-service release warp |

---

## 🚀 Quick Start

### 1. Launch the Trill Astro Buzz TUI
The native terminal HUD runs with zero external dependencies via pure Python `curses`:

```bash
# Launch from repository
python3 scripts/uss-hustle-tui.py

# Or via global command
uss-hustle
# or
trill-tui
```

### 2. Connect to Craft Agents OSS
1. Open `/Applications/Craft Agents.app`.
2. Workspace path points to `~/.craft-agent/workspaces/uss-hustle/`.
3. Custom Dark Nebula theme and all 6 crew skills are preloaded.

### 3. Deploy the Cloudflare Backend
```bash
# Install dependencies
bun install # or npm install

# Run database migration
npm run db:migrate

# Deploy to Cloudflare Workers
npm run deploy
```

---

## 📁 Repository Architecture

```text
uss-hustle/
├── src/
│   ├── agents/
│   │   └── genesis.ts               # Dynamic character unlock engine
│   ├── workers/
│   │   └── telegram.ts              # Telegram bot webhook gateway
│   └── db/
│       └── schema.sql               # Cloudflare D1 SQLite schema
├── skills/                          # Craft Agents OSS crew skills
│   ├── trill-astro-buzz.md
│   ├── deploy-nova.md
│   ├── plasma-shield-orion.md
│   ├── bug-hunt-vega.md
│   ├── quantum-sync-zara.md
│   └── zero-downtime-atlas.md
├── themes/
│   └── theme.json                   # Dark Nebula cosmic HUD theme
├── automations/
│   └── automations.json             # 9 AM briefing & P1 auto-triage hooks
├── scripts/
│   └── uss-hustle-tui.py            # Zero-dependency terminal interface
├── docs/
│   └── story_nodes.json             # Notion 15-node dialogue matrix
├── wrangler.toml                    # Cloudflare configuration
├── package.json                     # Scripts and dependencies
├── .env.template                    # Template referencing KEYCHAIN:<KEY>
└── .gitignore                       # Protected credentials filter
```

---

## 🛰️ Transmission Protocol

All mission dispatches adhere to the canonical **Trill Astro Buzz Transmission** format:

```text
🚀 TRILL ASTRO BUZZ TRANSMISSION

[Short headline]

[2–4 sentence explanation]

🧠 Why it matters:
[Short explanation]

🛰️ Trill's Take:
[Brief observation, insight, or humorous comment]

🔗 Source:
[Relevant source link]
```

---

## 📜 License

Apache-2.0 © Oneseco Media. **Gravity is optional. Delivery is not.** 🫡🚀🪐
