import { useCallback, useEffect, useMemo, useState } from 'react';
import { StyleSheet, Text, View } from 'react-native';
import { domains, type DomainId } from '@dailynews/shared';
import { ProgressBar } from '../../components/ProgressBar';
import { ThemeToggleButton } from '../../components/ThemeToggleButton';
import { fetchTodayDigest } from '../../services/api';
import type { AppStore, DigestGroup } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';
import { ReaderModal } from '../reader/ReaderModal';
import { DomainPager } from './DomainPager';

type TodayScreenProps = {
  store?: AppStore;
};

function mapDigestGroups(
  groups: Array<{
    domain_id: string;
    items: Array<{
      id: string;
      domain_id: string;
      title: string;
      summary: string;
      source: string;
      published_at: string;
      cover_image_url?: string | null;
      is_read: boolean;
    }>;
  }>
): DigestGroup[] {
  return groups.map((group) => ({
    domainId: group.domain_id as DomainId,
    items: group.items.map((item) => ({
      id: item.id,
      domainId: item.domain_id as DomainId,
      title: item.title,
      summary: item.summary,
      source: item.source,
      publishedAt: item.published_at,
      coverImageUrl: item.cover_image_url,
      isRead: item.is_read
    }))
  }));
}

function countReadDomains(groups: DigestGroup[]) {
  return groups.filter((group) => group.items.every((item) => item.isRead)).length;
}

const domainNames = new Map(domains.map((domain) => [domain.id, domain.name]));

