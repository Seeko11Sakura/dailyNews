import { useEffect, useState } from 'react';
import { Pressable, Text, View } from 'react-native';
import { fetchItemDetail, type ArticleDetail } from '../../services/api';

type ReaderModalProps = {
  visible: boolean;
  itemId: string | null;
  onClose: () => void;
};

export function ReaderModal({ visible, itemId, onClose }: ReaderModalProps) {
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

  return (
    <View accessibilityRole="dialog">
      <Pressable onPress={onClose} accessibilityRole="button">
        <Text>关闭阅读</Text>
      </Pressable>
      {isLoading ? <Text>加载中...</Text> : null}
      {error ? <Text>{error}</Text> : null}
      {article ? (
        <View>
          <Text>{article.title}</Text>
          <Text>{article.summary}</Text>
          <Text>{article.content}</Text>
        </View>
      ) : null}
    </View>
  );
}
