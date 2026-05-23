import AsyncStorage from '@react-native-async-storage/async-storage';

const SELECTED_DOMAINS_KEY = 'selected_domains';
const THEME_MODE_KEY = 'theme_mode';
const DISMISSED_DOMAINS_KEY = 'dismissed_domains';
const FAVORITE_IDS_KEY = 'favorite_ids';

function readItemKey(date: string) {
  return `read_items_${date}`;
}

function digestCacheKey(date: string) {
  return `cached_digest_${date}`;
}

function articleCacheKey(itemId: string) {
  return `cached_article_${itemId}`;
}

// --- Selected Domains ---

export async function saveSelectedDomains(ids: string[]) {
  await AsyncStorage.setItem(SELECTED_DOMAINS_KEY, JSON.stringify(ids));
}

export async function loadSelectedDomains(): Promise<string[]> {
  const raw = await AsyncStorage.getItem(SELECTED_DOMAINS_KEY);
  if (!raw) return [];
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [];
}

// --- Theme ---

export async function saveThemeMode(mode: 'light' | 'dark') {
  await AsyncStorage.setItem(THEME_MODE_KEY, mode);
}

export async function loadThemeMode(): Promise<'light' | 'dark'> {
  const raw = await AsyncStorage.getItem(THEME_MODE_KEY);
  return raw === 'dark' ? 'dark' : 'light';
}

// --- Dismissed Domains ---

export async function saveDismissedDomains(ids: string[]) {
  await AsyncStorage.setItem(DISMISSED_DOMAINS_KEY, JSON.stringify(ids));
}

export async function loadDismissedDomains(): Promise<string[]> {
  const raw = await AsyncStorage.getItem(DISMISSED_DOMAINS_KEY);
  if (!raw) return [];
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [];
}

// --- Favorites ---

export async function saveFavoriteIds(ids: string[]) {
  await AsyncStorage.setItem(FAVORITE_IDS_KEY, JSON.stringify(ids));
}

export async function loadFavoriteIds(): Promise<string[]> {
  const raw = await AsyncStorage.getItem(FAVORITE_IDS_KEY);
  if (!raw) return [];
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [];
}

// --- Read Items (per day) ---

export async function markAsRead(itemId: string, date: string) {
  const key = readItemKey(date);
  const existing = await getReadItems(date);
  if (!existing.includes(itemId)) {
    existing.push(itemId);
    await AsyncStorage.setItem(key, JSON.stringify(existing));
  }
}

export async function getReadItems(date: string): Promise<string[]> {
  const raw = await AsyncStorage.getItem(readItemKey(date));
  if (!raw) return [];
  const parsed = JSON.parse(raw);
  return Array.isArray(parsed) ? parsed : [];
}

// --- Digest Cache ---

export async function cacheDigest(date: string, data: unknown) {
  await AsyncStorage.setItem(digestCacheKey(date), JSON.stringify(data));
}

export async function getCachedDigest(date: string): Promise<unknown | null> {
  const raw = await AsyncStorage.getItem(digestCacheKey(date));
  return raw ? JSON.parse(raw) : null;
}

// --- Article Cache ---

export async function cacheArticle(itemId: string, data: unknown) {
  await AsyncStorage.setItem(articleCacheKey(itemId), JSON.stringify(data));
}

export async function getCachedArticle(itemId: string): Promise<unknown | null> {
  const raw = await AsyncStorage.getItem(articleCacheKey(itemId));
  return raw ? JSON.parse(raw) : null;
}

// --- Clear All ---

export async function clearCache() {
  const keys = await AsyncStorage.getAllKeys();
  await AsyncStorage.multiRemove(keys);
}
