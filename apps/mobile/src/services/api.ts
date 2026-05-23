type ApiDigestItem = {
  id: string;
  domain_id: string;
  title: string;
  summary: string;
  source: string;
  published_at: string;
  is_read: boolean;
};

type ApiDigestGroup = {
  domain_id: string;
  items: ApiDigestItem[];
};

type ApiDigestResponse = {
  groups: ApiDigestGroup[];
};

export type ArticleDetail = {
  id: string;
  title: string;
  summary: string;
  content: string;
  source_url: string;
  fetch_status: string;
};

export const API_BASE_URL = 'http://127.0.0.1:8000';

export async function fetchTodayDigest(
  selectedDomains: string[]
): Promise<ApiDigestResponse> {
  const today = new Date().toISOString().split('T')[0];
  const response = await fetch(`${API_BASE_URL}/digest/today`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_domains: selectedDomains,
      sort_preference: 'freshness',
      date: today
    })
  });

  if (!response.ok) {
    throw new Error('获取今日简报失败');
  }

  return response.json();
}

export async function fetchItemDetail(itemId: string): Promise<ArticleDetail> {
  const response = await fetch(`${API_BASE_URL}/items/${itemId}`);

  if (!response.ok) {
    throw new Error('获取文章详情失败');
  }

  return response.json();
}

export type ExploreCard = {
  domain_id: string;
  domain_name: string;
  reason: string;
  preview_titles: string[];
};

type ExploreResponse = {
  cards: ExploreCard[];
};

export async function fetchExploreCards(
  selectedDomains: string[],
  dismissedDomains: string[] = [],
  seenDomainIds: string[] = []
): Promise<ExploreResponse> {
  const today = new Date().toISOString().split('T')[0];
  const response = await fetch(`${API_BASE_URL}/explore/draw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_domains: selectedDomains,
      dismissed_domains: dismissedDomains,
      seen_domain_ids: seenDomainIds,
      date: today
    })
  });

  if (!response.ok) {
    throw new Error('获取探索卡片失败');
  }

  return response.json();
}
