import { useMemo } from 'react';
import { domains, edgeMap, type Domain, type DomainId } from '@dailynews/shared';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { AnimatedPressable } from '../../components/AnimatedPressable';
import { ThemeToggleButton } from '../../components/ThemeToggleButton';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';

type ExploreScreenProps = {
  store?: AppStore;
};

const domainById = new Map(domains.map((domain) => [domain.id, domain]));

export function ExploreScreen({ store }: ExploreScreenProps) {
  const selectedDomains = useAppStore((state) => state.selectedDomains, store);
  const themeMode = useAppStore((state) => state.themeMode, store);
  const toggleThemeMode = useAppStore((state) => state.toggleThemeMode, store);
  const toggleDomainSelection = useAppStore(
    (state) => state.toggleDomainSelection,
    store
  );

  const recommendations = useMemo(
    () => getRecommendations(selectedDomains),
    [selectedDomains]
  );
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>领域探索</Text>
        </View>
        <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
      </View>
      <ScrollView
        style={styles.scroller}
        contentContainerStyle={styles.cards}
        showsVerticalScrollIndicator={false}
      >
        {recommendations.map(({ domain, reason }) => {
          const selected = selectedDomains.includes(domain.id);
          return (
            <View key={domain.id} style={styles.card}>
              <View style={styles.reasonPill}>
                <Text style={styles.reasonText} numberOfLines={1}>
                  {reason}
                </Text>
              </View>
              <Text style={styles.topic}>{domain.name}</Text>
              <View style={styles.previewBox}>
                <Text style={styles.preview}>
                  从今天的资讯里抽取一个相邻视角，帮助你低成本判断它是否值得长期关注。
                </Text>
              </View>
              <AnimatedPressable
                onPress={() => toggleDomainSelection(domain.id)}
                accessibilityRole="button"
                accessibilityLabel={`${selected ? '移出主页' : '添加到主页'}${domain.name}`}
                accessibilityState={{ selected }}
                style={[
                  styles.followButton,
                  selected ? styles.followedButton : null
                ]}
                pressedStyle={styles.pressed}
              >
                <Text
                  style={[
                    styles.followButtonText,
                    selected ? styles.followedButtonText : null
                  ]}
                >
                  {selected ? '已在主页' : '添加到主页'}
                </Text>
              </AnimatedPressable>
            </View>
          );
        })}
      </ScrollView>
    </View>
  );
}

function getRecommendations(selectedDomains: DomainId[]) {
  const selectedSet = new Set(selectedDomains);
  const sourceIds: DomainId[] =
    selectedDomains.length > 0 ? selectedDomains : ['technology', 'ai'];
  const seen = new Set<DomainId>();

  const adjacent = sourceIds.flatMap((sourceId) =>
    (edgeMap[sourceId] ?? []).map((domainId: DomainId) => ({
      domainId,
      reason: `因为关注「${domainById.get(sourceId)?.name ?? sourceId}」`
    }))
  );

  const picks: Array<{ domain: Domain; reason: string }> = [];
  for (const item of adjacent) {
    if (seen.has(item.domainId) || selectedSet.has(item.domainId)) {
      continue;
    }

    const domain = domainById.get(item.domainId);
    if (!domain) {
      continue;
    }

    seen.add(item.domainId);
    picks.push({ domain, reason: item.reason });
  }

  return picks.length > 0
    ? picks.slice(0, 6)
    : domains.slice(0, 6).map((domain) => ({
        domain,
        reason: '从热门领域开始'
      }));
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
    marginBottom: 30,
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
    fontWeight: '800'
  },
  cards: {
    gap: 18,
    paddingHorizontal: theme.space.xl,
    paddingBottom: 18
  },
  scroller: {
    marginBottom: 118
  },
  card: {
    width: '100%',
    height: 316,
    paddingHorizontal: theme.space.xl,
    paddingTop: theme.space.xl,
    paddingBottom: 22,
    borderRadius: theme.radius.xl,
    backgroundColor: theme.color.surface,
    borderWidth: 1,
    borderColor: theme.color.border,
    ...theme.shadow.glass
  },
  reasonPill: {
    alignSelf: 'flex-start',
    height: 28,
    minWidth: 116,
    paddingHorizontal: 12,
    borderRadius: theme.radius.sm,
    backgroundColor: theme.color.primarySoft,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16
  },
  reasonText: {
    color: theme.color.primary,
    fontSize: 12,
    fontWeight: '800',
    lineHeight: 16,
    textAlign: 'center'
  },
  topic: {
    color: theme.color.text,
    fontSize: 26,
    lineHeight: 34,
    fontWeight: '800',
    marginBottom: 12
  },
  previewBox: {
    height: 100,
    padding: theme.space.md,
    borderRadius: theme.radius.md,
    backgroundColor: theme.color.surfaceInner,
    marginBottom: 32,
    justifyContent: 'center'
  },
  preview: {
    color: theme.color.muted,
    fontSize: 14,
    lineHeight: 22,
    fontWeight: '500'
  },
  followButton: {
    minHeight: 52,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.primary
  },
  followedButton: {
    backgroundColor: theme.color.surfaceStrong,
    borderWidth: 1,
    borderColor: theme.color.faint
  },
  followButtonText: {
    color: theme.color.white,
    fontSize: 16,
    fontWeight: '800'
  },
  followedButtonText: {
    color: theme.color.muted
  },
  pressed: {
    opacity: 0.78
  }
});
}
