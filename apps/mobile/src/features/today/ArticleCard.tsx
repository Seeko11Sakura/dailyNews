import { Pressable, StyleSheet, Text, View } from 'react-native';
import type { DigestListItem } from '../../store/app-store';
import { getTheme } from '../../theme/tokens';
import { AnimatedPressable } from '../../components/AnimatedPressable';

type ArticleCardProps = {
  item: DigestListItem;
  onOpen: (item: DigestListItem) => void;
  domainName?: string;
  index?: number;
  total?: number;
  theme: ReturnType<typeof getTheme>;
};

export function ArticleCard({
  item,
  onOpen,
  domainName,
  index,
  total,
  theme
}: ArticleCardProps) {
  const styles = createStyles(theme);

  return (
    <View style={[styles.wrapper, item.isRead ? styles.readWrapper : null]}>
      <View style={styles.card}>
        <View style={styles.topBar}>
          <Text style={styles.domainTag}>{domainName ?? item.domainId}</Text>
          {index !== undefined && total !== undefined ? (
            <Text style={styles.indexTag}>{`${index + 1} / ${total}`}</Text>
          ) : null}
          <Text style={styles.readState}>{item.isRead ? '已读' : '未读'}</Text>
        </View>
        <Text style={styles.title}>{item.title}</Text>
        <Text style={styles.meta}>{`${item.source} · ${formatTime(item.publishedAt)}`}</Text>
        <View style={styles.conclusionBox}>
          <Text style={styles.conclusionLabel}>结论速读</Text>
          <Text style={styles.summary}>{item.summary}</Text>
        </View>
      </View>
      <AnimatedPressable
        onPress={() => onOpen(item)}
        accessibilityLabel={`阅读全文：${item.title}`}
        accessibilityRole="button"
        style={styles.openButton}
        pressedStyle={styles.pressed}
      >
        <Text style={styles.openButtonText}>阅读全文</Text>
      </AnimatedPressable>
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
  topBar: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: theme.space.sm,
    marginBottom: theme.space.lg,
    flexWrap: 'wrap'
  },
  domainTag: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: theme.radius.sm,
    overflow: 'hidden',
    backgroundColor: theme.color.primarySoft,
    color: theme.color.primary,
    fontSize: 13,
    fontWeight: '800'
  },
  indexTag: {
    color: theme.color.muted,
    fontSize: 13,
    fontWeight: '700'
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
