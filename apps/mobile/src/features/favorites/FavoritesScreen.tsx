import { Text, TextInput, View } from 'react-native';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';

type FavoritesScreenProps = {
  store?: AppStore;
};

export function FavoritesScreen({ store }: FavoritesScreenProps) {
  const favoriteIds = useAppStore((state) => state.favoriteIds, store);

  return (
    <View>
      <TextInput placeholder="搜索标题或来源" />
      <Text>收藏列表</Text>
      <Text>{`已收藏 ${favoriteIds.length} 条`}</Text>
      {favoriteIds.length === 0 ? <Text>暂无收藏内容</Text> : null}
    </View>
  );
}
