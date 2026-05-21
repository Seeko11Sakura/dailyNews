import { useStore } from 'zustand';
import { createStore } from 'zustand/vanilla';
import type { StoreApi } from 'zustand/vanilla';
import type { DomainId } from '@dailynews/shared';
import {
  clearCache as clearPersistedCache,
  loadSelectedDomains,
  loadThemeMode,
  saveSelectedDomains,
  saveThemeMode
} from '../services/storage';

export type DigestListItem = {
  id: string;
  domainId: DomainId;
  title: string;
  summary: string;
  source: string;
  publishedAt: string;
  isRead: boolean;
};

export type DigestGroup = {
  domainId: DomainId;
  items: DigestListItem[];
};

export type AppState = {
  hasCompletedOnboarding: boolean;
  selectedDomains: DomainId[];
  digestGroups: DigestGroup[];
  readCount: number;
  favoriteIds: string[];
  themeMode: 'light' | 'dark';
  toggleDomainSelection: (id: DomainId) => void;
  setDigest: (groups: DigestGroup[]) => void;
  markItemRead: (itemId: string) => void;
  toggleFavorite: (itemId: string) => void;
  toggleThemeMode: () => Promise<void>;
  completeOnboarding: () => Promise<void>;
  clearCache: () => Promise<void>;
  hydrate: () => Promise<void>;
};

export type AppStorage = {
  loadSelectedDomains: () => Promise<string[]>;
  saveSelectedDomains: (ids: string[]) => Promise<void>;
  loadThemeMode: () => Promise<'light' | 'dark'>;
  saveThemeMode: (mode: 'light' | 'dark') => Promise<void>;
  clearCache: () => Promise<void>;
};

export type AppStore = StoreApi<AppState>;

const MAX_ONBOARDING_DOMAINS = 5;

function toggleSelection(current: DomainId[], id: DomainId) {
  if (current.includes(id)) {
    return current.filter((value) => value !== id);
  }

  if (current.length >= MAX_ONBOARDING_DOMAINS) {
    return current;
  }

  return [...current, id];
}

function countReadItems(groups: DigestGroup[]) {
  return groups.reduce((total, group) => {
    return (
      total + group.items.filter((item) => item.isRead).length
    );
  }, 0);
}

export function createAppStore(
  storage: AppStorage = {
    loadSelectedDomains,
    saveSelectedDomains,
    loadThemeMode,
    saveThemeMode,
    clearCache: clearPersistedCache
  }
) {
  return createStore<AppState>()((set, get) => ({
    hasCompletedOnboarding: false,
    selectedDomains: [],
    digestGroups: [],
    readCount: 0,
    favoriteIds: [],
    themeMode: 'light',
    toggleDomainSelection: (id) => {
      set((state) => ({
        selectedDomains: toggleSelection(state.selectedDomains, id)
      }));
    },
    setDigest: (groups) => {
      set({
        digestGroups: groups,
        readCount: countReadItems(groups)
      });
    },
    markItemRead: (itemId) => {
      set((state) => {
        const digestGroups = state.digestGroups.map((group) => ({
          ...group,
          items: group.items.map((item) =>
            item.id === itemId && !item.isRead
              ? { ...item, isRead: true }
              : item
          )
        }));

        return {
          digestGroups,
          readCount: countReadItems(digestGroups)
        };
      });
    },
    toggleFavorite: (itemId) => {
      set((state) => ({
        favoriteIds: state.favoriteIds.includes(itemId)
          ? state.favoriteIds.filter((id) => id !== itemId)
          : [...state.favoriteIds, itemId]
      }));
    },
    toggleThemeMode: async () => {
      const nextMode = get().themeMode === 'dark' ? 'light' : 'dark';
      await storage.saveThemeMode(nextMode);
      set((state) => ({
        themeMode: state.themeMode === 'dark' ? 'light' : 'dark'
      }));
    },
    completeOnboarding: async () => {
      const { selectedDomains } = get();
      if (selectedDomains.length === 0) {
        return;
      }

      await storage.saveSelectedDomains(selectedDomains);
      set({
        hasCompletedOnboarding: true
      });
    },
    clearCache: async () => {
      await storage.clearCache();
      set({
        hasCompletedOnboarding: false,
        selectedDomains: [],
        digestGroups: [],
        readCount: 0,
        favoriteIds: [],
        themeMode: 'light'
      });
    },
    hydrate: async () => {
      const [selectedDomains, themeMode] = await Promise.all([
        storage.loadSelectedDomains(),
        storage.loadThemeMode()
      ]);
      set({
        selectedDomains: selectedDomains as DomainId[],
        themeMode,
        hasCompletedOnboarding: selectedDomains.length > 0
      });
    }
  }));
}

export const appStore = createAppStore();

export function useAppStore<T>(
  selector: (state: AppState) => T,
  store: AppStore = appStore
) {
  return useStore(store, selector);
}
