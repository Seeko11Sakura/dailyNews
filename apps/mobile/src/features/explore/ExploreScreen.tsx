import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';
import { AnimatedPressable } from '../../components/AnimatedPressable';
import { ThemeToggleButton } from '../../components/ThemeToggleButton';
import type { ExploreCard } from '../../services/api';
import { fetchExploreCards } from '../../services/api';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';

type ExploreScreenProps = {
  store?: AppStore;
};

export function ExploreScreen({ store }: ExploreScreenProps) {
  const selectedDomains = useAppStore((state) => state.selectedDomains, store);
  const themeMode = useAppStore((state) => state.themeMode, store);
  const toggleThemeMode = useAppStore((state) => state.toggleThemeMode, store);
  const toggleDomainSelection = useAppStore(
    (state) => state.toggleDomainSelection,
    store
  );
  const addDismissedDomain = useAppStore(
    (state) => state.addDismissedDomain,
    store
  );
  const dismissedDomains = useAppStore(
    (state) => state.dismissedDomains,
    store
  );

  const [cards, setCards] = useState<ExploreCard[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  const loadCards = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetchExploreCards(
        selectedDomains,
        dismissedDomains
      );
      setCards(response.cards);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
    } finally {
      setLoading(false);
    }
  }, [selectedDomains, dismissedDomains]);

  useEffect(() => {
    loadCards();
  }, [loadCards]);

  const handleDismiss = useCallback(
    (domainId: string) => {
      addDismissedDomain(domainId);
      setCards((prev) => prev.filter((c) => c.domain_id !== domainId));
    },
    [addDismissedDomain]
  );

  const handleFollow = useCallback(
    (domainId: string) => {
      toggleDomainSelection(domainId);
    },
    [toggleDomainSelection]
  );

  if (loading) {
    return (
      <View style={[styles.screen, styles.center]}>
        <ActivityIndicator size="large" color={theme.color.primary} />
      </View>
    );
  }

  if (error) {
    return (
      <View style={[styles.screen, styles.center]}>
        <Text style={styles.errorText}>{error}</Text>
        <AnimatedPressable onPress={loadCards} style={styles.retryButton}>
          <Text style={styles.retryText}>重试</Text>
        </AnimatedPressable>
      </View>
    );
  }

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>领域探索</Text>
          <Text style={styles.subtitle}>
            每天 3 个相邻领域，拓宽你的视野
          </Text>
        </View>
        <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
      </View>
      <ScrollView
        style={styles.scroller}
        contentContainerStyle={styles.cards}
        showsVerticalScrollIndicator={false}
      >
        {cards.map((card) => {
          const isSelected = selectedDomains.includes(card.domain_id);
          const isFull = selectedDomains.length >= 5;
          return (
            <View key={card.domain_id} style={styles.card}>
              <View style={styles.reasonPill}>
                <Text style={styles.reasonText} numberOfLines={1}>
                  {card.reason}
                </Text>
              </View>
              <Text style={styles.topic}>{card.domain_name}</Text>
              <View style={styles.previewBox}>
                {card.preview_titles.map((title, i) => (
                  <Text key={i} style={styles.preview}>
                    {title}
                  </Text>
                ))}
              </View>
              <View style={styles.actions}>
                <AnimatedPressable
                  onPress={() => handleFollow(card.domain_id)}
                  disabled={isSelected || isFull}
                  accessibilityRole="button"
                  accessibilityLabel={`${isSelected ? '已在主页' : '添加到主页'}${card.domain_name}`}
                  style={[
                    styles.followButton,
                    isSelected ? styles.followedButton : null,
                    isFull && !isSelected ? styles.disabledButton : null
                  ]}
                  pressedStyle={styles.pressed}
                >
                  <Text
                    style={[
                      styles.followButtonText,
                      isSelected ? styles.followedButtonText : null,
                      isFull && !isSelected ? styles.disabledText : null
                    ]}
                  >
                    {isSelected ? '已在主页' : isFull ? '已达上限' : '添加到主页'}
                  </Text>
                </AnimatedPressable>
                {!isSelected && (
                  <Pressable
                    onPress={() => handleDismiss(card.domain_id)}
                    style={styles.dismissButton}
                    accessibilityLabel={`不感兴趣${card.domain_name}`}
                  >
                    <Text style={styles.dismissText}>不感兴趣</Text>
                  </Pressable>
                )}
              </View>
            </View>
          );
        })}
        {cards.length === 0 && (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyText}>今日探索已完成</Text>
            <Text style={styles.emptySubtext}>
              所有相邻领域都已探索过，明天会有新内容
            </Text>
          </View>
        )}
      </ScrollView>
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
    center: {
      justifyContent: 'center',
      alignItems: 'center'
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
    subtitle: {
      color: theme.color.muted,
      fontSize: 12,
      marginTop: 2
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
      padding: theme.space.md,
      borderRadius: theme.radius.md,
      backgroundColor: theme.color.surfaceInner,
      marginBottom: 24,
      gap: 4
    },
    preview: {
      color: theme.color.muted,
      fontSize: 14,
      lineHeight: 22,
      fontWeight: '500'
    },
    actions: {
      flexDirection: 'row',
      gap: 12
    },
    followButton: {
      flex: 1,
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
    disabledButton: {
      backgroundColor: theme.color.surfaceStrong,
      opacity: 0.6
    },
    followButtonText: {
      color: theme.color.white,
      fontSize: 16,
      fontWeight: '800'
    },
    followedButtonText: {
      color: theme.color.muted
    },
    disabledText: {
      color: theme.color.muted
    },
    dismissButton: {
      minHeight: 52,
      paddingHorizontal: 20,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: theme.radius.pill,
      borderWidth: 1,
      borderColor: theme.color.border
    },
    dismissText: {
      color: theme.color.muted,
      fontSize: 14,
      fontWeight: '600'
    },
    pressed: {
      opacity: 0.78
    },
    errorText: {
      color: theme.color.muted,
      fontSize: 16,
      marginBottom: 16
    },
    retryButton: {
      paddingHorizontal: 24,
      paddingVertical: 12,
      borderRadius: theme.radius.pill,
      backgroundColor: theme.color.primary
    },
    retryText: {
      color: theme.color.white,
      fontSize: 14,
      fontWeight: '600'
    },
    emptyCard: {
      width: '100%',
      padding: 40,
      borderRadius: theme.radius.xl,
      backgroundColor: theme.color.surface,
      borderWidth: 1,
      borderColor: theme.color.border,
      alignItems: 'center',
      ...theme.shadow.glass
    },
    emptyText: {
      color: theme.color.text,
      fontSize: 20,
      fontWeight: '800',
      marginBottom: 8
    },
    emptySubtext: {
      color: theme.color.muted,
      fontSize: 14,
      textAlign: 'center'
    }
  });
}
