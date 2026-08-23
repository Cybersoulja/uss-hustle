#!/usr/bin/env python3
"""
USS HUSTLE COMMAND CENTER - TRILL ASTRO BUZZ TUI
Space Age Hustle: The Zero-Gravity Productivity RPG Terminal Interface
Pure Python & standard library 'curses' - zero external dependencies.
"""

import curses
import datetime
import json
import os
import random
import sys
import subprocess

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(SCRIPT_DIR)
STATE_FILE = os.path.join(WORKSPACE_DIR, "game_state.json")

BUZZ_QUOTES = [
    "Every commit is a step on the moon of progress. Keep your thrusters firing!",
    "The galaxy doesn't wait. Neither should your pull requests.",
    "You're not just shipping code, Commander — you're shipping DESTINY.",
    "Coffee: the dark matter that powers the universe. Refuel and conquer.",
    "In zero-gravity, technical debt floats right to the surface where Nova can vaporize it.",
    "Warp speed isn't a velocity — it's a mindset.",
    "Gravity is optional. Delivery is mandatory.",
    "When in doubt: Commit, Deploy, and Repeat."
]

DEFAULT_STATE = {
    "commander": {
        "callsign": "Commander",
        "rank": "Junior Hustler",
        "level": 3,
        "xp": 420,
        "xp_to_next": 600,
        "streak_days": 7,
        "status": "Hustling"
    },
    "stats": {
        "bugs_fixed": 6,
        "deployments": 4,
        "tests_written": 12,
        "meetings_led": 3,
        "weekly_deploys": 3
    },
    "agents": [
        {
            "id": "buzz",
            "name": "Trill Astro Buzz",
            "role": "First Officer",
            "title": "Cosmic Clutch",
            "rank": "LEGEND",
            "stars": "⭐⭐⭐⭐⭐",
            "level": 5,
            "xp": 1250,
            "loyalty": 100,
            "energy": 100,
            "stage": "Transcended",
            "power": "Cosmic Clutch (+10% XP & Zero-G Motivation)",
            "catchphrase": "The grind never stops, Commander. Gravity is optional.",
            "unlocked": True
        },
        {
            "id": "nova",
            "name": "Nova Starwind",
            "role": "Code Navigator",
            "title": "Slingshot Refactor",
            "rank": "EXPERT",
            "stars": "⭐⭐⭐⭐",
            "level": 4,
            "xp": 820,
            "loyalty": 92,
            "energy": 85,
            "stage": "Enlightened",
            "power": "Slingshot Refactor (Complexity breakdown & +25 XP)",
            "catchphrase": "I can see clean code from orbit.",
            "unlocked": True
        },
        {
            "id": "orion",
            "name": "Orion Codex",
            "role": "DevOps Engineer",
            "title": "Plasma Shield",
            "rank": "VETERAN",
            "stars": "⭐⭐⭐",
            "level": 3,
            "xp": 640,
            "loyalty": 78,
            "energy": 92,
            "stage": "Awakened",
            "power": "Plasma Shield (Zero-downtime preflight CI/CD)",
            "catchphrase": "Pipelines run faster than light.",
            "unlocked": True
        },
        {
            "id": "vega",
            "name": "Vega Quantum",
            "role": "QA Scientist",
            "title": "Tachyon Scan",
            "rank": "SPECIALIST",
            "stars": "⭐⭐⭐",
            "level": 3,
            "xp": 580,
            "loyalty": 72,
            "energy": 90,
            "stage": "Awakened",
            "power": "Tachyon Scan (Edge-case discovery & test fixtures)",
            "catchphrase": "No bug escapes the tachyon scan.",
            "unlocked": True
        },
        {
            "id": "zara",
            "name": "Zara Nebula",
            "role": "Project Wrangler",
            "title": "Quantum Sync",
            "rank": "SPECIALIST",
            "stars": "⭐⭐⭐",
            "level": 3,
            "xp": 510,
            "loyalty": 68,
            "energy": 88,
            "stage": "Awakened",
            "power": "Quantum Sync (Auto-prioritize backlogs & sprints)",
            "catchphrase": "Backlogs aligned across all light-years.",
            "unlocked": True
        },
        {
            "id": "atlas",
            "name": "Atlas Comet",
            "role": "Release Engineer",
            "title": "Zero Downtime",
            "rank": "LEGEND",
            "stars": "⭐⭐⭐⭐⭐",
            "level": 5,
            "xp": 1400,
            "loyalty": 95,
            "energy": 95,
            "stage": "Transcended",
            "power": "Zero Downtime (Multi-service release cutover warp)",
            "catchphrase": "Zero downtime is a universal law.",
            "unlocked": True
        }
    ],
    "missions": [
        {
            "id": "JIRA-101",
            "title": "Resolve OAuth2 Token Refresh Race Condition",
            "category": "Bug",
            "priority": "🔥 Cosmic P1",
            "xp": 110,
            "assigned_to": "Nova Starwind",
            "status": "In Orbit (75%)"
        },
        {
            "id": "JIRA-102",
            "title": "Deploy Cloudflare D1 Schema Migrations",
            "category": "DevOps",
            "priority": "⚡ High Orbit",
            "xp": 90,
            "assigned_to": "Orion Codex",
            "status": "Queued"
        },
        {
            "id": "JIRA-103",
            "title": "Write Tachyon Test Suite for Gateway API",
            "category": "QA",
            "priority": "🔬 Standard",
            "xp": 80,
            "assigned_to": "Vega Quantum",
            "status": "Queued"
        },
        {
            "id": "JIRA-104",
            "title": "Synchronize Sprint Backlog with Notion Story Matrix",
            "category": "Project",
            "priority": "🌌 Standard",
            "xp": 70,
            "assigned_to": "Zara Nebula",
            "status": "Queued"
        }
    ],
    "inventory": [
        {"name": "Quantum Coffee", "count": 3, "desc": "Restores 25% energy to active crew member"},
        {"name": "Warp Accelerator", "count": 1, "desc": "Doubles XP on next mission completion"},
        {"name": "Tachyon Crystal", "count": 2, "desc": "Instantly discovers 3 hidden edge cases"},
        {"name": "Quantum Levitation Token", "count": 1, "desc": "Zero-gravity shield (+50% bonus on PR review)"}
    ],
    "dispatches": [
        {
            "headline": "Craft Agents OSS Cockpit Docked",
            "date": "2026.08.22",
            "summary": "Installed native macOS desktop HUD with 6 custom crew skills.",
            "source": "/Applications/Craft Agents.app"
        },
        {
            "headline": "Telegram Gateway API Online",
            "date": "2026.08.22",
            "summary": "Direct OTP deliverability and verification channel enabled with TTL refunds.",
            "source": "https://gatewayapi.telegram.org"
        }
    ]
}

