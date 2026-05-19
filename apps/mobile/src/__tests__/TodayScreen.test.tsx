import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { TodayScreen } from '../features/today/TodayScreen';
import { createAppStore } from '../store/app-store';

const { fetchTodayDigest, fetchItemDetail } = vi.hoisted(() => ({
  fetchTodayDigest: vi.fn(),
  fetchItemDetail: vi.fn()
}));

vi.mock('../services/api', () => ({
  fetchTodayDigest,
  fetchItemDetail
}));

it('loads digest, opens reader modal and marks item as read', async () => {
  fetchTodayDigest.mockResolvedValue({
    groups: [
      {
        domain_id: 'technology',
        items: [
          {
            id: 'technology-1',
            domain_id: 'technology',
            title: 'technology 今日第 1 条重要资讯',
            summary: '结论卡摘要',
            source: 'Mock Source',
            published_at: '2026-05-19T08:00:00+08:00',
            is_read: false
          }
        ]
      }
    ]
  });
  fetchItemDetail.mockResolvedValue({
    id: 'technology-1',
    title: 'Mock 详情',
    summary: '结论卡回顾',
    content: '正文内容联调用。',
    source_url: 'https://example.com/article',
    fetch_status: 'success'
  });

  const store = createAppStore();
  store.setState({
    hasCompletedOnboarding: true,
    selectedDomains: ['technology']
  });

  render(<TodayScreen store={store} />);

  await screen.findByText('technology 今日第 1 条重要资讯');

  fireEvent.click(screen.getByText('阅读全文'));

  await waitFor(() => {
    expect(screen.getByText('Mock 详情')).toBeTruthy();
  });

  expect(fetchTodayDigest).toHaveBeenCalledWith(['technology']);
  expect(fetchItemDetail).toHaveBeenCalledWith('technology-1');
  expect(store.getState().readCount).toBe(1);
});
