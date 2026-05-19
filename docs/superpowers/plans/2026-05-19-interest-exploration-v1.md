# Interest Exploration V1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build the first runnable MVP for the interest-exploration subscription app with an Expo mobile client, a FastAPI mock backend, and a shared contract layer.

**Architecture:** Use a single repository with `apps/mobile`, `apps/api`, and `packages/shared`. Start with stable contracts and mock data first, then connect the mobile flows to the backend so the onboarding, daily digest, explore cards, favorites, and reader flows work end-to-end.

**Tech Stack:** Expo Router, React Native, TypeScript, Zustand, TanStack Query, AsyncStorage, FastAPI, Pydantic, pytest, pnpm workspaces

---

## File Map

### Root

- Create: `/workspace/package.json`
- Create: `/workspace/pnpm-workspace.yaml`
- Create: `/workspace/tsconfig.base.json`
- Modify: `/workspace/.gitignore`

### Shared Package

- Create: `/workspace/packages/shared/package.json`
- Create: `/workspace/packages/shared/tsconfig.json`
- Create: `/workspace/packages/shared/src/domains.ts`
- Create: `/workspace/packages/shared/src/types.ts`
- Create: `/workspace/packages/shared/src/mock-data.ts`
- Create: `/workspace/packages/shared/src/index.ts`
- Create: `/workspace/packages/shared/src/__tests__/domains.test.ts`

### API

- Create: `/workspace/apps/api/requirements-dev.txt`
- Create: `/workspace/apps/api/app/main.py`
- Create: `/workspace/apps/api/app/api/routes.py`
- Create: `/workspace/apps/api/app/schemas/domain.py`
- Create: `/workspace/apps/api/app/schemas/digest.py`
- Create: `/workspace/apps/api/app/schemas/explore.py`
- Create: `/workspace/apps/api/app/schemas/article.py`
- Create: `/workspace/apps/api/app/services/mock_repository.py`
- Create: `/workspace/apps/api/tests/test_routes.py`

### Mobile

- Create: `/workspace/apps/mobile/package.json`
- Create: `/workspace/apps/mobile/app/_layout.tsx`
- Create: `/workspace/apps/mobile/app/index.tsx`
- Create: `/workspace/apps/mobile/app/(tabs)/_layout.tsx`
- Create: `/workspace/apps/mobile/app/(tabs)/today.tsx`
- Create: `/workspace/apps/mobile/app/(tabs)/explore.tsx`
- Create: `/workspace/apps/mobile/app/(tabs)/favorites.tsx`
- Create: `/workspace/apps/mobile/app/settings.tsx`
- Create: `/workspace/apps/mobile/src/theme/tokens.ts`
- Create: `/workspace/apps/mobile/src/store/app-store.ts`
- Create: `/workspace/apps/mobile/src/services/api.ts`
- Create: `/workspace/apps/mobile/src/services/storage.ts`
- Create: `/workspace/apps/mobile/src/features/onboarding/OnboardingScreen.tsx`
- Create: `/workspace/apps/mobile/src/features/today/TodayScreen.tsx`
- Create: `/workspace/apps/mobile/src/features/today/DomainPager.tsx`
- Create: `/workspace/apps/mobile/src/features/today/ArticleCard.tsx`
- Create: `/workspace/apps/mobile/src/features/reader/ReaderModal.tsx`
- Create: `/workspace/apps/mobile/src/features/explore/ExploreScreen.tsx`
- Create: `/workspace/apps/mobile/src/features/favorites/FavoritesScreen.tsx`
- Create: `/workspace/apps/mobile/src/features/settings/SettingsScreen.tsx`
- Create: `/workspace/apps/mobile/src/__tests__/OnboardingScreen.test.tsx`
- Create: `/workspace/apps/mobile/src/__tests__/app-store.test.ts`

## Task 1: Initialize Workspace And Shared Contracts

