import { useEffect, useState } from 'react';
import { Redirect } from 'expo-router';
import { ActivityIndicator, View } from 'react-native';
import { OnboardingScreen } from '../src/features/onboarding/OnboardingScreen';
import { useAppStore } from '../src/store/app-store';

export default function IndexScreen() {
  const hasCompletedOnboarding = useAppStore(
    (state) => state.hasCompletedOnboarding
  );
  const hydrate = useAppStore((state) => state.hydrate);
  const [hasHydrated, setHasHydrated] = useState(false);

  useEffect(() => {
    void hydrate().finally(() => {
      setHasHydrated(true);
    });
  }, [hydrate]);

  if (!hasHydrated) {
    return (
      <View>
        <ActivityIndicator />
      </View>
    );
  }

  return hasCompletedOnboarding ? (
    <Redirect href="/(tabs)/today" />
  ) : (
    <OnboardingScreen />
  );
}
