import { describe, expect, it } from 'vitest';
import { domains, edgeMap } from '../index';

describe('shared domain contracts', () => {
  it('exposes 12 launch domains', () => {
    expect(domains).toHaveLength(12);
  });

  it('contains adjacent domains for AI', () => {
    expect(edgeMap.ai).toContain('education');
    expect(edgeMap.ai).toContain('technology');
  });
});