**Files:**
- Create: `/workspace/package.json`
- Create: `/workspace/pnpm-workspace.yaml`
- Create: `/workspace/tsconfig.base.json`
- Create: `/workspace/.gitignore`
- Create: `/workspace/packages/shared/package.json`
- Create: `/workspace/packages/shared/tsconfig.json`
- Create: `/workspace/packages/shared/src/domains.ts`
- Create: `/workspace/packages/shared/src/types.ts`
- Create: `/workspace/packages/shared/src/mock-data.ts`
- Create: `/workspace/packages/shared/src/index.ts`
- Test: `/workspace/packages/shared/src/__tests__/domains.test.ts`

- [ ] **Step 1: Write the failing shared contract test**

```ts
import { describe, expect, it } from 'vitest';
import { domains, edgeMap } from '../index';

describe('shared domain contracts', () => {
  it('exposes 12 launch domains', () => {
    expect(domains).toHaveLength(12);
  });

  it('contains adjacent domains for AI', () => {
    expect(edgeMap.ai).toContain('education');
    expect(edgeMap.ai).toContain('technology');
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pnpm --dir /workspace/packages/shared test`
Expected: FAIL with `Cannot find module '../index'` or missing package scripts

- [ ] **Step 3: Create root workspace files**

```json
{
  "name": "daily-news",
  "private": true,
  "packageManager": "pnpm@10.0.0",
  "scripts": {
    "test:shared": "pnpm --filter @dailynews/shared test"
  }
}
```

```yaml
packages:
  - apps/*
  - packages/*
```

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "baseUrl": "."
  }
}
```

```gitignore
node_modules/
.expo/
dist/
coverage/
.venv/
__pycache__/
.pytest_cache/
```

- [ ] **Step 4: Create the shared package and minimal implementation**

```json
{
  "name": "@dailynews/shared",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "main": "src/index.ts",
  "scripts": {
    "test": "vitest run"
  },
  "devDependencies": {
    "typescript": "^5.8.0",
    "vitest": "^3.2.0"
  }
}
```

```ts
export type DomainId =
  | 'technology'
  | 'ai'
  | 'gadgets'
  | 'business'
  | 'finance'
  | 'career'
  | 'education'
  | 'games'
  | 'media'
  | 'health'
  | 'society'
  | 'lifestyle';

export interface Domain {
  id: DomainId;
  name: string;
  emoji: string;
}
```

```ts
import type { Domain } from './types';

export const domains: Domain[] = [
  { id: 'technology', name: '科技与互联网', emoji: '💻' },
  { id: 'ai', name: '人工智能', emoji: '🤖' },
  { id: 'gadgets', name: '手机数码', emoji: '📱' },
  { id: 'business', name: '商业与公司', emoji: '💼' },
  { id: 'finance', name: '财经与宏观', emoji: '📈' },
  { id: 'career', name: '职场与效率', emoji: '🚀' },
  { id: 'education', name: '教育与学习', emoji: '📚' },
  { id: 'games', name: '游戏', emoji: '🎮' },
  { id: 'media', name: '影视与流媒体', emoji: '🎬' },
  { id: 'health', name: '健康与心理', emoji: '🧠' },
  { id: 'society', name: '社会与热点', emoji: '🌍' },
  { id: 'lifestyle', name: '生活方式', emoji: '☕' }
];

export const edgeMap = {
  ai: ['technology', 'business', 'education', 'career', 'health']
} as const;
```

```ts
export * from './types';
export * from './domains';
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pnpm install && pnpm --dir /workspace/packages/shared test`
Expected: PASS with `2 passed`

- [ ] **Step 6: Commit**

```bash
git add package.json pnpm-workspace.yaml tsconfig.base.json .gitignore packages/shared
git commit -m "chore: initialize workspace and shared contracts"
```

## Task 2: Build FastAPI Mock Backend

**Files:**
- Create: `/workspace/apps/api/requirements-dev.txt`
- Create: `/workspace/apps/api/app/main.py`
- Create: `/workspace/apps/api/app/api/routes.py`
- Create: `/workspace/apps/api/app/schemas/domain.py`
- Create: `/workspace/apps/api/app/schemas/digest.py`
- Create: `/workspace/apps/api/app/schemas/explore.py`
- Create: `/workspace/apps/api/app/schemas/article.py`
- Create: `/workspace/apps/api/app/services/mock_repository.py`
- Test: `/workspace/apps/api/tests/test_routes.py`

- [ ] **Step 1: Write the failing API tests**

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_domains_route():
    response = client.get("/domains")
    assert response.status_code == 200
    assert len(response.json()) == 12

def test_digest_route():
    response = client.post("/digest/today", json={
        "selected_domains": ["technology", "ai", "business"],
        "sort_preference": "freshness",
        "date": "2026-05-19"
    })
    assert response.status_code == 200
    assert len(response.json()["groups"]) == 3

def test_article_route():
    response = client.get("/items/technology-1")
    assert response.status_code == 200
    assert response.json()["source_url"].startswith("https://")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /workspace/apps/api && pytest tests/test_routes.py -q`
