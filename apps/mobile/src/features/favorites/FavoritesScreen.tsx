import { ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';
import { ThemeToggleButton } from '../../components/ThemeToggleButton';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';

type FavoritesScreenProps = {
  store?: AppStore;
};

export function FavoritesScreen({ store }: FavoritesScreenProps) {
  const favoriteIds = useAppStore((state) => state.favoriteIds, store);
  const themeMode = useAppStore((state) => state.themeMode, store);
  const toggleThemeMode = useAppStore((state) => state.toggleThemeMode, store);
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>知识存档</Text>
          <Text style={styles.subtitle}>{`已收藏 ${favoriteIds.length} 条`}</Text>
        </View>
        <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        <TextInput
          placeholder="搜索标题或来源"
          placeholderTextColor={theme.color.muted}
          accessibilityLabel="搜索标题或来源"
          style={styles.searchInput}
        />
        <Text style={styles.sectionTitle}>收藏列表</Text>
        <View style={styles.emptyCard}>
          <Text style={styles.emptyTitle}>
            {favoriteIds.length === 0 ? '暂无收藏内容' : '收藏内容即将同步'}
          </Text>
          <Text style={styles.emptyText}>
            阅读时保存的长文会沉淀在这里，适合复盘和二次检索。
          </Text>
        </View>
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
  header: {
    marginHorizontal: theme.space.lg,
    marginBottom: theme.space.md,
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
    fontWeight: '800',
    marginTop: theme.space.xs
  },
  content: {
    paddingHorizontal: theme.space.lg,
    paddingBottom: 116
  },
  searchInput: {
    minHeight: 52,
    paddingHorizontal: theme.space.lg,
    borderRadius: theme.radius.lg,
    backgroundColor: theme.color.surfaceStrong,
    borderWidth: 1,
    borderColor: theme.color.border,
    color: theme.color.text,
    fontSize: 16,
    fontWeight: '600',
    marginBottom: theme.space.xl
  },
  sectionTitle: {
    color: theme.color.text,
    fontSize: 18,
    fontWeight: '800',
    marginBottom: theme.space.md
  },
  emptyCard: {
    alignItems: 'center',
    paddingVertical: 52,
    paddingHorizontal: theme.space.xl,
    borderRadius: theme.radius.xl,
    backgroundColor: theme.color.surface,
    borderWidth: 1,
    borderColor: theme.color.border,
    ...theme.shadow.glass
  },
  emptyTitle: {
    color: theme.color.primary,
    fontSize: 22,
    lineHeight: 30,
    fontWeight: '800',
    textAlign: 'center',
    marginBottom: theme.space.sm
  },
  emptyText: {
    color: theme.color.muted,
    fontSize: 15,
    lineHeight: 24,
    textAlign: 'center',
    fontWeight: '500'
  }
});
}
