// 今日页领域分页，负责按兴趣领域组织横向文章卡片。
import { useCallback, useRef, useState } from 'react';
import {
  Animated,
  Dimensions,
  FlatList,
  StyleSheet,
  Text,
  View,
  ViewToken
} from 'react-native';
import { getTheme } from '../../theme/tokens';
import { ArticleCard } from './ArticleCard';

export const DOMAIN_HEIGHT = 500;
const ARTICLE_LIST_HEIGHT = 500;

type DomainPagerProps = {
  domains: Array<{
    domainId: string;
    domainName: string;
    items: Array<{
      id: string;
      title: string;
      summary: string;
      source: string;
      publishedAt: string;
      coverImageUrl?: string | null;
      isRead: boolean;
    }>;
  }>;
  themeMode: 'light' | 'dark';
  onDomainChange: (index: number) => void;
  onItemRead: (itemId: string) => void;
  onItemPress: (itemId: string) => void;
};

export function DomainPager({
  domains,
  themeMode,
  onDomainChange,
  onItemRead,
  onItemPress
}: DomainPagerProps) {
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);
  const flatListRef = useRef<FlatList>(null);
  const [currentIndex, setCurrentIndex] = useState(0);

  const onViewableItemsChanged = useCallback(
    ({ viewableItems }: { viewableItems: ViewToken[] }) => {
      if (viewableItems.length > 0 && viewableItems[0].index != null) {
        setCurrentIndex(viewableItems[0].index);
        onDomainChange(viewableItems[0].index);
      }
    },
    [onDomainChange]
  );

  const viewabilityConfig = useRef({
    itemVisiblePercentThreshold: 50
  }).current;

  const onHorizontalViewableItemsChanged = useCallback(() => {
    // Track horizontal position if needed
  }, []);

  const horizontalViewabilityConfig = useRef({
    itemVisiblePercentThreshold: 50
  }).current;

  const renderDomain = useCallback(
    ({ item, index }: { item: typeof domains[0]; index: number }) => (
      <View style={styles.domainContainer}>
        <View style={styles.domainHeader}>
          <Text style={styles.domainName}>{item.domainName}</Text>
          <Text style={styles.domainIndex}>
            {index + 1} / {domains.length}
          </Text>
        </View>
        {item.items.length === 0 ? (
          <View style={styles.emptyCard}>
            <Text style={styles.emptyTitle}>该领域今日正在生成</Text>
            <Text style={styles.emptyText}>
              系统正在抓取并解析今天的内容，稍后刷新查看。
            </Text>
          </View>
        ) : (
          <FlatList
            data={item.items}
            horizontal
            pagingEnabled
            showsHorizontalScrollIndicator={false}
            keyExtractor={(article) => article.id}
            style={styles.articleList}
            renderItem={({ item: article }) => (
              <ArticleCard
                id={article.id}
                title={article.title}
                summary={article.summary}
                source={article.source}
                publishedAt={article.publishedAt}
                coverImageUrl={article.coverImageUrl}
                domainName={item.domainName}
                isRead={article.isRead}
                themeMode={themeMode}
                onPress={() => onItemPress(article.id)}
                onMarkRead={() => onItemRead(article.id)}
                fillHeight
              />
            )}
            onViewableItemsChanged={onHorizontalViewableItemsChanged}
            viewabilityConfig={horizontalViewabilityConfig}
          />
        )}
      </View>
    ),
    [domains.length, themeMode, onItemPress, onItemRead, styles, onHorizontalViewableItemsChanged, horizontalViewabilityConfig]
  );

  return (
    <View style={styles.container}>
      <FlatList
        ref={flatListRef}
        data={domains}
        vertical
        showsVerticalScrollIndicator={false}
        keyExtractor={(item) => item.domainId}
        renderItem={renderDomain}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        contentContainerStyle={styles.listContent}
        bounces={false}
      />
    </View>
  );
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
    container: {
      flex: 1
    },
    listContent: {
      paddingBottom: 150
    },
    domainContainer: {
      paddingHorizontal: theme.space.lg,
      marginBottom: theme.space.xxl
    },
    domainHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: theme.space.md
    },
    articleList: {
      height: ARTICLE_LIST_HEIGHT
    },
    emptyCard: {
      borderRadius: 28,
      backgroundColor: theme.color.surface,
      paddingHorizontal: theme.space.lg,
      paddingVertical: theme.space.lg,
      shadowColor: theme.color.shadow,
      shadowOpacity: 0.12,
      shadowRadius: 24,
      shadowOffset: { width: 0, height: 14 },
      elevation: 6
    },
    emptyTitle: {
      color: theme.color.text,
      fontSize: 18,
      fontWeight: '800',
      marginBottom: theme.space.sm
    },
    emptyText: {
      color: theme.color.muted,
      fontSize: 14,
      fontWeight: '600',
      lineHeight: 22
    },
    domainName: {
      color: theme.color.text,
      fontSize: 24,
      fontWeight: '800'
    },
    domainIndex: {
      color: theme.color.muted,
      fontSize: 14,
      fontWeight: '600'
    }
  });
}