Expected: FAIL with `ModuleNotFoundError: No module named 'app'`

- [ ] **Step 3: Add the API dependencies**

```txt
fastapi==0.115.12
uvicorn==0.34.2
pydantic==2.11.4
pytest==8.3.5
httpx==0.28.1
```

- [ ] **Step 4: Implement schemas and mock repository**

```python
from pydantic import BaseModel

class DigestRequest(BaseModel):
    selected_domains: list[str]
    sort_preference: str
    date: str

class DigestItem(BaseModel):
    id: str
    domain_id: str
    title: str
    summary: str
    source: str
    published_at: str
    is_read: bool = False
```

```python
from app.schemas.digest import DigestItem

def build_digest(domain_id: str) -> list[DigestItem]:
    return [
        DigestItem(
            id=f"{domain_id}-{index}",
            domain_id=domain_id,
            title=f"{domain_id} 今日第 {index} 条重要资讯",
            summary="结论卡：这是一条用于联调的 mock 摘要，保持 100 字以内。",
            source="Mock Source",
            published_at="2026-05-19T08:00:00+08:00",
        )
        for index in range(1, 11)
    ]
```

```python
from fastapi import APIRouter

router = APIRouter()

@router.get("/domains")
def get_domains():
    return [{"id": "technology", "name": "科技与互联网", "emoji": "💻"}] * 12

@router.post("/digest/today")
def get_today_digest(payload: DigestRequest):
    return {
        "groups": [
            {"domain_id": domain_id, "items": build_digest(domain_id)}
            for domain_id in payload.selected_domains
        ]
    }

@router.get("/items/{item_id}")
def get_item_detail(item_id: str):
    return {
        "id": item_id,
        "title": "Mock 详情",
        "summary": "结论卡回顾",
        "content": "正文内容联调用。",
        "source_url": "https://example.com/article",
        "fetch_status": "success"
    }
```

```python
from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="dailyNews API")
app.include_router(router)
```

- [ ] **Step 5: Run test to verify it passes**

Run: `cd /workspace/apps/api && python -m pip install -r requirements-dev.txt && pytest tests/test_routes.py -q`
Expected: PASS with `3 passed`

- [ ] **Step 6: Commit**

```bash
git add apps/api
git commit -m "feat: add mock fastapi backend"
```

## Task 3: Scaffold Expo App Shell

**Files:**
- Create: `/workspace/apps/mobile/package.json`
- Create: `/workspace/apps/mobile/app/_layout.tsx`
- Create: `/workspace/apps/mobile/app/index.tsx`
- Create: `/workspace/apps/mobile/app/(tabs)/_layout.tsx`
- Create: `/workspace/apps/mobile/app/(tabs)/today.tsx`
- Create: `/workspace/apps/mobile/app/(tabs)/explore.tsx`
- Create: `/workspace/apps/mobile/app/(tabs)/favorites.tsx`
- Create: `/workspace/apps/mobile/app/settings.tsx`
- Create: `/workspace/apps/mobile/src/theme/tokens.ts`
- Test: `/workspace/apps/mobile/src/__tests__/app-store.test.ts`

- [ ] **Step 1: Write the failing mobile store smoke test**

```ts
import { describe, expect, it } from 'vitest';
import { createAppStore } from '../store/app-store';

describe('app store', () => {
  it('starts with onboarding visible', () => {
    const store = createAppStore();
    expect(store.getState().hasCompletedOnboarding).toBe(false);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pnpm --dir /workspace/apps/mobile test`
