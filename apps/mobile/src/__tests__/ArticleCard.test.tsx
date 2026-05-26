import { render, screen } from '@testing-library/react';
import { ArticleCard } from '../features/today/ArticleCard';

it('limits overview lines in full height cards', () => {
  const longSummary =
    '这是一段很长的概览内容，用来模拟抓取到整篇文章内容时的展示效果。'.repeat(20);

  render(
    <ArticleCard
      title="测试标题"
      summary={longSummary}
      source="测试来源"
      publishedAt="2026-05-26T08:00:00+08:00"
      fillHeight
    />
  );

  const summary = screen.getByText(longSummary) as HTMLElement;
  expect(summary.style.WebkitLineClamp).toBe('4');
});
