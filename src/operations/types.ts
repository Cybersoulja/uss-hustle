export type MissionCategory = 'engineering' | 'content' | 'operations';
export type CrewCode = 'nova' | 'orion' | 'vega' | 'zara' | 'atlas' | 'trill';
export type RuntimeKind = 'codex' | 'jules' | 'craft' | 'zapier' | 'local' | 'manual';
export type MissionState = 'DRAFT' | 'PROPOSED' | 'APPROVED' | 'LAUNCHED' | 'COMPLETED' | 'BLOCKED' | 'FAILED' | 'CANCELLED';

export interface MissionProposal {
  category: MissionCategory;
  advisor: CrewCode;
  runtime: RuntimeKind;
  rationale: string;
  deliverable: string;
  requiresJiraIssue: boolean;
}

export interface RuntimeLaunchRequest {
  missionId: string;
  idempotencyKey: string;
  runtime: RuntimeKind;
  title: string;
  safeContext: string;
  expectedDeliverable: string;
  callbackUrl: string;
}