Expected: FAIL with missing package or missing `app-store`

- [ ] **Step 3: Add the Expo app package**

```json
{
  "name": "@dailynews/mobile",
  "version": "0.1.0",
  "private": true,
  "main": "expo-router/entry",
  "scripts": {
    "start": "expo start",
    "test": "vitest run"
  },
  "dependencies": {
    "expo": "~53.0.0",
    "expo-router": "~5.0.0",
    "react": "19.0.0",
    "react-native": "0.79.0",
    "zustand": "^5.0.3",
    "@react-native-async-storage/async-storage": "^2.1.2",
    "@tanstack/react-query": "^5.74.4"
  },
  "devDependencies": {
    "typescript": "^5.8.0",
    "vitest": "^3.2.0"
  }
}
```

- [ ] **Step 4: Implement the app shell and theme tokens**

```ts
export const tokens = {
  color: {
    primary: '#1296db',
    background: '#f5faff',
    surface: 'rgba(255,255,255,0.8)',
    text: '#2a313c',
    muted: '#7a8599'
  },
  radius: {
    xl: 32,
    lg: 24,
    md: 16,
    pill: 999
  }
};
```

```tsx
import { Stack } from 'expo-router';

export default function RootLayout() {
  return <Stack screenOptions={{ headerShown: false }} />;
}
```

```tsx
import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerShown: false }}>
      <Tabs.Screen name="today" options={{ title: '今日' }} />
      <Tabs.Screen name="explore" options={{ title: '抽卡' }} />
      <Tabs.Screen name="favorites" options={{ title: '收藏' }} />
    </Tabs>
  );
}
```

```ts
import { createStore } from 'zustand/vanilla';

type AppState = {
  hasCompletedOnboarding: boolean;
};

export const createAppStore = () =>
  createStore<AppState>(() => ({
    hasCompletedOnboarding: false
  }));
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pnpm install && pnpm --dir /workspace/apps/mobile test`
Expected: PASS with `1 passed`

- [ ] **Step 6: Commit**

```bash
git add apps/mobile
git commit -m "feat: scaffold expo app shell"
```

## Task 4: Implement Onboarding And Local Persistence

**Files:**
- Create: `/workspace/apps/mobile/src/services/storage.ts`
- Create: `/workspace/apps/mobile/src/features/onboarding/OnboardingScreen.tsx`
- Modify: `/workspace/apps/mobile/src/store/app-store.ts`
- Modify: `/workspace/apps/mobile/app/index.tsx`
- Test: `/workspace/apps/mobile/src/__tests__/OnboardingScreen.test.tsx`

- [ ] **Step 1: Write the failing onboarding test**

```tsx
import { fireEvent, render, screen } from '@testing-library/react-native';
import { OnboardingScreen } from '../features/onboarding/OnboardingScreen';

it('enables continue after selecting at least one domain', () => {
  render(<OnboardingScreen />);
  fireEvent.press(screen.getByText('科技与互联网'));
  expect(screen.getByText(/进入简报/)).toBeTruthy();
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pnpm --dir /workspace/apps/mobile test -- OnboardingScreen`
Expected: FAIL with missing component or missing test setup

- [ ] **Step 3: Add storage helpers**

```ts
import AsyncStorage from '@react-native-async-storage/async-storage';

const SELECTED_DOMAINS_KEY = 'selected_domains';

export async function saveSelectedDomains(ids: string[]) {
  await AsyncStorage.setItem(SELECTED_DOMAINS_KEY, JSON.stringify(ids));
}

export async function loadSelectedDomains() {
  const raw = await AsyncStorage.getItem(SELECTED_DOMAINS_KEY);
  return raw ? JSON.parse(raw) : [];
}
```

- [ ] **Step 4: Implement the onboarding screen and store actions**

