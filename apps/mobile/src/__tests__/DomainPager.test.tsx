import { render, screen } from '@testing-library/react';
import { DomainPager, DOMAIN_HEIGHT } from '../features/today/DomainPager';

it('keeps domain sections close enough for scanning', () => {
  expect(DOMAIN_HEIGHT).toBeLessThanOrEqual(520);

  render(
    <DomainPager
      domains={[
        {
          domainId: 'technology',
          domainName: '科技与互联网',
          items: [
            {
              id: 'article-1',
              title: '测试标题',
              summary: '测试概览',
              source: '测试来源',
              publishedAt: '2026-05-26T08:00:00+08:00',
              isRead: false
            }
          ]
        }
      ]}
      themeMode="light"
      onDomainChange={() => undefined}
      onItemRead={() => undefined}
      onItemPress={() => undefined}
    />
  );

  expect(screen.getByText('科技与互联网')).toBeTruthy();
});

it('shows a generating card when a domain has no articles', () => {
  render(
    <DomainPager
      domains={[
        {
          domainId: 'finance',
          domainName: '财经与宏观',
          items: []
        }
      ]}
      themeMode="light"
      onDomainChange={() => undefined}
      onItemRead={() => undefined}
      onItemPress={() => undefined}
    />
  );

  expect(screen.getByText('该领域今日正在生成')).toBeTruthy();
});
