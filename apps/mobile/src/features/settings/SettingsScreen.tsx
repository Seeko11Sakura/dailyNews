import { Pressable, Text, View } from 'react-native';
import type { AppStore } from '../../store/app-store';
import { useAppStore } from '../../store/app-store';

type SettingsScreenProps = {
  store?: AppStore;
};

export function SettingsScreen({ store }: SettingsScreenProps) {
  const themeMode = useAppStore((state) => state.themeMode, store);
  const clearCache = useAppStore((state) => state.clearCache, store);

  return (
    <View>
      <Text>设置</Text>
      <Text>{`主题模式`}</Text>
      <Text>{themeMode === 'dark' ? '深色' : '浅色'}</Text>
      <Pressable onPress={() => void clearCache()} accessibilityRole="button">
        <Text>清除缓存</Text>
      </Pressable>
    </View>
  );
}