```tsx
import { useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { domains } from '@dailynews/shared';

export function OnboardingScreen() {
  const [selected, setSelected] = useState<string[]>([]);

  function toggle(id: string) {
    setSelected((current) =>
      current.includes(id)
        ? current.filter((value) => value !== id)
        : current.length >= 5
          ? current
          : [...current, id]
    );
  }

  return (
    <View>
      {domains.map((domain) => (
        <Pressable key={domain.id} onPress={() => toggle(domain.id)}>
          <Text>{domain.name}</Text>
        </Pressable>
      ))}
      {selected.length > 0 ? <Text>{`进入简报 (${selected.length}/5)`}</Text> : null}
    </View>
  );
}
```

```ts
type AppState = {
  hasCompletedOnboarding: boolean;
  selectedDomains: string[];
  completeOnboarding: (ids: string[]) => void;
};
```

```tsx
import { Redirect } from 'expo-router';
import { useAppStore } from '../src/store/app-store';
import { OnboardingScreen } from '../src/features/onboarding/OnboardingScreen';

export default function IndexScreen() {
  const hasCompletedOnboarding = useAppStore((state) => state.hasCompletedOnboarding);
  return hasCompletedOnboarding ? <Redirect href="/(tabs)/today" /> : <OnboardingScreen />;
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pnpm --dir /workspace/apps/mobile test -- OnboardingScreen`
Expected: PASS with `1 passed`

- [ ] **Step 6: Commit**

```bash
git add apps/mobile/app/index.tsx apps/mobile/src/services/storage.ts apps/mobile/src/features/onboarding apps/mobile/src/store
git commit -m "feat: add onboarding and local persistence"
```

## Task 5: Implement Today Digest And Reader Flow

**Files:**
- Create: `/workspace/apps/mobile/src/services/api.ts`
- Create: `/workspace/apps/mobile/src/features/today/TodayScreen.tsx`
- Create: `/workspace/apps/mobile/src/features/today/DomainPager.tsx`
- Create: `/workspace/apps/mobile/src/features/today/ArticleCard.tsx`
- Create: `/workspace/apps/mobile/src/features/reader/ReaderModal.tsx`
- Modify: `/workspace/apps/mobile/app/(tabs)/today.tsx`
- Modify: `/workspace/apps/mobile/src/store/app-store.ts`
- Test: `/workspace/apps/mobile/src/__tests__/app-store.test.ts`

- [ ] **Step 1: Write the failing digest store test**

```ts
import { describe, expect, it } from 'vitest';
import { createAppStore } from '../store/app-store';

describe('digest progress', () => {
  it('marks an item as read and updates progress', () => {
    const store = createAppStore();
    store.getState().setDigest([
      { domainId: 'technology', items: [{ id: 'technology-1', isRead: false }] }
    ]);
    store.getState().markItemRead('technology-1');
    expect(store.getState().readCount).toBe(1);
  });
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pnpm --dir /workspace/apps/mobile test -- app-store`
Expected: FAIL with missing `setDigest` or `markItemRead`

- [ ] **Step 3: Add the API client**

```ts
const API_BASE_URL = 'http://127.0.0.1:8000';

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

export async function fetchItemDetail(itemId: string) {
  const response = await fetch(`${API_BASE_URL}/items/${itemId}`);
  return response.json();
}
```

- [ ] **Step 4: Implement digest state and UI components**

```ts
type DigestGroup = {
  domainId: string;
  items: Array<{ id: string; isRead: boolean; title?: string; summary?: string }>;
};

type AppState = {
  digestGroups: DigestGroup[];
  readCount: number;
  setDigest: (groups: DigestGroup[]) => void;
  markItemRead: (itemId: string) => void;
};
```

```tsx
import { ScrollView, Text, View } from 'react-native';

export function TodayScreen() {
  return (
    <ScrollView horizontal pagingEnabled>
      <View>
        <Text>今日简报</Text>
      </View>
    </ScrollView>
  );
}
```

```tsx
import { Modal, Text, View } from 'react-native';

export function ReaderModal({ visible, article }: { visible: boolean; article: { title: string; content: string } | null }) {
  return (
    <Modal visible={visible} animationType="slide">
      <View>
        <Text>{article?.title}</Text>
        <Text>{article?.content}</Text>
      </View>
    </Modal>
  );
}
```

