import { StyleSheet, Text, View } from 'react-native';
import { getTheme } from '../theme/tokens';

type ProgressBarProps = {
  current: number;
  total: number;
  themeMode: 'light' | 'dark';
};

export function ProgressBar({ current, total, themeMode }: ProgressBarProps) {
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);
  const progress = total > 0 ? current / total : 0;

  return (
    <View style={styles.container}>
      <View style={styles.track}>
        <View style={[styles.fill, { width: `${progress * 100}%` }]} />
      </View>
      <Text style={styles.label}>
        {current} / {total} 领域
      </Text>
    </View>
  );
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
    container: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: 12,
      paddingHorizontal: 4
    },
    track: {
      flex: 1,
      height: 6,
      borderRadius: 3,
      backgroundColor: theme.color.surfaceStrong,
      overflow: 'hidden'
    },
    fill: {
      height: '100%',
      borderRadius: 3,
      backgroundColor: theme.color.primary
    },
    label: {
      color: theme.color.muted,
      fontSize: 12,
      fontWeight: '600',
      minWidth: 60,
      textAlign: 'right'
    }
  });
}
