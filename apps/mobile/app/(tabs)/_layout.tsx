import { Tabs } from 'expo-router';

export default function TabsLayout() {
  return (
    <Tabs screenOptions={{ headerShown: false }}>
      <Tabs.Screen name="today" options={{ title: '今日' }} />
      <Tabs.Screen name="explore" options={{ title: '抽卡' }} />
      <Tabs.Screen name="favorites" options={{ title: '收藏' }} />
    </Tabs>
  );
}