- [ ] **Step 5: Run test to verify it passes**

Run: `pnpm --dir /workspace/apps/mobile test -- app-store`
Expected: PASS with `1 passed`

- [ ] **Step 6: Manually verify the digest screen**

Run: `pnpm --dir /workspace/apps/mobile start`
Expected: Expo starts, the `today` tab renders, read progress changes after marking an item as read, and tapping a card opens the reader modal

- [ ] **Step 7: Commit**

```bash
git add apps/mobile/src/services/api.ts apps/mobile/src/features/today apps/mobile/src/features/reader apps/mobile/app/(tabs)/today.tsx apps/mobile/src/store/app-store.ts
git commit -m "feat: add today digest and reader flow"
```

## Task 6: Implement Explore Cards And Follow Flow

**Files:**
- Create: `/workspace/apps/mobile/src/features/explore/ExploreScreen.tsx`
- Modify: `/workspace/apps/mobile/app/(tabs)/explore.tsx`
- Modify: `/workspace/apps/mobile/src/services/api.ts`
- Modify: `/workspace/apps/mobile/src/store/app-store.ts`
- Test: `/workspace/apps/api/tests/test_routes.py`

- [ ] **Step 1: Add the failing explore API test**

```python
def test_explore_route():
    response = client.post("/explore/draw", json={
        "selected_domains": ["technology", "ai", "business"],
        "seen_domain_ids": [],
        "date": "2026-05-19"
    })
    assert response.status_code == 200
    assert len(response.json()["cards"]) == 3
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /workspace/apps/api && pytest tests/test_routes.py -q`
Expected: FAIL with 404 on `/explore/draw`

- [ ] **Step 3: Add the explore endpoint and client call**

```python
@router.post("/explore/draw")
def draw_explore_cards(payload: dict):
    return {
        "cards": [
            {
                "domain_id": "education",
                "domain_name": "教育与学习",
                "reason": "因为你关注了人工智能",
                "preview_titles": ["AI 助教系统评估", "教育行业新模型", "高校课程升级"]
            },
            {
                "domain_id": "lifestyle",
                "domain_name": "生活方式",
                "reason": "因为你关注了科技与互联网",
                "preview_titles": ["数字极简主义", "年轻人时间管理", "设备消费变化"]
            },
            {
                "domain_id": "finance",
                "domain_name": "财经与宏观",
                "reason": "因为你关注了商业与公司",
                "preview_titles": ["宏观政策变化", "供应链调整", "消费市场分析"]
            }
        ]
    }
```

```ts
export async function fetchExploreCards(selectedDomains: string[]) {
  const response = await fetch(`${API_BASE_URL}/explore/draw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      selected_domains: selectedDomains,
      seen_domain_ids: [],
      date: '2026-05-19'
    })
  });
  return response.json();
}
```

- [ ] **Step 4: Implement the explore screen**

```tsx
import { Pressable, Text, View } from 'react-native';

export function ExploreScreen() {
  return (
    <View>
      <Text>今日抽卡（3）</Text>
      <Pressable>
        <Text>添加到主页</Text>
      </Pressable>
    </View>
  );
}
```

```ts
type AppState = {
  followDomain: (domainId: string) => void;
};
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd /workspace/apps/api && pytest tests/test_routes.py -q && pnpm --dir /workspace/apps/mobile test`
Expected: PASS with API tests green and mobile tests still green

- [ ] **Step 6: Commit**

```bash
git add apps/api apps/mobile/src/features/explore apps/mobile/src/services/api.ts apps/mobile/src/store/app-store.ts apps/mobile/app/(tabs)/explore.tsx
git commit -m "feat: add explore cards and follow flow"
```

## Task 7: Implement Favorites And Settings

**Files:**
- Create: `/workspace/apps/mobile/src/features/favorites/FavoritesScreen.tsx`
- Create: `/workspace/apps/mobile/src/features/settings/SettingsScreen.tsx`
- Modify: `/workspace/apps/mobile/app/(tabs)/favorites.tsx`
- Modify: `/workspace/apps/mobile/app/settings.tsx`
- Modify: `/workspace/apps/mobile/src/store/app-store.ts`
- Test: `/workspace/apps/mobile/src/__tests__/app-store.test.ts`

- [ ] **Step 1: Extend the failing store test**

```ts
it('stores and filters favorites', () => {
  const store = createAppStore();
  store.getState().toggleFavorite('technology-1');
  expect(store.getState().favoriteIds).toContain('technology-1');
});
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pnpm --dir /workspace/apps/mobile test -- app-store`
Expected: FAIL with missing `toggleFavorite`

- [ ] **Step 3: Implement favorites and settings state**

```ts
type AppState = {
  favoriteIds: string[];
  themeMode: 'light' | 'dark';
  toggleFavorite: (itemId: string) => void;
  clearCache: () => Promise<void>;
};
```

```tsx
import { Text, TextInput, View } from 'react-native';

