// =============================================================================
// Agent Genesis Engine: Dynamic Character Unlock Logic
// =============================================================================

export interface PlayerStats {
  bugs_fixed: number;
  deployments_successful: number;
  tests_written: number;
  meetings_led: number;
  weekly_deploys: number;
}

export interface UnlockResult {
  unlocked: boolean;
  agentCodeName?: string;
  agentName?: string;
  dialogueNodeId?: string;
  announcement?: string;
}

export function evaluateAgentGenesis(stats: PlayerStats, currentUnlocked: string[]): UnlockResult[] {
  const results: UnlockResult[] = [];

  // 1. Nova Starwind (5 Bugs Fixed)
  if (stats.bugs_fixed >= 5 && !currentUnlocked.includes('nova')) {
    results.push({
      unlocked: true,
      agentCodeName: 'nova',
      agentName: 'Nova Starwind',
      dialogueNodeId: 'NODE_003',
      announcement: '🌠 NOVA STARWIND HAS EMERGED FROM YOUR CODE SYNTAX!'
    });
  }

  // 2. Orion Codex (3 Successful Deploys)
  if (stats.deployments_successful >= 3 && !currentUnlocked.includes('orion')) {
    results.push({
      unlocked: true,
      agentCodeName: 'orion',
      agentName: 'Orion Codex',
      dialogueNodeId: 'NODE_004',
      announcement: '🔭 ORION CODEX HAS ACTIVATED THE PLASMA SHIELD!'
    });
  }

  // 3. Vega Quantum (10 Tests Written)
  if (stats.tests_written >= 10 && !currentUnlocked.includes('vega')) {
    results.push({
      unlocked: true,
      agentCodeName: 'vega',
      agentName: 'Vega Quantum',
      dialogueNodeId: 'NODE_005',
      announcement: '🔬 VEGA QUANTUM HAS CALIBRATED THE TACHYON SCAN!'
    });
  }

  // 4. Zara Nebula (2 Sprint / Team Meetings)
  if (stats.meetings_led >= 2 && !currentUnlocked.includes('zara')) {
    results.push({
      unlocked: true,
      agentCodeName: 'zara',
      agentName: 'Zara Nebula',
      dialogueNodeId: 'NODE_006',
      announcement: '🌌 ZARA NEBULA HAS ENGAGED QUANTUM SYNC!'
    });
  }

  // 5. Atlas Comet (3 Deploys in One Week)
  if (stats.weekly_deploys >= 3 && !currentUnlocked.includes('atlas')) {
    results.push({
      unlocked: true,
      agentCodeName: 'atlas',
      agentName: 'Atlas Comet',
      dialogueNodeId: 'NODE_007',
      announcement: '☄️ ATLAS COMET HAS INITIATED ZERO DOWNTIME WARP!'
    });
  }

  return results;
}
