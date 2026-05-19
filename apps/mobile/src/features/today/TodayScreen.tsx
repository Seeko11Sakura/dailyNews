import { useEffect, useMemo, useState } from 'react';
import { ScrollView, Text, View } from 'react-native';
import type { DomainId } from '@dailynews/shared';
import { fetchTodayDigest } from '../../services/api';
import type { AppStore, DigestGroup, DigestListItem } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';
import { ReaderModal } from '../reader/ReaderModal';
import { ArticleCard } from './ArticleCard';

type TodayScreenProps = {
  store?: AppStore;
};

function mapDigestGroups(
  groups: Array<{
    domain_id: string;
    items: Array<{
      id: string;
      domain_id: string;
      title: string;
      summary: string;
      source: string;
      published_at: string;
      is_read: boolean;
    }>;
  }>
): DigestGroup[] {
  return groups.map((group) => ({
    domainId: group.domain_id as DomainId,
    items: group.items.map((item) => ({
      id: item.id,
      domainId: item.domain_id as DomainId,
      title: item.title,
      summary: item.summary,
      source: item.source,
      publishedAt: item.published_at,
      isRead: item.is_read
    }))
  }));
}

function countTotalItems(groups: DigestGroup[]) {
  return groups.reduce((total, group) => total + group.items.length, 0);
}

export function TodayScreen({ store }: TodayScreenProps) {
  const selectedDomains = useAppStore((state) => state.selectedDomains, store);
  const digestGroups = useAppStore((state) => state.digestGroups, store);
  const readCount = useAppStore((state) => state.readCount, store);
  const setDigest = useAppStore((state) => state.setDigest, store);
  const markItemRead = useAppStore((state) => state.markItemRead, store);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeItemId, setActiveItemId] = useState<string | null>(null);

  useEffect(() => {
    if (selectedDomains.length === 0) {
      return;
    }

    setIsLoading(true);
    setError(null);

    void fetchTodayDigest(selectedDomains)
      .then((payload) => {
        setDigest(mapDigestGroups(payload.groups));
      })
      .catch(() => {
        setError('今日简报加载失败');
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [selectedDomains, setDigest]);

  const totalCount = useMemo(() => countTotalItems(digestGroups), [digestGroups]);

  function handleOpen(item: DigestListItem) {
    markItemRead(item.id);
    setActiveItemId(item.id);
  }

  return (
    <View>
      <Text>今日简报</Text>
      <Text>{`已读 ${readCount}/${totalCount}`}</Text>
      {selectedDomains.length === 0 ? <Text>请先完成兴趣选择</Text> : null}
      {isLoading ? <Text>加载中...</Text> : null}
      {error ? <Text>{error}</Text> : null}
      <ScrollView>
        {digestGroups.map((group) => (
          <View key={group.domainId}>
            <Text>{group.domainId}</Text>
            {group.items.map((item) => (
              <ArticleCard key={item.id} item={item} onOpen={handleOpen} />
            ))}
          </View>
        ))}
      </ScrollView>
      <ReaderModal
        visible={activeItemId !== null}
        itemId={activeItemId}
        onClose={() => setActiveItemId(null)}
      />
    </View>
  );
}
