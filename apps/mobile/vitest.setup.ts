import { vi } from 'vitest';

vi.mock('@react-native-async-storage/async-storage', () => {
  const storage = new Map<string, string>();

  return {
    default: {
      async getItem(key: string) {
        return storage.has(key) ? storage.get(key)! : null;
      },
      async setItem(key: string, value: string) {
        storage.set(key, value);
      },
      async removeItem(key: string) {
        storage.delete(key);
      },
      async clear() {
        storage.clear();
      }
    }
  };
});
