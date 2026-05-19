import { describe, expect, it, vi } from 'vitest';
import { createAppStore } from '../store/app-store';

describe('app store', () => {
  it('starts with onboarding visible', () => {
    const store = createAppStore();

    expect(store.getState().hasCompletedOnboarding).toBe(false);
  });

  it('persists selected domains when completing onboarding', async () => {
    const storage = {
      loadSelectedDomains: vi.fn().mockResolvedValue([]),
      saveSelectedDomains: vi.fn().mockResolvedValue(undefined)
    };
    const store = createAppStore(storage);

    store.getState().toggleDomainSelection('technology');
    await store.getState().completeOnboarding();

    expect(storage.saveSelectedDomains).toHaveBeenCalledWith(['technology']);
    expect(store.getState().hasCompletedOnboarding).toBe(true);
  });

  it('hydrates selected domains from storage', async () => {
    const storage = {
      loadSelectedDomains: vi.fn().mockResolvedValue(['technology', 'ai']),
      saveSelectedDomains: vi.fn().mockResolvedValue(undefined)
    };
    const store = createAppStore(storage);

    await store.getState().hydrate();

    expect(store.getState().selectedDomains).toEqual(['technology', 'ai']);
    expect(store.getState().hasCompletedOnboarding).toBe(true);
  });
});
