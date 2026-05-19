import { useMemo } from 'react';
import { domains, type DomainId } from '@dailynews/shared';
import { Pressable, Text, View } from 'react-native';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';

type OnboardingScreenProps = {
  store?: AppStore;
};

export function OnboardingScreen({ store }: OnboardingScreenProps) {
  const selectedDomains = useAppStore((state) => state.selectedDomains, store);
  const toggleDomainSelection = useAppStore(
    (state) => state.toggleDomainSelection,
    store
  );
  const completeOnboarding = useAppStore((state) => state.completeOnboarding, store);

  const selectedDomainSet = useMemo(
    () => new Set(selectedDomains),
    [selectedDomains]
  );

  return (
    <View>
      {domains.map((domain) => {
        const selected = selectedDomainSet.has(domain.id as DomainId);
        return (
          <Pressable
            key={domain.id}
            onPress={() => toggleDomainSelection(domain.id)}
            accessibilityRole="button"
          >
            <Text>{domain.name}</Text>
            {selected ? <Text>已选择</Text> : null}
          </Pressable>
        );
      })}
      {selectedDomains.length > 0 ? (
        <Pressable onPress={() => void completeOnboarding()} accessibilityRole="button">
          <Text>{`进入简报 (${selectedDomains.length}/5)`}</Text>
        </Pressable>
      ) : null}
    </View>
  );
}
