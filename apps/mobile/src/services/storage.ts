import AsyncStorage from '@react-native-async-storage/async-storage';

const SELECTED_DOMAINS_KEY = 'selected_domains';
const THEME_MODE_KEY = 'theme_mode';

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

export async function clearCache() {
  await AsyncStorage.removeItem(SELECTED_DOMAINS_KEY);
  await AsyncStorage.removeItem(THEME_MODE_KEY);
}

export async function saveThemeMode(mode: 'light' | 'dark') {
  await AsyncStorage.setItem(THEME_MODE_KEY, mode);
}

export async function loadThemeMode(): Promise<'light' | 'dark'> {
  const raw = await AsyncStorage.getItem(THEME_MODE_KEY);
  return raw === 'dark' ? 'dark' : 'light';
}
