# Task5 Today Digest Reader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在现有 `apps/mobile` 与 `apps/api` 基础上，以最小闭环打通今日简报拉取、已读进度统计、卡片点击阅读与站内阅读弹层。

**Architecture:** 采用轻量直连方案，由 `TodayScreen` 在挂载后直接请求今日简报接口并把结果写入 store。store 负责维护 `digestGroups` 与 `readCount`，`ArticleCard` 负责展示与触发阅读，`ReaderModal` 按需拉取文章详情并在打开入口即时标记已读。

**Tech Stack:** Expo Router, React Native, TypeScript, Zustand, Vitest, Testing Library

---

## File Map

- Modify: `/workspace/apps/mobile/src/__tests__/app-store.test.ts`
- Create: `/workspace/apps/mobile/src/__tests__/TodayScreen.test.tsx`
- Create: `/workspace/apps/mobile/src/services/api.ts`
- Modify: `/workspace/apps/mobile/src/store/app-store.ts`
- Create: `/workspace/apps/mobile/src/features/today/TodayScreen.tsx`
- Create: `/workspace/apps/mobile/src/features/today/ArticleCard.tsx`
- Create: `/workspace/apps/mobile/src/features/reader/ReaderModal.tsx`
- Modify: `/workspace/apps/mobile/app/(tabs)/today.tsx`

## Task 1: 扩展 store 测试与状态

**Files:**
- Modify: `/workspace/apps/mobile/src/__tests__/app-store.test.ts`
- Modify: `/workspace/apps/mobile/src/store/app-store.ts`

- [ ] **Step 1: 先写失败的 store 测试**

```ts
it('marks an item as read and updates progress', () => {
  const store = createAppStore();

  store.getState().setDigest([
    {
      domainId: 'technology',
      items: [{ id: 'technology-1', isRead: false, title: 't', summary: 's' }]
    }
  ]);

  store.getState().markItemRead('technology-1');

  expect(store.getState().readCount).toBe(1);
  expect(store.getState().digestGroups[0]?.items[0]?.isRead).toBe(true);
});
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pnpm --dir /workspace/apps/mobile test -- app-store`
Expected: FAIL with missing `setDigest` or `markItemRead`

- [ ] **Step 3: 最小实现 digest state**

```ts
export type DigestListItem = {
  id: string;
  domainId: string;
  title: string;
  summary: string;
  source?: string;
  publishedAt?: string;
  isRead: boolean;
};

export type DigestGroup = {
  domainId: string;
  items: DigestListItem[];
};
```

```ts
setDigest: (groups) =>
  set({
    digestGroups: groups,
    readCount: countReadItems(groups)
  }),
markItemRead: (itemId) =>
  set((state) => {
    const digestGroups = state.digestGroups.map((group) => ({
      ...group,
      items: group.items.map((item) =>
        item.id === itemId ? { ...item, isRead: true } : item
      )
    }));

    return {
      digestGroups,
      readCount: countReadItems(digestGroups)
    };
  })
```

- [ ] **Step 4: 运行测试确认通过**

Run: `pnpm --dir /workspace/apps/mobile test -- app-store`
Expected: PASS

## Task 2: 先写 TodayScreen 基础链路测试

**Files:**
- Create: `/workspace/apps/mobile/src/__tests__/TodayScreen.test.tsx`
- Create: `/workspace/apps/mobile/src/services/api.ts`
- Create: `/workspace/apps/mobile/src/features/today/TodayScreen.tsx`
- Create: `/workspace/apps/mobile/src/features/today/ArticleCard.tsx`
- Create: `/workspace/apps/mobile/src/features/reader/ReaderModal.tsx`
- Modify: `/workspace/apps/mobile/app/(tabs)/today.tsx`

- [ ] **Step 1: 写 UI 失败测试**

```tsx
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { TodayScreen } from '../features/today/TodayScreen';
import { createAppStore } from '../store/app-store';

vi.mock('../services/api', () => ({
  fetchTodayDigest: vi.fn(),
  fetchItemDetail: vi.fn()
}));

it('loads digest, opens reader modal and marks item as read', async () => {
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

  expect(store.getState().readCount).toBe(1);
});
```

- [ ] **Step 2: 运行测试确认失败**

Run: `pnpm --dir /workspace/apps/mobile test -- TodayScreen`
Expected: FAIL with missing component, API module, or unread behavior

- [ ] **Step 3: 最小实现 API 与组件**

```ts
export async function fetchTodayDigest(selectedDomains: string[]) {
  const response = await fetch(`${API_BASE_URL}/digest/today`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_domains: selectedDomains,
      sort_preference: 'freshness',
      date: '2026-05-19'
    })
  });

  return response.json();
}
```

```tsx
useEffect(() => {
  if (selectedDomains.length === 0) {
    return;
  }

  void fetchTodayDigest(selectedDomains).then((payload) => {
    setDigest(mapDigestGroups(payload.groups));
  });
}, [selectedDomains, setDigest]);
```

```tsx
function handleOpen(item: DigestListItem) {
  markItemRead(item.id);
  setActiveItem(item);
}
```

```tsx
useEffect(() => {
  if (!visible || !itemId) {
    return;
  }

  void fetchItemDetail(itemId).then(setArticle);
}, [visible, itemId]);
```

- [ ] **Step 4: 运行测试确认通过**

Run: `pnpm --dir /workspace/apps/mobile test -- TodayScreen`
Expected: PASS

## Task 3: 路由接线与回归验证

**Files:**
- Modify: `/workspace/apps/mobile/app/(tabs)/today.tsx`
- Modify: `/workspace/apps/mobile/src/store/app-store.ts`

- [ ] **Step 1: 接入 TodayRoute**

```tsx
import { TodayScreen } from '../../src/features/today/TodayScreen';

export default function TodayRoute() {
  return <TodayScreen />;
}
```

- [ ] **Step 2: 运行聚焦测试**

Run: `pnpm --dir /workspace/apps/mobile test -- app-store`
Expected: PASS

Run: `pnpm --dir /workspace/apps/mobile test -- TodayScreen`
Expected: PASS

- [ ] **Step 3: 运行 mobile 全量测试**

Run: `pnpm --dir /workspace/apps/mobile test`
Expected: PASS with existing onboarding/store tests still green
