import { Pressable, StyleSheet, Text, View } from 'react-native';
import { Dimensions } from 'react-native';
import { AnimatedPressable } from '../../components/AnimatedPressable';
import { getTheme } from '../../theme/tokens';

const { width: SCREEN_WIDTH } = Dimensions.get('window');
const CARD_WIDTH = SCREEN_WIDTH - 48;

type ArticleCardProps = {
  // New interface for matrix layout
  id?: string;
  title?: string;
  summary?: string;
  source?: string;
  publishedAt?: string;
  isRead?: boolean;
  themeMode?: 'light' | 'dark';
  onPress?: () => void;
  onMarkRead?: () => void;
  fillHeight?: boolean;
};

export function ArticleCard({
  id,
  title = '',
  summary = '',
  source = '',
  publishedAt = '',
  isRead = false,
  themeMode = 'light',
  onPress,
  onMarkRead,
  fillHeight = false
}: ArticleCardProps) {
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  return (
    <View style={[styles.wrapper, fillHeight && styles.fillWrapper, isRead && styles.readWrapper]}>
      <View style={[styles.card, fillHeight && styles.fillCard]}>
        <View style={styles.topBar}>
          <Text style={styles.readState}>{isRead ? '已读' : '未读'}</Text>
        </View>
        <Text style={styles.title} numberOfLines={fillHeight ? undefined : 3}>
          {title}
        </Text>
        <Text style={styles.meta}>{`${source} · ${formatTime(publishedAt)}`}</Text>
        <View style={styles.conclusionBox}>
          <Text style={styles.conclusionLabel}>结论速读</Text>
          <Text style={styles.summary} numberOfLines={fillHeight ? undefined : 4}>
            {summary}
          </Text>
        </View>
        <AnimatedPressable
          onPress={onPress}
          accessibilityLabel={`阅读全文：${title}`}
          accessibilityRole="button"
          style={styles.openButton}
          pressedStyle={styles.pressed}
        >
          <Text style={styles.openButtonText}>阅读全文</Text>
        </AnimatedPressable>
      </View>
    </View>
  );
}

function formatTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleTimeString('zh-CN', {
    hour: '2-digit',
    minute: '2-digit'
  });
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
    wrapper: {
      gap: theme.space.md,
      marginBottom: theme.space.xl
    },
    fillWrapper: {
      width: CARD_WIDTH,
      marginRight: theme.space.lg,
      marginBottom: 0
    },
    readWrapper: {
      opacity: 0.58
    },
    card: {
      minHeight: 320,
      padding: theme.space.xl,
      borderRadius: theme.radius.xl,
      backgroundColor: theme.color.surface,
      borderWidth: 1,
      borderColor: theme.color.border,
      ...theme.shadow.glass
    },
    fillCard: {
      flex: 1,
      minHeight: 0
    },
    topBar: {
      flexDirection: 'row',
      alignItems: 'center',
      gap: theme.space.sm,
      marginBottom: theme.space.lg,
      flexWrap: 'wrap'
    },
    readState: {
      marginLeft: 'auto',
      color: theme.color.muted,
      fontSize: 13,
      fontWeight: '700'
    },
    title: {
      color: theme.color.text,
      fontSize: 22,
      fontWeight: '800',
      lineHeight: 32,
      marginBottom: theme.space.md
    },
    meta: {
      color: theme.color.muted,
      fontSize: 13,
      fontWeight: '600',
      marginBottom: theme.space.xl
    },
    conclusionBox: {
      flex: 1,
      padding: theme.space.lg,
      borderRadius: theme.radius.lg,
      backgroundColor: theme.color.surfaceInner,
      borderWidth: 1,
      borderColor: theme.color.border
    },
    conclusionLabel: {
      color: theme.color.primary,
      fontSize: 13,
      fontWeight: '800',
      marginBottom: theme.space.sm
    },
    summary: {
      color: theme.color.text,
      fontSize: 16,
      lineHeight: 26,
      fontWeight: '500'
    },
    openButton: {
      minHeight: 56,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: theme.radius.lg,
      backgroundColor: theme.color.primary,
      marginTop: theme.space.md,
      ...theme.shadow.primary
    },
    pressed: {
      opacity: 0.82
    },
    openButtonText: {
      color: theme.color.white,
      fontSize: 16,
      fontWeight: '800'
    }
  });
}
