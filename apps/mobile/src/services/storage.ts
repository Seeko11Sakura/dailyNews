import AsyncStorage from '@react-native-async-storage/async-storage';

const SELECTED_DOMAINS_KEY = 'selected_domains';

export async function saveSelectedDomains(ids: string[]) {
  await AsyncStorage.setItem(SELECTED_DOMAINS_KEY, JSON.stringify(ids));
}

export async function loadSelectedDomains(): Promise<string[]> {
  const raw = await AsyncStorage.getItem(SELECTED_DOMAINS_KEY);
  if (!raw) {
    return [];
  }

  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [];
}
