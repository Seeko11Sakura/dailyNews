import { useEffect, useState } from 'react';
import { Linking, ScrollView, StyleSheet, Text, View } from 'react-native';
import { AnimatedPressable } from '../../components/AnimatedPressable';
import { fetchItemDetail, type ArticleDetail } from '../../services/api';
import { getTheme } from '../../theme/tokens';

type ReaderModalProps = {
  visible: boolean;
  itemId: string | null;
  onClose: () => void;
  theme: ReturnType<typeof getTheme>;
};

export function ReaderModal({ visible, itemId, onClose, theme }: ReaderModalProps) {
  const [article, setArticle] = useState<ArticleDetail | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!visible || !itemId) {
      setArticle(null);
      setError(null);
      setIsLoading(false);
      return;
    }

    setIsLoading(true);
    setError(null);

    void fetchItemDetail(itemId)
      .then((payload) => {
        setArticle(payload);
      })
      .catch(() => {
        setError('站内阅读暂时不可用');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [itemId, visible]);

  if (!visible) {
    return null;
  }

  const styles = createStyles(theme);

  return (
    <View accessibilityViewIsModal style={styles.overlay}>
      <View style={styles.handle} />
      <View style={styles.header}>
        <AnimatedPressable
          onPress={onClose}
          accessibilityLabel="关闭阅读"
          accessibilityRole="button"
          hitSlop={8}
          style={styles.closeButton}
          pressedStyle={styles.pressed}
        >
          <Text style={styles.closeText}>×</Text>
        </AnimatedPressable>
      </View>
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        {isLoading ? <Text style={styles.status}>加载中...</Text> : null}
        {error ? <Text style={styles.status}>{error}</Text> : null}
        {article ? (
          <View>
            <Text style={styles.title}>{article.title}</Text>
            <View style={styles.summaryBox}>
              <Text style={styles.summary}>{article.summary}</Text>
            </View>
            <Text style={styles.body}>{article.content}</Text>
            <AnimatedPressable
              onPress={() => void Linking.openURL(article.source_url)}
              accessibilityLabel="打开原文站点"
              accessibilityRole="link"
              style={styles.sourceButton}
              pressedStyle={styles.pressed}
            >
              <Text style={styles.sourceButtonText}>一键直达原文站</Text>
            </AnimatedPressable>
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    top: 40,
    zIndex: 20,
    borderTopLeftRadius: 40,
    borderTopRightRadius: 40,
    backgroundColor: theme.color.surfaceStrong,
    borderWidth: 1,
    borderColor: theme.color.border,
    ...theme.shadow.glass
  },
  handle: {
    width: 48,
    height: 6,
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.faint,
    alignSelf: 'center',
    marginTop: theme.space.md,
    marginBottom: theme.space.sm
  },
  header: {
    alignItems: 'flex-end',
    paddingHorizontal: theme.space.xl,
    paddingBottom: theme.space.md
  },
  closeButton: {
    width: 44,
    height: 44,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.faint
  },
  closeText: {
    color: theme.color.text,
    fontSize: 26,
    lineHeight: 28,
    fontWeight: '700'
  },
  content: {
    paddingHorizontal: theme.space.xl,
    paddingBottom: 48
  },
  status: {
    color: theme.color.muted,
    fontSize: 16,
    lineHeight: 26,
    fontWeight: '600'
  },
  title: {
    color: theme.color.text,
    fontSize: 24,
    lineHeight: 34,
    fontWeight: '800',
    marginBottom: theme.space.xl
  },
  summaryBox: {
    padding: theme.space.lg,
    borderRadius: theme.radius.lg,
    backgroundColor: theme.color.primarySoft,
    borderWidth: 1,
    borderColor: theme.color.border,
    marginBottom: theme.space.xxl
  },
  summary: {
    color: theme.color.text,
    fontSize: 16,
    lineHeight: 26,
    fontWeight: '600'
  },
  body: {
    color: theme.color.muted,
    fontSize: 17,
    lineHeight: 30,
    fontWeight: '500'
  },
  sourceButton: {
    minHeight: 56,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: theme.space.xl,
    borderRadius: theme.radius.pill,
    backgroundColor: theme.color.primary,
    ...theme.shadow.primary
  },
  sourceButtonText: {
    color: theme.color.white,
    fontSize: 16,
    fontWeight: '800'
  },
  pressed: {
    opacity: 0.78
  }
});
}
