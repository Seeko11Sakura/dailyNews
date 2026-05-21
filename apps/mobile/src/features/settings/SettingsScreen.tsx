import { StyleSheet, Text, View } from 'react-native';
import { AnimatedPressable } from '../../components/AnimatedPressable';
import { ThemeToggleButton } from '../../components/ThemeToggleButton';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';

type SettingsScreenProps = {
  store?: AppStore;
};

export function SettingsScreen({ store }: SettingsScreenProps) {
  const themeMode = useAppStore((state) => state.themeMode, store);
  const toggleThemeMode = useAppStore((state) => state.toggleThemeMode, store);
  const clearCache = useAppStore((state) => state.clearCache, store);
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  return (
    <View style={styles.screen}>
      <View style={styles.header}>
        <View>
          <Text style={styles.title}>设置</Text>
          <Text style={styles.subtitle}>偏好与本地数据</Text>
        </View>
        <ThemeToggleButton mode={themeMode} onToggle={toggleThemeMode} />
      </View>
      <View style={styles.panel}>
        <View style={styles.row}>
          <View>
            <Text style={styles.rowTitle}>主题模式</Text>
            <Text style={styles.rowText}>{themeMode === 'dark' ? '深色' : '浅色'}</Text>
          </View>
          <View style={styles.modePill}>
            <Text style={styles.modePillText}>{themeMode === 'dark' ? 'Dark' : 'Light'}</Text>
          </View>
        </View>
        <AnimatedPressable
          onPress={toggleThemeMode}
          accessibilityRole="switch"
          accessibilityLabel="切换浅色深色模式"
          accessibilityState={{ checked: themeMode === 'dark' }}
          style={styles.themeButton}
          pressedStyle={styles.pressed}
        >
          <Text style={styles.themeButtonText}>
            {themeMode === 'dark' ? '切换浅色模式' : '切换深色模式'}
          </Text>
        </AnimatedPressable>
        <AnimatedPressable
          onPress={() => void clearCache()}
          accessibilityRole="button"
          accessibilityLabel="清除缓存"
          style={styles.clearButton}
          pressedStyle={styles.pressed}
        >
          <Text style={styles.clearButtonText}>清除缓存</Text>
        </AnimatedPressable>
      </View>
    </View>
  );
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: theme.color.background,
    paddingTop: 40,
    paddingHorizontal: theme.space.lg
  },
  header: {
    marginBottom: theme.space.xl,
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
  panel: {
    padding: theme.space.xl,
    borderRadius: theme.radius.xl,
    backgroundColor: theme.color.surface,
    borderWidth: 1,
    borderColor: theme.color.border,
    ...theme.shadow.glass
  },
  row: {
    minHeight: 64,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: theme.space.md,
    marginBottom: theme.space.xl
  },
  rowTitle: {
    color: theme.color.text,
    fontSize: 17,
    fontWeight: '800',
    marginBottom: theme.space.xs
  },
  rowText: {
    color: theme.color.muted,
    fontSize: 14,
    fontWeight: '600'
  },
  modePill: {
    minHeight: 44,
    minWidth: 76,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.primarySoft
  },
  modePillText: {
    color: theme.color.primary,
    fontSize: 13,
    fontWeight: '800'
  },
  clearButton: {
    minHeight: 56,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.primary
  },
  themeButton: {
    minHeight: 56,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.primarySoft,
    marginBottom: theme.space.md
  },
  themeButtonText: {
    color: theme.color.primary,
    fontSize: 16,
    fontWeight: '800'
  },
  clearButtonText: {
    color: theme.color.white,
    fontSize: 16,
    fontWeight: '800'
  },
  pressed: {
    opacity: 0.78
  }
});
}
