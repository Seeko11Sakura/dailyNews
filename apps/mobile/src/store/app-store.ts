import { useStore } from 'zustand';
import { createStore } from 'zustand/vanilla';
import type { StoreApi } from 'zustand/vanilla';
import type { DomainId } from '@dailynews/shared';
import { loadSelectedDomains, saveSelectedDomains } from '../services/storage';

export type AppState = {
  hasCompletedOnboarding: boolean;
  selectedDomains: DomainId[];
  toggleDomainSelection: (id: DomainId) => void;
  completeOnboarding: () => Promise<void>;
  hydrate: () => Promise<void>;
};

export type AppStorage = {
  loadSelectedDomains: () => Promise<string[]>;
  saveSelectedDomains: (ids: string[]) => Promise<void>;
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

export function createAppStore(
  storage: AppStorage = {
    loadSelectedDomains,
    saveSelectedDomains
  }
) {
  return createStore<AppState>()((set, get) => ({
    hasCompletedOnboarding: false,
    selectedDomains: [],
    toggleDomainSelection: (id) => {
      set((state) => ({
        selectedDomains: toggleSelection(state.selectedDomains, id)
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
    hydrate: async () => {
      const selectedDomains = (await storage.loadSelectedDomains()) as DomainId[];
      set({
        selectedDomains,
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
