-- =============================================================================
-- Space Age Hustle: Core Cloudflare D1 Database Schema
-- =============================================================================

-- 1. Players / Commanders
CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,
    telegram_id INTEGER UNIQUE NOT NULL,
    username TEXT,
    callsign TEXT DEFAULT 'Commander',
    rank TEXT DEFAULT 'Hustler-in-Training',
    xp INTEGER DEFAULT 0,
    level INTEGER DEFAULT 1,
    streak_days INTEGER DEFAULT 0,
    last_active_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Agents Roster
CREATE TABLE IF NOT EXISTS agents (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    name TEXT NOT NULL, -- 'Trill Astro Buzz', 'Nova Starwind', etc.
    code_name TEXT NOT NULL, -- 'buzz', 'nova', 'orion', 'vega', 'zara', 'atlas'
    level INTEGER DEFAULT 1,
    xp INTEGER DEFAULT 0,
    loyalty INTEGER DEFAULT 50, -- 0 to 100
    energy INTEGER DEFAULT 100, -- 0 to 100
    special_power TEXT NOT NULL,
    evolution_stage TEXT DEFAULT 'Genesis', -- Genesis, Awakened, Enlightened, Transcended
    is_unlocked BOOLEAN DEFAULT 0,
    unlocked_at TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

-- 3. Work Missions / Quests
CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    jira_key TEXT UNIQUE, -- e.g., 'PROJ-102'
    title TEXT NOT NULL,
    description TEXT,
    category TEXT DEFAULT 'Feature', -- Bug, Feature, Deploy, Test, Meeting
    priority TEXT DEFAULT 'Medium', -- Low, Medium, High, Cosmic P1
    base_xp INTEGER DEFAULT 50,
    assigned_agent_id TEXT,
    status TEXT DEFAULT 'Queued', -- Queued, In Orbit, Review, Completed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_agent_id) REFERENCES agents(id)
);

-- 4. Inventory & Loot Items
CREATE TABLE IF NOT EXISTS inventory (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    item_code TEXT NOT NULL, -- 'quantum_coffee', 'warp_accelerator', 'tachyon_crystal'
    name TEXT NOT NULL,
    description TEXT,
    quantity INTEGER DEFAULT 1,
    acquired_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

-- 5. Work Metrics & Telemetry (Fuel for Agent Genesis)
CREATE TABLE IF NOT EXISTS player_stats (
    player_id TEXT PRIMARY KEY,
    bugs_fixed INTEGER DEFAULT 0,
    deployments_successful INTEGER DEFAULT 0,
    tests_written INTEGER DEFAULT 0,
    meetings_led INTEGER DEFAULT 0,
    weekly_deploys INTEGER DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (player_id) REFERENCES players(id) ON DELETE CASCADE
);

-- 6. Transmission & Event Logs
CREATE TABLE IF NOT EXISTS logs (
    id TEXT PRIMARY KEY,
    player_id TEXT NOT NULL,
    agent_id TEXT,
    event_type TEXT NOT NULL, -- 'MISSION_COMPLETE', 'AGENT_UNLOCKED', 'LEVEL_UP'
    payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 7. Operations command-center configuration. Populate these tables through an
-- operator-controlled migration; Telegram identities are never inferred from a display name.
CREATE TABLE IF NOT EXISTS telegram_admins (
    telegram_id INTEGER PRIMARY KEY,
    display_name TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS teammates (
    id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    telegram_id INTEGER UNIQUE,
    telegram_username TEXT UNIQUE,
    jira_account_id TEXT,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS operation_drafts (
    id TEXT PRIMARY KEY,
    requested_by_telegram_id INTEGER NOT NULL,
    chat_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    priority TEXT NOT NULL DEFAULT 'Medium',
    due_at TIMESTAMP,
    crew_code TEXT NOT NULL,
    teammate_id TEXT,
    state TEXT NOT NULL DEFAULT 'PENDING', -- PENDING, EXECUTING, APPROVED, CANCELLED, EXPIRED, FAILED
    jira_project_key TEXT,
    jira_issue_key TEXT UNIQUE,
    idempotency_key TEXT NOT NULL UNIQUE,
    expires_at TIMESTAMP NOT NULL,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teammate_id) REFERENCES teammates(id)
);

CREATE INDEX IF NOT EXISTS idx_operation_drafts_state_expiry ON operation_drafts(state, expires_at);

CREATE TABLE IF NOT EXISTS operation_deliveries (
    id TEXT PRIMARY KEY,
    draft_id TEXT,
    kind TEXT NOT NULL, -- ASSIGNMENT, DUE_REMINDER, ESCALATION, STATUS_UPDATE
    idempotency_key TEXT NOT NULL UNIQUE,
    target_telegram_id INTEGER,
    status TEXT NOT NULL DEFAULT 'PENDING',
    provider_message_id TEXT,
    error_message TEXT,
    delivered_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (draft_id) REFERENCES operation_drafts(id)
);

CREATE TABLE IF NOT EXISTS operation_webhook_events (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    external_event_id TEXT NOT NULL,
    payload TEXT NOT NULL,
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(source, external_event_id)
);

CREATE TABLE IF NOT EXISTS operation_audit_events (
    id TEXT PRIMARY KEY,
    actor_telegram_id INTEGER,
    event_type TEXT NOT NULL,
    payload TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
