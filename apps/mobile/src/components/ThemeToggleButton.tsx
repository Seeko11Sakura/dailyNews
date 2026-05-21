import { StyleSheet, View } from 'react-native';
import { AnimatedPressable } from './AnimatedPressable';
import type { ThemeMode } from '../theme/tokens';
import { getTheme } from '../theme/tokens';

type ThemeToggleButtonProps = {
  mode: ThemeMode;
  onToggle: () => void | Promise<void>;
};

export function ThemeToggleButton({ mode, onToggle }: ThemeToggleButtonProps) {
  const theme = getTheme(mode);
  const styles = createStyles(theme);
  const isDark = mode === 'dark';

  return (
    <AnimatedPressable
      onPress={() => void onToggle()}
      accessibilityRole="switch"
      accessibilityLabel={isDark ? '切换浅色模式' : '切换深色模式'}
      accessibilityState={{ checked: isDark }}
      hitSlop={8}
      style={styles.button}
      pressedStyle={styles.pressed}
    >
      {isDark ? <SunGlyph /> : <MoonGlyph />}
    </AnimatedPressable>
  );
}

function SunGlyph() {
  return (
    <View style={glyphStyles.sunWrap}>
      {Array.from({ length: 8 }).map((_, index) => (
        <View
          key={index}
          style={[
            glyphStyles.ray,
            {
              transform: [{ rotate: `${index * 45}deg` }, { translateY: -9 }]
            }
          ]}
        />
      ))}
      <View style={glyphStyles.sunCore} />
    </View>
  );
}

function MoonGlyph() {
  return (
    <View style={glyphStyles.moon}>
      <View style={glyphStyles.moonCutout} />
    </View>
  );
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
    button: {
      width: 44,
      height: 44,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 22,
      backgroundColor: theme.color.surfaceInner,
      borderWidth: 1,
      borderColor: theme.color.border
    },
    pressed: {
      opacity: 0.8
    }
  });
}

const glyphStyles = StyleSheet.create({
  sunWrap: {
    width: 24,
    height: 24,
    alignItems: 'center',
    justifyContent: 'center'
  },
  sunCore: {
    width: 15,
    height: 15,
    borderRadius: 8,
    backgroundColor: '#ff8a24'
  },
  ray: {
    position: 'absolute',
    width: 3,
    height: 7,
    borderRadius: 2,
    backgroundColor: '#ffd25a'
  },
  moon: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#2ab0f5'
  },
  moonCutout: {
    position: 'absolute',
    right: -2,
    top: -1,
    width: 17,
    height: 17,
    borderRadius: 9,
    backgroundColor: '#f5faff'
  }
});
