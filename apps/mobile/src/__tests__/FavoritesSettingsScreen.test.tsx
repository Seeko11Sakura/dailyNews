import { fireEvent, render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { FavoritesScreen } from '../features/favorites/FavoritesScreen';
import { SettingsScreen } from '../features/settings/SettingsScreen';
import { createAppStore } from '../store/app-store';

it('renders favorites skeleton with search and count', () => {
  const store = createAppStore();
  store.getState().toggleFavorite('technology-1');

  render(<FavoritesScreen store={store} />);

  expect(screen.getByPlaceholderText('搜索标题或来源')).toBeTruthy();
  expect(screen.getByText('收藏列表')).toBeTruthy();
  expect(screen.getByText('已收藏 1 条')).toBeTruthy();
});

it('renders settings skeleton and clears cache from button press', async () => {
  const storage = {
    loadSelectedDomains: vi.fn().mockResolvedValue([]),
    loadThemeMode: vi.fn().mockResolvedValue('light'),
    saveSelectedDomains: vi.fn().mockResolvedValue(undefined),
    saveThemeMode: vi.fn().mockResolvedValue(undefined),
    clearCache: vi.fn().mockResolvedValue(undefined)
  };
  const store = createAppStore(storage);
  const clearCache = vi.spyOn(store.getState(), 'clearCache');

  render(<SettingsScreen store={store} />);

  expect(screen.getByText('主题模式')).toBeTruthy();
  fireEvent.click(screen.getByText('清除缓存'));

  expect(clearCache).toHaveBeenCalledTimes(1);
});