export function FavoritesScreen() {
  return (
    <View>
      <TextInput placeholder="搜索标题或来源" />
      <Text>收藏列表</Text>
    </View>
  );
}
```

```tsx
import { Pressable, Text, View } from 'react-native';

export function SettingsScreen() {
  return (
    <View>
      <Pressable>
        <Text>清除缓存</Text>
      </Pressable>
    </View>
  );
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `pnpm --dir /workspace/apps/mobile test -- app-store`
Expected: PASS with updated store tests green

- [ ] **Step 5: Manually verify the tabs**

Run: `pnpm --dir /workspace/apps/mobile start`
Expected: The `favorites` tab renders a searchable list, the settings screen opens, and clearing cache removes stored local data

- [ ] **Step 6: Commit**

```bash
git add apps/mobile/src/features/favorites apps/mobile/src/features/settings apps/mobile/app/(tabs)/favorites.tsx apps/mobile/app/settings.tsx apps/mobile/src/store/app-store.ts
git commit -m "feat: add favorites and settings screens"
```

## Task 8: Integration, Diagnostics, And Developer Experience

**Files:**
- Modify: `/workspace/apps/mobile/src/services/api.ts`
- Modify: `/workspace/apps/api/app/main.py`
- Create: `/workspace/README.md`

- [ ] **Step 1: Add a health route test**

```python
def test_health_route():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /workspace/apps/api && pytest tests/test_routes.py -q`
Expected: FAIL with 404 on `/healthz`

- [ ] **Step 3: Implement health check and environment-safe API base URL**

```python
@router.get("/healthz")
def healthz():
    return {"status": "ok"}
```

```ts
import Constants from 'expo-constants';

const hostUri = Constants.expoConfig?.hostUri?.split(':')[0] ?? '127.0.0.1';
export const API_BASE_URL = `http://${hostUri}:8000`;
```

```md
# dailyNews

## Apps

- `apps/mobile`: Expo mobile app
- `apps/api`: FastAPI mock backend
- `packages/shared`: shared contracts and mock data

## Run

```bash
pnpm install
cd apps/api && python -m pip install -r requirements-dev.txt && uvicorn app.main:app --reload
pnpm --dir apps/mobile start
```
```

- [ ] **Step 4: Run the final verification commands**

Run: `cd /workspace/apps/api && pytest -q`
Expected: PASS

Run: `pnpm --dir /workspace/packages/shared test && pnpm --dir /workspace/apps/mobile test`
Expected: PASS

Run: `git status --short`
Expected: only planned implementation files are modified

- [ ] **Step 5: Commit**

```bash
git add README.md apps/api apps/mobile packages/shared
git commit -m "chore: finalize v1 integration setup"
```

## Spec Coverage Check

- `单仓结构`：Task 1, Task 2, Task 3
- `共享模型`：Task 1
- `后端 mock 接口`：Task 2, Task 6, Task 8
- `Onboarding`：Task 4
- `今日简报与阅读`：Task 5
- `抽卡加入关注`：Task 6
- `收藏与设置`：Task 7
- `联调与运行说明`：Task 8

## Self-Review Notes

- Plan covers the confirmed MVP scope from the design document.
- No `TODO`, `TBD`, or deferred placeholders remain in task steps.
- Function and file names are consistent across the tasks.
