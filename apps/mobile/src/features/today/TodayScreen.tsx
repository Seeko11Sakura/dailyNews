import { useEffect, useMemo, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { domains, type DomainId } from '@dailynews/shared';
import { ThemeToggleButton } from '../../components/ThemeToggleButton';
import { fetchTodayDigest } from '../../services/api';
import type { AppStore, DigestGroup, DigestListItem } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';
import { ReaderModal } from '../reader/ReaderModal';
import { ArticleCard } from './ArticleCard';

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
      isRead: item.is_read
    }))
  }));
}

function countTotalItems(groups: DigestGroup[]) {
  return groups.reduce((total, group) => total + group.items.length, 0);
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
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeItemId, setActiveItemId] = useState<string | null>(null);
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  useEffect(() => {
    if (selectedDomains.length === 0) {
      return;
    }

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

  const totalCount = useMemo(() => countTotalItems(digestGroups), [digestGroups]);
  const progress = totalCount === 0 ? 0 : Math.round((readCount / totalCount) * 100);

  function handleOpen(item: DigestListItem) {
    markItemRead(item.id);
    setActiveItemId(item.id);
  }

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>今日简报</Text>
          <View style={styles.progressRow}>
            <View style={styles.progressTrack}>
              <View style={[styles.progressBar, { width: `${progress}%` }]} />
            </View>
            <Text style={styles.progressText}>{`已读 ${readCount}/${totalCount}`}</Text>
          </View>
        </View>
        <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
      </View>

      {selectedDomains.length === 0 ? (
        <View style={styles.stateCard}>
          <Text style={styles.stateTitle}>请先完成兴趣选择</Text>
          <Text style={styles.stateText}>选择最多 5 个核心领域后，今日简报会在这里生成。</Text>
        </View>
      ) : null}
      {isLoading ? (
        <View style={styles.stateCard}>
          <Text style={styles.stateTitle}>加载中...</Text>
          <Text style={styles.stateText}>正在整理今天值得读的内容。</Text>
        </View>
      ) : null}
      {error ? (
        <View style={styles.stateCard}>
          <Text style={styles.errorText}>{error}</Text>
        </View>
      ) : null}

      <ScrollView
        contentContainerStyle={styles.listContent}
        showsVerticalScrollIndicator={false}
      >
        {totalCount > 0 && readCount === totalCount ? (
          <View style={styles.zeroCard}>
            <Text style={styles.zeroTitle}>今日已清零</Text>
            <Text style={styles.stateText}>极简阅读，保持清醒。去享受真实的生活吧。</Text>
          </View>
        ) : null}
        {digestGroups.map((group) => (
          <View key={group.domainId} style={styles.group}>
            <Text style={styles.groupTitle}>{domainNames.get(group.domainId) ?? group.domainId}</Text>
            {group.items.map((item, index) => (
              <ArticleCard
                key={item.id}
                item={item}
                onOpen={handleOpen}
                domainName={domainNames.get(group.domainId)}
                index={index}
                total={group.items.length}
                theme={theme}
              />
            ))}
          </View>
        ))}
      </ScrollView>
      <ReaderModal
        visible={activeItemId !== null}
        itemId={activeItemId}
        onClose={() => setActiveItemId(null)}
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
  title: {
    color: theme.color.primary,
    fontSize: 20,
    fontWeight: '800',
    marginBottom: theme.space.xs
  },
  progressRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.space.sm
  },
  progressTrack: {
    width: 108,
    height: 6,
    borderRadius: theme.radius.pill,
    overflow: 'hidden',
    backgroundColor: theme.color.faint
  },
  progressBar: {
    height: '100%',
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.primary
  },
  progressText: {
    color: theme.color.muted,
    fontSize: 12,
    fontWeight: '800'
  },
  listContent: {
    paddingHorizontal: theme.space.lg,
    paddingBottom: 116
  },
  group: {
    marginTop: theme.space.md
  },
  groupTitle: {
    color: theme.color.primaryDark,
    fontSize: 15,
    fontWeight: '800',
    marginBottom: theme.space.md,
    marginLeft: theme.space.xs
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
  zeroCard: {
    alignItems: 'center',
    marginTop: theme.space.lg,
    marginBottom: theme.space.xl,
    padding: theme.space.xxl,
    borderRadius: theme.radius.xl,
    backgroundColor: theme.color.surface,
    borderWidth: 1,
    borderColor: theme.color.border,
    ...theme.shadow.glass
  },
  zeroTitle: {
    color: theme.color.primary,
    fontSize: 26,
    fontWeight: '800',
    marginBottom: theme.space.sm
  }
});
}
