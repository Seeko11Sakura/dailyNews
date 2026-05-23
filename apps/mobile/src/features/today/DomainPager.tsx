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

const { height: SCREEN_HEIGHT } = Dimensions.get('window');
const DOMAIN_HEIGHT = SCREEN_HEIGHT - 200;

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

  const renderDomain = useCallback(
    ({ item, index }: { item: typeof domains[0]; index: number }) => (
      <View style={styles.domainContainer}>
        <View style={styles.domainHeader}>
          <Text style={styles.domainName}>{item.domainName}</Text>
          <Text style={styles.domainIndex}>
            {index + 1} / {domains.length}
          </Text>
        </View>
        <FlatList
          data={item.items}
          horizontal
          pagingEnabled
          showsHorizontalScrollIndicator={false}
          keyExtractor={(article) => article.id}
          renderItem={({ item: article }) => (
            <ArticleCard
              id={article.id}
              title={article.title}
              summary={article.summary}
              source={article.source}
              publishedAt={article.publishedAt}
              isRead={article.isRead}
              themeMode={themeMode}
              onPress={() => onItemPress(article.id)}
              onMarkRead={() => onItemRead(article.id)}
              fillHeight
            />
          )}
          onViewableItemsChanged={({ viewableItems }) => {
            // Track horizontal position if needed
          }}
          viewabilityConfig={{ itemVisiblePercentThreshold: 50 }}
        />
      </View>
    ),
    [domains.length, themeMode, onItemPress, onItemRead, styles]
  );

  return (
    <View style={styles.container}>
      <FlatList
        ref={flatListRef}
        data={domains}
        vertical
        pagingEnabled
        showsVerticalScrollIndicator={false}
        keyExtractor={(item) => item.domainId}
        renderItem={renderDomain}
        onViewableItemsChanged={onViewableItemsChanged}
        viewabilityConfig={viewabilityConfig}
        snapToInterval={DOMAIN_HEIGHT}
        decelerationRate="fast"
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
    domainContainer: {
      height: DOMAIN_HEIGHT,
      paddingHorizontal: theme.space.lg
    },
    domainHeader: {
      flexDirection: 'row',
      justifyContent: 'space-between',
      alignItems: 'center',
      paddingVertical: theme.space.md
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