def load_game_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_STATE.copy()

def save_game_state(state):
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2)
    except Exception:
        pass

class USSHustleTUI:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.state = load_game_state()
        self.active_tab = 0  # 0: Bridge/HUD, 1: Crew, 2: Missions, 3: Cargo, 4: Transmissions
        self.selected_row = 0
        self.current_quote = random.choice(BUZZ_QUOTES)
        self.status_banner = "⚡ Zero-Gravity Anti-Gravity Field: 100% | All Systems Nominal"
        self.tabs = ["[1] 🚀 BRIDGE / HUD", "[2] 🪐 CREW ROSTER", "[3] 📋 MISSIONS", "[4] 💎 CARGO BAY", "[5] 📡 DISPATCHES"]

        curses.curs_set(0)
        self.stdscr.nodelay(False)
        self.stdscr.keypad(True)
        self.init_colors()

    def init_colors(self):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_CYAN, -1)     # Cosmic Blue / Cyan
        curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN) # Inverted Cyan Highlight
        curses.init_pair(3, curses.COLOR_GREEN, -1)    # Success / Green
        curses.init_pair(4, curses.COLOR_RED, -1)      # Alert / Red
        curses.init_pair(5, curses.COLOR_YELLOW, -1)   # Gold / XP / Stars
        curses.init_pair(6, curses.COLOR_MAGENTA, -1)  # Nebula Purple
        curses.init_pair(7, curses.COLOR_BLACK, curses.COLOR_WHITE) # Status Footer
        curses.init_pair(8, curses.COLOR_BLACK, curses.COLOR_YELLOW) # Gold Highlight

    def draw_header(self, max_y, max_x):
        banner = " 🛸 USS HUSTLE COMMAND CENTER — SPACE AGE HUSTLE (Anti-Gravity v1.0) "
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(0, 1, banner[:max_x-2])
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)

        # Draw Nav Tabs
        x = 1
        for i, tab in enumerate(self.tabs):
            if i == self.active_tab:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                self.stdscr.addstr(1, x, f" {tab} ")
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.attron(curses.color_pair(6))
                self.stdscr.addstr(1, x, f" {tab} ")
                self.stdscr.attroff(curses.color_pair(6))
            x += len(tab) + 3
            if x >= max_x - 10:
                break

    def draw_footer(self, max_y, max_x):
        # Status Banner
        self.stdscr.attron(curses.color_pair(5) | curses.A_BOLD)
        self.stdscr.addstr(max_y - 2, 2, f"➤ {self.status_banner}"[:max_x-4])
        self.stdscr.attroff(curses.color_pair(5) | curses.A_BOLD)

        # Keybindings Bar
        help_str = " [1-5] Tabs  [↑/↓/j/k] Navigate  [Enter/c] Check-in  [m] Buzz Quote  [n] New Mission  [q] Quit "
        help_str = help_str.ljust(max_x - 1)
        self.stdscr.addstr(max_y - 1, 0, help_str[:max_x-1], curses.color_pair(7))

    def draw_bridge_hud(self, start_y, height, width):
        cmd = self.state["commander"]
        stats = self.state["stats"]

        # Left Column: Commander Profile & XP
        left_w = min(40, width // 2)
        right_w = width - left_w - 3
        right_x = left_w + 3

        # Box 1: Commander Profile
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(start_y, 1, "┌" + "─" * (left_w - 2) + "┐")
        self.stdscr.addstr(start_y, 3, " 👨‍🚀 Commander Dossier ", curses.color_pair(5) | curses.A_BOLD)
        for y in range(1, 10):
            self.stdscr.addstr(start_y + y, 1, "│")
            self.stdscr.addstr(start_y + y, left_w, "│")
        self.stdscr.addstr(start_y + 10, 1, "└" + "─" * (left_w - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1))

        self.stdscr.addstr(start_y + 2, 3, f"Callsign  : ", curses.A_BOLD)
        self.stdscr.addstr(start_y + 2, 15, cmd["callsign"], curses.color_pair(5) | curses.A_BOLD)

        self.stdscr.addstr(start_y + 3, 3, f"Rank      : ", curses.A_BOLD)
        self.stdscr.addstr(start_y + 3, 15, cmd["rank"], curses.color_pair(3))

        self.stdscr.addstr(start_y + 4, 3, f"Level     : ", curses.A_BOLD)
        self.stdscr.addstr(start_y + 4, 15, f"Lvl {cmd['level']}", curses.color_pair(1))

        self.stdscr.addstr(start_y + 5, 3, f"Streak    : ", curses.A_BOLD)
        self.stdscr.addstr(start_y + 5, 15, f"{cmd['streak_days']} Days 🔥", curses.color_pair(4) | curses.A_BOLD)

        self.stdscr.addstr(start_y + 6, 3, f"Status    : ", curses.A_BOLD)
        self.stdscr.addstr(start_y + 6, 15, f"✨ {cmd['status']}", curses.color_pair(3))

        # XP Bar
        xp_pct = min(1.0, cmd["xp"] / cmd["xp_to_next"])
        bar_len = left_w - 18
        filled = int(bar_len * xp_pct)
        bar = "█" * filled + "░" * (bar_len - filled)
        self.stdscr.addstr(start_y + 8, 3, f"XP Progress:", curses.A_BOLD)
        self.stdscr.addstr(start_y + 9, 3, f"[{bar}] {cmd['xp']}/{cmd['xp_to_next']}", curses.color_pair(5))

        # Box 2: Telemetry Metrics
        telemetry_y = start_y + 11
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(telemetry_y, 1, "┌" + "─" * (left_w - 2) + "┐")
        self.stdscr.addstr(telemetry_y, 3, " 📊 Work Telemetry ", curses.color_pair(5) | curses.A_BOLD)
        for y in range(1, 6):
            self.stdscr.addstr(telemetry_y + y, 1, "│")
            self.stdscr.addstr(telemetry_y + y, left_w, "│")
        self.stdscr.addstr(telemetry_y + 6, 1, "└" + "─" * (left_w - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1))

        self.stdscr.addstr(telemetry_y + 2, 3, f"• Bugs Fixed      : {stats['bugs_fixed']} (Nova unlocked)")
        self.stdscr.addstr(telemetry_y + 3, 3, f"• Deploys Verified: {stats['deployments']} (Orion shield active)")
        self.stdscr.addstr(telemetry_y + 4, 3, f"• Tests Written   : {stats['tests_written']} (Vega scan online)")
        self.stdscr.addstr(telemetry_y + 5, 3, f"• Sprint Meetings : {stats['meetings_led']} (Zara synced)")

        # Right Column: Floating Motivation & Active Quest
        self.stdscr.attron(curses.color_pair(6))
        self.stdscr.addstr(start_y, right_x, "┌" + "─" * (right_w - 2) + "┐")
        self.stdscr.addstr(start_y, right_x + 3, " 🛰️ Trill Astro Buzz Floating Dispatch ", curses.color_pair(5) | curses.A_BOLD)
        for y in range(1, 6):
            self.stdscr.addstr(start_y + y, right_x, "│")
            self.stdscr.addstr(start_y + y, right_x + right_w - 1, "│")
        self.stdscr.addstr(start_y + 6, right_x, "└" + "─" * (right_w - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(6))

        # Render Quote
        self.stdscr.attron(curses.color_pair(1) | curses.A_BOLD)
        self.stdscr.addstr(start_y + 2, right_x + 3, "Buzz:")
        self.stdscr.attroff(curses.color_pair(1) | curses.A_BOLD)
        # Word wrap quote
        words = self.current_quote.split(' ')
        q_line = ""
        q_y = start_y + 3
        for w in words:
            if len(q_line) + len(w) + 1 > right_w - 8:
                self.stdscr.addstr(q_y, right_x + 3, f'"{q_line}"', curses.color_pair(3))
                q_y += 1
                q_line = w
            else:
                q_line = f"{q_line} {w}" if q_line else w
        if q_line:
            self.stdscr.addstr(q_y, right_x + 3, f'"{q_line}"', curses.color_pair(3))

        # Active Orbital Quest Panel
        quest_y = start_y + 7
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(quest_y, right_x, "┌" + "─" * (right_w - 2) + "┐")
        self.stdscr.addstr(quest_y, right_x + 3, " 🔥 Priority Orbital Quest ", curses.color_pair(4) | curses.A_BOLD)
        for y in range(1, 10):
            self.stdscr.addstr(quest_y + y, right_x, "│")
            self.stdscr.addstr(quest_y + y, right_x + right_w - 1, "│")
        self.stdscr.addstr(quest_y + 10, right_x, "└" + "─" * (right_w - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1))

        if self.state["missions"]:
            m = self.state["missions"][0]
            self.stdscr.addstr(quest_y + 2, right_x + 3, f"[{m['id']}] {m['title']}"[:right_w-6], curses.color_pair(5) | curses.A_BOLD)
            self.stdscr.addstr(quest_y + 4, right_x + 3, f"Status    : ", curses.A_BOLD)
            self.stdscr.addstr(quest_y + 4, right_x + 15, m["status"], curses.color_pair(3))
            self.stdscr.addstr(quest_y + 5, right_x + 3, f"Priority  : ", curses.A_BOLD)
            self.stdscr.addstr(quest_y + 5, right_x + 15, m["priority"])
            self.stdscr.addstr(quest_y + 6, right_x + 3, f"Navigator : ", curses.A_BOLD)
            self.stdscr.addstr(quest_y + 6, right_x + 15, m["assigned_to"], curses.color_pair(1))
            self.stdscr.addstr(quest_y + 7, right_x + 3, f"Reward    : ", curses.A_BOLD)
            self.stdscr.addstr(quest_y + 7, right_x + 15, f"+{m['xp']} XP (Anti-Gravity Boosted)", curses.color_pair(5))
            self.stdscr.addstr(quest_y + 9, right_x + 3, "[Press Enter or 'c' to initiate Mission Check-in]", curses.color_pair(8))

    def draw_crew_roster(self, start_y, height, width):
        agents = self.state["agents"]
        list_w = min(36, width // 2)
        detail_w = width - list_w - 3
        detail_x = list_w + 3

        # List Panel
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(start_y, 1, "┌" + "─" * (list_w - 2) + "┐")
        self.stdscr.addstr(start_y, 3, f" Active Crew ({len(agents)}) ", curses.color_pair(5) | curses.A_BOLD)
        for y in range(1, height - 1):
            self.stdscr.addstr(start_y + y, 1, "│")
            self.stdscr.addstr(start_y + y, list_w, "│")
        self.stdscr.addstr(start_y + height - 1, 1, "└" + "─" * (list_w - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1))

        if self.selected_row >= len(agents):
            self.selected_row = max(0, len(agents) - 1)

        for i, a in enumerate(agents):
            row_y = start_y + 1 + i * 2
            if row_y >= start_y + height - 2:
                break
            is_sel = (i == self.selected_row)
            line = f" {a['name']} "
            role_line = f"   ↳ {a['role']} [{a['rank']}] "

            if is_sel:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                self.stdscr.addstr(row_y, 2, line.ljust(list_w - 2))
                self.stdscr.addstr(row_y + 1, 2, role_line.ljust(list_w - 2))
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.addstr(row_y, 2, line.ljust(list_w - 2), curses.color_pair(5) if a['unlocked'] else curses.color_pair(6))
                self.stdscr.addstr(row_y + 1, 2, role_line.ljust(list_w - 2), curses.color_pair(6))

        # Details Panel
        sel_agent = agents[self.selected_row] if agents else None
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(start_y, detail_x, "┌" + "─" * (detail_w - 2) + "┐")
        self.stdscr.addstr(start_y, detail_x + 3, " 🪐 Agent Holographic Dossier ", curses.color_pair(5) | curses.A_BOLD)
        for y in range(1, height - 1):
            self.stdscr.addstr(start_y + y, detail_x, "│")
            self.stdscr.addstr(start_y + y, detail_x + detail_w - 1, "│")
        self.stdscr.addstr(start_y + height - 1, detail_x, "└" + "─" * (detail_w - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1))

        if sel_agent:
            d_y = start_y + 2
            self.stdscr.addstr(d_y, detail_x + 3, f"{sel_agent['name']} ({sel_agent['role']})", curses.color_pair(1) | curses.A_BOLD)
            self.stdscr.addstr(d_y + 1, detail_x + 3, f"Title: {sel_agent['title']} | Rank: {sel_agent['rank']} {sel_agent['stars']}", curses.color_pair(5))

            d_y += 3
            self.stdscr.addstr(d_y, detail_x + 3, f"Evolution Stage : ", curses.A_BOLD)
            self.stdscr.addstr(d_y, detail_x + 22, sel_agent['stage'], curses.color_pair(3) | curses.A_BOLD)

            d_y += 1
            # Loyalty meter
            loyalty_bar = "█" * (sel_agent['loyalty'] // 10) + "░" * (10 - (sel_agent['loyalty'] // 10))
            self.stdscr.addstr(d_y, detail_x + 3, f"Loyalty Meter   : [{loyalty_bar}] {sel_agent['loyalty']}%", curses.color_pair(5))

            d_y += 1
            # Energy meter
            energy_bar = "█" * (sel_agent['energy'] // 10) + "░" * (10 - (sel_agent['energy'] // 10))
            self.stdscr.addstr(d_y, detail_x + 3, f"Energy Reserves : [{energy_bar}] {sel_agent['energy']}%", curses.color_pair(3))

            d_y += 2
            self.stdscr.addstr(d_y, detail_x + 3, "Cosmic Superpower:", curses.A_BOLD)
            self.stdscr.addstr(d_y + 1, detail_x + 5, f"⚡ {sel_agent['power']}", curses.color_pair(1))

            d_y += 3
            self.stdscr.addstr(d_y, detail_x + 3, "Agent Catchphrase:", curses.A_BOLD)
            self.stdscr.addstr(d_y + 1, detail_x + 5, f'"{sel_agent["catchphrase"]}"', curses.color_pair(3))

    def draw_missions(self, start_y, height, width):
        missions = self.state["missions"]
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(start_y, 1, "┌" + "─" * (width - 2) + "┐")
        self.stdscr.addstr(start_y, 3, f" 📋 Active Missions in Orbit ({len(missions)}) ", curses.color_pair(5) | curses.A_BOLD)
        for y in range(1, height - 1):
            self.stdscr.addstr(start_y + y, 1, "│")
            self.stdscr.addstr(start_y + y, width, "│")
        self.stdscr.addstr(start_y + height - 1, 1, "└" + "─" * (width - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1))

        if self.selected_row >= len(missions):
            self.selected_row = max(0, len(missions) - 1)

        for i, m in enumerate(missions):
            m_y = start_y + 2 + i * 3
            if m_y >= start_y + height - 2:
                break
            is_sel = (i == self.selected_row)
            line1 = f" {m['id']:<10} {m['title']} "
            line2 = f"   Priority: {m['priority']:<16} Assigned: {m['assigned_to']:<18} Reward: +{m['xp']} XP "

            if is_sel:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                self.stdscr.addstr(m_y, 2, line1[:width-4].ljust(width-4))
                self.stdscr.addstr(m_y + 1, 2, line2[:width-4].ljust(width-4))
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.addstr(m_y, 2, line1[:width-4], curses.color_pair(5) | curses.A_BOLD)
                self.stdscr.addstr(m_y + 1, 2, line2[:width-4], curses.color_pair(6))

    def draw_cargo(self, start_y, height, width):
        inventory = self.state["inventory"]
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(start_y, 1, "┌" + "─" * (width - 2) + "┐")
        self.stdscr.addstr(start_y, 3, f" 💎 Cargo Bay & Loot Inventory ({len(inventory)} items) ", curses.color_pair(5) | curses.A_BOLD)
        for y in range(1, height - 1):
            self.stdscr.addstr(start_y + y, 1, "│")
            self.stdscr.addstr(start_y + y, width, "│")
        self.stdscr.addstr(start_y + height - 1, 1, "└" + "─" * (width - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1))

        if self.selected_row >= len(inventory):
            self.selected_row = max(0, len(inventory) - 1)

        for i, item in enumerate(inventory):
            c_y = start_y + 2 + i * 3
            if c_y >= start_y + height - 2:
                break
            is_sel = (i == self.selected_row)
            line1 = f" 📦 {item['name']} (x{item['count']}) "
            line2 = f"    Effect: {item['desc']} "

            if is_sel:
                self.stdscr.attron(curses.color_pair(2) | curses.A_BOLD)
                self.stdscr.addstr(c_y, 2, line1[:width-4].ljust(width-4))
                self.stdscr.addstr(c_y + 1, 2, line2[:width-4].ljust(width-4))
                self.stdscr.attroff(curses.color_pair(2) | curses.A_BOLD)
            else:
                self.stdscr.addstr(c_y, 2, line1[:width-4], curses.color_pair(5) | curses.A_BOLD)
                self.stdscr.addstr(c_y + 1, 2, line2[:width-4], curses.color_pair(3))

    def draw_dispatches(self, start_y, height, width):
        dispatches = self.state.get("dispatches", [])
        self.stdscr.attron(curses.color_pair(1))
        self.stdscr.addstr(start_y, 1, "┌" + "─" * (width - 2) + "┐")
        self.stdscr.addstr(start_y, 3, " 📡 Trill Astro Buzz Transmission Log ", curses.color_pair(5) | curses.A_BOLD)
        for y in range(1, height - 1):
            self.stdscr.addstr(start_y + y, 1, "│")
            self.stdscr.addstr(start_y + y, width, "│")
        self.stdscr.addstr(start_y + height - 1, 1, "└" + "─" * (width - 2) + "┘")
        self.stdscr.attroff(curses.color_pair(1))

        for i, d in enumerate(dispatches):
            d_y = start_y + 2 + i * 4
            if d_y >= start_y + height - 3:
                break
            self.stdscr.addstr(d_y, 3, f"🚀 [{d.get('date', '')}] {d.get('headline', '')}", curses.color_pair(5) | curses.A_BOLD)
            self.stdscr.addstr(d_y + 1, 5, d.get('summary', '')[:width-10], curses.color_pair(3))
            self.stdscr.addstr(d_y + 2, 5, f"Source: {d.get('source', '')}"[:width-10], curses.color_pair(1))

    def show_checkin_modal(self):
        curses.curs_set(1)
        max_y, max_x = self.stdscr.getmaxyx()
        h, w = 14, min(70, max_x - 6)
        start_y = (max_y - h) // 2
        start_x = (max_x - w) // 2

        win = curses.newwin(h, w, start_y, start_x)
        win.keypad(True)
        task_input = ""

        while True:
            win.clear()
            win.box()
            win.addstr(0, 3, " 🛸 Mission Check-in & XP Boost ", curses.color_pair(5) | curses.A_BOLD)
            win.addstr(2, 3, "Report completed engineering progress:")
            win.addstr(4, 3, "[" + " " * (w - 8) + "]")
            win.addstr(4, 4, task_input[:w-10])

            win.addstr(6, 3, "Rewards Calculator:")
            win.addstr(7, 5, "• Base Mission Reward : +75 XP", curses.color_pair(3))
            win.addstr(8, 5, "• Speed Velocity Bonus: +20 XP", curses.color_pair(5))
            win.addstr(9, 5, "• Zero-G Floating Buff: +15 XP", curses.color_pair(1))

            win.addstr(h - 2, 2, " [Enter] Claim 110 XP  [Esc] Cancel ", curses.color_pair(7))
            win.refresh()

            curses.setsyx(start_y + 4, start_x + 4 + len(task_input))
            curses.doupdate()

            ch = win.getch()
            if ch == 27:
                curses.curs_set(0)
                return
            elif ch in [10, 13]:
                # Grant XP
                self.state["commander"]["xp"] += 110
                if self.state["commander"]["xp"] >= self.state["commander"]["xp_to_next"]:
                    self.state["commander"]["level"] += 1
                    self.state["commander"]["xp_to_next"] += 300
                    self.status_banner = f"⭐ LEVEL UP! Commander is now Level {self.state['commander']['level']}!"
                else:
                    self.status_banner = "✅ Mission Complete! +110 XP claimed. Buzz is floating with pride."
                save_game_state(self.state)
                curses.curs_set(0)
                return
            elif ch in [curses.KEY_BACKSPACE, 127, 8]:
                if task_input:
                    task_input = task_input[:-1]
            elif 32 <= ch <= 126:
                if len(task_input) < (w - 10):
                    task_input += chr(ch)

    def run(self):
        while True:
            self.stdscr.erase()
            max_y, max_x = self.stdscr.getmaxyx()

            if max_y < 20 or max_x < 76:
                self.stdscr.addstr(0, 0, f"Terminal size too small ({max_x}x{max_y}). Need at least 76x20.")
                self.stdscr.refresh()
                ch = self.stdscr.getch()
                if ch in [ord('q'), ord('Q')]:
                    break
                continue

            self.draw_header(max_y, max_x)

            content_y = 3
            content_h = max_y - content_y - 3
            content_w = max_x - 2

            if self.active_tab == 0:
                self.draw_bridge_hud(content_y, content_h, content_w)
            elif self.active_tab == 1:
                self.draw_crew_roster(content_y, content_h, content_w)
            elif self.active_tab == 2:
                self.draw_missions(content_y, content_h, content_w)
            elif self.active_tab == 3:
                self.draw_cargo(content_y, content_h, content_w)
            elif self.active_tab == 4:
                self.draw_dispatches(content_y, content_h, content_w)

            self.draw_footer(max_y, max_x)
            self.stdscr.refresh()

            try:
                ch = self.stdscr.getch()
            except KeyboardInterrupt:
                break

            if ch in [ord('q'), ord('Q')]:
                break
            elif ord('1') <= ch <= ord('5'):
                self.active_tab = ch - ord('1')
                self.selected_row = 0
            elif ch in [curses.KEY_UP, ord('k')]:
                if self.selected_row > 0:
                    self.selected_row -= 1
            elif ch in [curses.KEY_DOWN, ord('j')]:
                self.selected_row += 1
            elif ch == ord('m'):
                self.current_quote = random.choice(BUZZ_QUOTES)
                self.status_banner = "💬 New floating motivation dispatched from Trill Astro Buzz!"
            elif ch in [10, 13, ord('c')]:
                self.show_checkin_modal()

def main():
    curses.wrapper(lambda stdscr: USSHustleTUI(stdscr).run())

if __name__ == "__main__":
    main()
