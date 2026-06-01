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
  expect(summary.style.WebkitLineClamp).toBe('3');
});

it('keeps the title compact so the read button remains visible', () => {
  const longTitle = '这是一个很长很长的文章标题，用来模拟真实新闻标题在手机卡片里占用多行的情况。'.repeat(3);

  render(
    <ArticleCard
      title={longTitle}
      summary="短概览"
      source="测试来源"
      publishedAt="2026-05-26T08:00:00+08:00"
      fillHeight
    />
  );

  const title = screen.getByText(longTitle) as HTMLElement;
  expect(title.style.WebkitLineClamp).toBe('2');
  expect(screen.getByText('阅读全文')).toBeTruthy();
});

it('renders cover image when provided', () => {
  render(
    <ArticleCard
      title="测试标题"
      summary="短概览"
      source="测试来源"
      publishedAt="2026-05-26T08:00:00+08:00"
      coverImageUrl="https://cdn.example.com/cover.jpg"
      fillHeight
    />
  );

  expect(screen.getByLabelText('文章封面图')).toBeTruthy();
});

it('renders a default cover when article image is missing', () => {
  render(
    <ArticleCard
      title="测试标题"
      summary="短概览"
      source="测试来源"
      publishedAt="2026-05-26T08:00:00+08:00"
      domainName="人工智能"
      fillHeight
    />
  );

  expect(screen.getByLabelText('默认文章封面')).toBeTruthy();
  expect(screen.getByText('人工智能')).toBeTruthy();
});