export function TodayScreen({ store }: TodayScreenProps) {
  const selectedDomains = useAppStore((state) => state.selectedDomains, store);
  const digestGroups = useAppStore((state) => state.digestGroups, store);
  const readCount = useAppStore((state) => state.readCount, store);
  const themeMode = useAppStore((state) => state.themeMode, store);
  const toggleThemeMode = useAppStore((state) => state.toggleThemeMode, store);
  const setDigest = useAppStore((state) => state.setDigest, store);
  const markItemRead = useAppStore((state) => state.markItemRead, store);
  const setReaderOpen = useAppStore((state) => state.setReaderOpen, store);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeItemId, setActiveItemId] = useState<string | null>(null);
  const [currentDomainIndex, setCurrentDomainIndex] = useState(0);
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  useEffect(() => {
    if (selectedDomains.length === 0) return;

    setIsLoading(true);
    setError(null);

    void fetchTodayDigest(selectedDomains)
      .then((payload) => {
        setDigest(mapDigestGroups(payload.groups));
      })
      .catch(() => {
        setError('今日简报加载失败');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [selectedDomains, setDigest]);

  const totalCount = useMemo(
    () => digestGroups.reduce((t, g) => t + g.items.length, 0),
    [digestGroups]
  );
  const readDomains = useMemo(() => countReadDomains(digestGroups), [digestGroups]);
  const allDone = totalCount > 0 && readCount === totalCount;
  const isDigestEmpty = digestGroups.length > 0 && totalCount === 0;

  const handleItemRead = useCallback(
    (itemId: string) => {
      markItemRead(itemId);
    },
    [markItemRead]
  );

  const handleItemPress = useCallback(
    (itemId: string) => {
      markItemRead(itemId);
      setActiveItemId(itemId);
      setReaderOpen(true);
    },
    [markItemRead, setReaderOpen]
  );

  const handleDomainChange = useCallback((index: number) => {
    setCurrentDomainIndex(index);
  }, []);

  const pagerData = useMemo(
    () =>
      digestGroups.map((group) => ({
        domainId: group.domainId,
        domainName: domainNames.get(group.domainId) ?? group.domainId,
        items: group.items
      })),
    [digestGroups]
  );

  if (selectedDomains.length === 0) {
    return (
      <View style={styles.screen}>
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>今日简报</Text>
            <Text style={styles.subtitle}>选择领域后开始阅读</Text>
          </View>
          <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
        </View>
        <View style={styles.stateCard}>
          <Text style={styles.stateTitle}>请先完成兴趣选择</Text>
          <Text style={styles.stateText}>
            选择最多 5 个核心领域后，今日简报会在这里生成。
          </Text>
        </View>
      </View>
    );
  }

  if (isLoading) {
    return (
      <View style={styles.screen}>
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>今日简报</Text>
            <Text style={styles.subtitle}>加载中...</Text>
          </View>
          <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
        </View>
        <View style={styles.stateCard}>
          <Text style={styles.stateTitle}>加载中...</Text>
          <Text style={styles.stateText}>正在整理今天值得读的内容。</Text>
        </View>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.screen}>
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>今日简报</Text>
            <Text style={styles.subtitle}>加载失败</Text>
          </View>
          <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
        </View>
        <View style={styles.stateCard}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <Text style={styles.title}>今日简报</Text>
          <ProgressBar
            current={readDomains}
            total={digestGroups.length}
            themeMode={themeMode}
          />
        </View>
        <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
      </View>

      {allDone ? (
        <View style={styles.doneCard}>
          <Text style={styles.doneTitle}>今日已清零</Text>
          <Text style={styles.doneText}>
            极简阅读，保持清醒。去享受真实的生活吧。
          </Text>
        </View>
      ) : isDigestEmpty ? (
        <View style={styles.stateCard}>
          <Text style={styles.stateTitle}>今日简报正在生成</Text>
          <Text style={styles.stateText}>
            系统会在每天 8 点抓取当天资讯并生成 AI 概览，请稍后刷新。
          </Text>
        </View>
      ) : (
        <DomainPager
          domains={pagerData}
          themeMode={themeMode}
          onDomainChange={handleDomainChange}
          onItemRead={handleItemRead}
          onItemPress={handleItemPress}
        />
      )}

      <ReaderModal
        visible={activeItemId !== null}
        itemId={activeItemId}
        onClose={() => {
          setActiveItemId(null);
          setReaderOpen(false);
        }}
        theme={theme}
      />
    </View>
  );
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
    screen: {
      flex: 1,
      backgroundColor: theme.color.background,
      paddingTop: 40
    },
    header: {
      marginHorizontal: theme.space.lg,
      marginBottom: theme.space.sm,
      paddingVertical: theme.space.md,
      paddingHorizontal: theme.space.xl,
      borderRadius: theme.radius.pill,
      backgroundColor: theme.color.surface,
      borderWidth: 1,
      borderColor: theme.color.border,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      ...theme.shadow.glass
    },
    headerContent: {
      flex: 1,
      marginRight: theme.space.md
    },
    title: {
      color: theme.color.primary,
      fontSize: 20,
      fontWeight: '800',
      marginBottom: theme.space.xs
    },
    subtitle: {
      color: theme.color.muted,
      fontSize: 12,
      marginTop: 2
    },
    stateCard: {
      margin: theme.space.lg,
      padding: theme.space.xl,
      borderRadius: theme.radius.xl,
      backgroundColor: theme.color.surface,
      borderWidth: 1,
      borderColor: theme.color.border,
      ...theme.shadow.glass
    },
    stateTitle: {
      color: theme.color.text,
      fontSize: 18,
      fontWeight: '800',
      marginBottom: theme.space.sm
    },
    stateText: {
      color: theme.color.muted,
      fontSize: 15,
      lineHeight: 24,
      fontWeight: '500'
    },
    errorText: {
      color: theme.color.primaryDark,
      fontSize: 15,
      lineHeight: 24,
      fontWeight: '700'
    },
    doneCard: {
      margin: theme.space.lg,
      padding: theme.space.xxl,
      borderRadius: theme.radius.xl,
      backgroundColor: theme.color.surface,
      borderWidth: 1,
      borderColor: theme.color.border,
      alignItems: 'center',
      ...theme.shadow.glass
    },
    doneTitle: {
      color: theme.color.primary,
      fontSize: 26,
      fontWeight: '800',
      marginBottom: theme.space.sm
    },
    doneText: {
      color: theme.color.muted,
      fontSize: 15,
      lineHeight: 24,
      fontWeight: '500',
      textAlign: 'center'
    }
  });
}
