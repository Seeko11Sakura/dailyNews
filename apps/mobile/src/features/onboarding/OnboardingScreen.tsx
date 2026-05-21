import { useMemo } from 'react';
import { domains, type DomainId } from '@dailynews/shared';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { AnimatedPressable } from '../../components/AnimatedPressable';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';

type OnboardingScreenProps = {
  store?: AppStore;
};

export function OnboardingScreen({ store }: OnboardingScreenProps) {
  const selectedDomains = useAppStore((state) => state.selectedDomains, store);
  const themeMode = useAppStore((state) => state.themeMode, store);
  const toggleDomainSelection = useAppStore(
    (state) => state.toggleDomainSelection,
    store
  );
  const completeOnboarding = useAppStore((state) => state.completeOnboarding, store);

  const selectedDomainSet = useMemo(
    () => new Set(selectedDomains),
    [selectedDomains]
  );
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  return (
    <View style={styles.screen}>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.title}>定制边界</Text>
        <Text style={styles.subtitle}>
          选择你的核心领域。每天 10 分钟清零，隔绝算法噪音。
        </Text>
        <View style={styles.grid}>
          {domains.map((domain, index) => {
            const selected = selectedDomainSet.has(domain.id as DomainId);
            return (
              <AnimatedPressable
                key={domain.id}
                onPress={() => toggleDomainSelection(domain.id)}
                accessibilityLabel={`${selected ? '取消选择' : '选择'}${domain.name}`}
                accessibilityRole="button"
                accessibilityState={{ selected }}
                style={[
                  styles.domainButton,
                  index === 0 ? styles.heroDomain : null,
                  selected ? styles.selectedDomain : null
                ]}
                pressedStyle={styles.pressed}
              >
                <Text
                  style={[
                    styles.domainName,
                    index === 0 ? styles.heroDomainName : null,
                    selected ? styles.selectedText : null
                  ]}
                >
                  {domain.name}
                </Text>
                {selected ? <Text style={styles.selectedText}>已选择</Text> : null}
              </AnimatedPressable>
            );
          })}
        </View>
      </ScrollView>
      <View style={styles.footer}>
        <AnimatedPressable
          onPress={() => void completeOnboarding()}
          accessibilityRole="button"
          accessibilityState={{ disabled: selectedDomains.length === 0 }}
          disabled={selectedDomains.length === 0}
          style={[
            styles.startButton,
            selectedDomains.length === 0 ? styles.disabledButton : null
          ]}
          pressedStyle={styles.pressed}
        >
          <Text style={styles.startButtonText}>
            {selectedDomains.length > 0
              ? `进入简报 (${selectedDomains.length}/5)`
              : '开启清零之旅'}
          </Text>
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
    paddingTop: 50
  },
  content: {
    paddingHorizontal: theme.space.xl,
    paddingBottom: 132
  },
  title: {
    color: theme.color.primary,
    fontSize: 34,
    lineHeight: 42,
    fontWeight: '800',
    marginBottom: theme.space.md
  },
  subtitle: {
    color: theme.color.muted,
    fontSize: 16,
    lineHeight: 26,
    fontWeight: '600',
    marginBottom: 40
  },
  grid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: theme.space.md
  },
  domainButton: {
    width: '47%',
    minHeight: 96,
    alignItems: 'center',
    justifyContent: 'center',
    padding: theme.space.md,
    borderRadius: theme.radius.xl,
    backgroundColor: theme.color.surface,
    borderWidth: 1,
    borderColor: theme.color.border,
    ...theme.shadow.glass
  },
  heroDomain: {
    width: '100%',
    minHeight: 116
  },
  selectedDomain: {
    backgroundColor: theme.color.primary,
    borderColor: theme.color.primary
  },
  domainName: {
    color: theme.color.text,
    fontSize: 16,
    lineHeight: 22,
    textAlign: 'center',
    fontWeight: '800'
  },
  heroDomainName: {
    fontSize: 20,
    lineHeight: 28
  },
  selectedText: {
    color: theme.color.white,
    fontSize: 13,
    lineHeight: 20,
    fontWeight: '800',
    marginTop: theme.space.xs
  },
  footer: {
    position: 'absolute',
    left: theme.space.xl,
    right: theme.space.xl,
    bottom: theme.space.xl
  },
  startButton: {
    minHeight: 60,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.primary,
    ...theme.shadow.primary
  },
  disabledButton: {
    opacity: 0.42
  },
  startButtonText: {
    color: theme.color.white,
    fontSize: 18,
    fontWeight: '800'
  },
  pressed: {
    opacity: 0.8
  }
});
}
