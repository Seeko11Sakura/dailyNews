import { useEffect, useState } from 'react';
import { Redirect, Tabs } from 'expo-router';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { AppDock } from '../../src/components/AppDock';
import { useAppStore } from '../../src/store/app-store';
import { getTheme } from '../../src/theme/tokens';

export default function TabsLayout() {
  const hasCompletedOnboarding = useAppStore(
    (state) => state.hasCompletedOnboarding
  );
  const hydrate = useAppStore((state) => state.hydrate);
  const themeMode = useAppStore((state) => state.themeMode);
  const [hasHydrated, setHasHydrated] = useState(false);
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  useEffect(() => {
    void hydrate().finally(() => {
      setHasHydrated(true);
    });
  }, [hydrate]);

  if (!hasHydrated) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={theme.color.primary} />
      </View>
    );
  }

  if (!hasCompletedOnboarding) {
    return <Redirect href="/" />;
  }

  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: false
      }}
      tabBar={(props) => <AppDock {...props} />}
    >
      <Tabs.Screen name="today" options={{ title: '今日' }} />
      <Tabs.Screen name="explore" options={{ title: '抽卡' }} />
      <Tabs.Screen name="favorites" options={{ title: '收藏' }} />
    </Tabs>
  );
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
    loading: {
      flex: 1,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: theme.color.background
    }
  });
}
