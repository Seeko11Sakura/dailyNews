import { fireEvent, render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { OnboardingScreen } from '../features/onboarding/OnboardingScreen';
import { createAppStore } from '../store/app-store';

it('enables continue after selecting at least one domain', () => {
  const storage = {
    loadSelectedDomains: vi.fn().mockResolvedValue([]),
    loadThemeMode: vi.fn().mockResolvedValue('light'),
    saveSelectedDomains: vi.fn().mockResolvedValue(undefined),
    saveThemeMode: vi.fn().mockResolvedValue(undefined),
    clearCache: vi.fn().mockResolvedValue(undefined)
  };
  const store = createAppStore(storage);

  render(<OnboardingScreen store={store} />);

  expect(screen.queryByText(/进入简报/)).toBeNull();

  fireEvent.click(screen.getByLabelText('选择科技与互联网'));

  expect(screen.getByText('进入简报 (1/5)')).toBeTruthy();
});
