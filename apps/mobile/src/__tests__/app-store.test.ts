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

  it('marks an item as read and updates progress', () => {
    const store = createAppStore();

    store.getState().setDigest([
      {
        domainId: 'technology',
        items: [
          {
            id: 'technology-1',
            domainId: 'technology',
            title: '科技要闻',
            summary: '摘要',
            source: 'Mock Source',
            publishedAt: '2026-05-19T08:00:00+08:00',
            isRead: false
          }
        ]
      }
    ]);

    store.getState().markItemRead('technology-1');

    expect(store.getState().readCount).toBe(1);
    expect(store.getState().digestGroups[0]?.items[0]?.isRead).toBe(true);
  });


  it('toggles favorites by item id', () => {
    const store = createAppStore();

    store.getState().toggleFavorite('technology-1');
    expect(store.getState().favoriteIds).toEqual(['technology-1']);

    store.getState().toggleFavorite('technology-1');
    expect(store.getState().favoriteIds).toEqual([]);
  });

  it('clears persisted data and resets in-memory state', async () => {
    const storage = {
      loadSelectedDomains: vi.fn().mockResolvedValue([]),
      saveSelectedDomains: vi.fn().mockResolvedValue(undefined),
      clearCache: vi.fn().mockResolvedValue(undefined)
    };
    const store = createAppStore(storage);

    store.getState().toggleDomainSelection('technology');
    store.getState().toggleFavorite('technology-1');
    await store.getState().completeOnboarding();
    await store.getState().clearCache();

    expect(storage.clearCache).toHaveBeenCalledTimes(1);
    expect(store.getState().selectedDomains).toEqual([]);
    expect(store.getState().favoriteIds).toEqual([]);
    expect(store.getState().themeMode).toBe('light');
    expect(store.getState().hasCompletedOnboarding).toBe(false);
  });
});
