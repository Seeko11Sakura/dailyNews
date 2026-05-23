// 引导页负责让用户选择初始关注领域，并和应用状态、主题配置联动。
import { useMemo } from 'react';
import { domains, type DomainId } from '@dailynews/shared';
import { ScrollView, StyleSheet, Text, useWindowDimensions, View } from 'react-native';
import { AnimatedPressable } from '../../components/AnimatedPressable';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';

type OnboardingScreenProps = {
  store?: AppStore;
};

export function OnboardingScreen({ store }: OnboardingScreenProps) {
  const { width } = useWindowDimensions();
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
  const cardLayout = getCardLayout(width, theme.space.xl);
  const styles = createStyles(theme);

  return (
    <View style={styles.screen}>
      <ScrollView
        style={styles.scroller}
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.title}>定制边界</Text>
        <Text style={styles.subtitle}>
          选择你的核心领域。每天 10 分钟清零，隔绝算法噪音。
        </Text>
        {/* 顶部领域卡片用实际宽度，避免窄屏下被压成竖排。 */}
        <View style={styles.grid}>
          {(() => {
            const domain = domains[0];
            const selected = selectedDomainSet.has(domain.id as DomainId);
            const shortName = domain.name.split('与')[0].split('和')[0];
            return (
              <AnimatedPressable
                key={domain.id}
                onPress={() => toggleDomainSelection(domain.id)}
                accessibilityLabel={`${selected ? '取消选择' : '选择'}${domain.name}`}
                accessibilityRole="button"
                accessibilityState={{ selected }}
                style={[
                  styles.domainButton,
                  styles.fullWidthCard,
                  { width: cardLayout.full },
                  selected ? styles.selectedDomain : null
                ]}
                pressedStyle={styles.pressed}
              >
                <Text style={styles.domainEmoji}>{domain.emoji}</Text>
                <Text style={[styles.domainName, selected ? styles.selectedText : null]}>{shortName}</Text>
                {selected && (
                  <View style={styles.checkmark}>
                    <Text style={styles.checkmarkText}>✓</Text>
                  </View>
                )}
              </AnimatedPressable>
            );
          })()}
        </View>

        {/* 其他领域保持两列排列，并使用固定计算宽度保证对齐。 */}
        <View style={styles.grid}>
          {domains.slice(1).map((domain) => {
            const selected = selectedDomainSet.has(domain.id as DomainId);
            const shortName = domain.name.split('与')[0].split('和')[0];
            return (
              <AnimatedPressable
                key={domain.id}
                onPress={() => toggleDomainSelection(domain.id)}
                accessibilityLabel={`${selected ? '取消选择' : '选择'}${domain.name}`}
                accessibilityRole="button"
                accessibilityState={{ selected }}
                style={[
                  styles.domainButton,
                  { width: cardLayout.half },
                  selected ? styles.selectedDomain : null
                ]}
                pressedStyle={styles.pressed}
              >
                <Text style={styles.domainEmoji}>{domain.emoji}</Text>
                <Text style={[styles.domainName, selected ? styles.selectedText : null]}>{shortName}</Text>
                {selected && (
                  <View style={styles.checkmark}>
                    <Text style={styles.checkmarkText}>✓</Text>
                  </View>
                )}
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

// 根据屏幕宽度计算卡片宽度，保证两列和全宽卡片都不会溢出。
function getCardLayout(screenWidth: number, horizontalPadding: number) {
  const gap = 12;
  const contentWidth = Math.max(0, screenWidth - horizontalPadding * 2);

  return {
    full: contentWidth,
    half: Math.floor((contentWidth - gap) / 2)
  };
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
    paddingBottom: theme.space.lg
  },
  scroller: {
    flex: 1
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
    gap: 12,
    width: '100%'
  },
  domainButton: {
    height: 100,
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderRadius: 24,
    backgroundColor: theme.color.surface,
    borderWidth: 1,
    borderColor: theme.color.border,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
    ...theme.shadow.glass,
    flexShrink: 0
  },
  fullWidthCard: {
    height: 120,
    marginBottom: 12
  },
  selectedDomain: {
    backgroundColor: theme.color.primarySoft,
    borderColor: theme.color.primary,
    borderWidth: 2
  },
  domainEmoji: {
    fontSize: 32,
    marginBottom: 8
  },
  domainName: {
    color: theme.color.text,
    fontSize: 18,
    lineHeight: 24,
    textAlign: 'center',
    fontWeight: '700'
  },
  selectedText: {
    color: theme.color.primary
  },
  checkmark: {
    position: 'absolute',
    top: 8,
    right: 8,
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: theme.color.primary,
    alignItems: 'center',
    justifyContent: 'center'
  },
  checkmarkText: {
    color: theme.color.white,
    fontSize: 14,
    fontWeight: '800'
  },
  footer: {
    paddingHorizontal: theme.space.xl,
    paddingTop: theme.space.xxl,
    paddingBottom: theme.space.xl,
    backgroundColor: theme.color.background
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
