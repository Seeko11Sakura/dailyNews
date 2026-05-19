import { Pressable, Text, View } from 'react-native';
import type { DigestListItem } from '../../store/app-store';

type ArticleCardProps = {
  item: DigestListItem;
  onOpen: (item: DigestListItem) => void;
};

export function ArticleCard({ item, onOpen }: ArticleCardProps) {
  return (
    <View>
      <Text>{item.title}</Text>
      <Text>{item.summary}</Text>
      <Text>{`${item.source} · ${item.publishedAt}`}</Text>
      <Text>{item.isRead ? '已读' : '未读'}</Text>
      <Pressable onPress={() => onOpen(item)} accessibilityRole="button">
        <Text>阅读全文</Text>
      </Pressable>
    </View>
  );
}
