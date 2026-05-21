import { useEffect, useState } from 'react';
import { Redirect } from 'expo-router';
import { ActivityIndicator, StyleSheet, View } from 'react-native';
import { OnboardingScreen } from '../src/features/onboarding/OnboardingScreen';
import { useAppStore } from '../src/store/app-store';
import { getTheme } from '../src/theme/tokens';

export default function IndexScreen() {
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

  return hasCompletedOnboarding ? (
    <Redirect href="/(tabs)/today" />
  ) : (
    <OnboardingScreen />
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
