import { describe, expect, it } from 'vitest';
import { classifyMission } from '../../src/operations/classifier';

describe('classifyMission', () => {
  it('routes a GitHub issue request to Jules and Nova', () => {
    expect(classifyMission('Triage GitHub issue #42 and prepare a PR')).toMatchObject({
      category: 'engineering', advisor: 'nova', runtime: 'jules'
    });
  });
});
