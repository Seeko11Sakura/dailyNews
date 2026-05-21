import { Tabs } from 'expo-router';
import { AppDock } from '../../src/components/AppDock';

export default function TabsLayout() {
  return (
    <Tabs
      screenOptions={{
        headerShown: false,
        tabBarShowLabel: false
      }}
      tabBar={(props) => <AppDock {...props} />}
    >
      <Tabs.Screen name="today" options={{ title: '今日' }} />
      <Tabs.Screen name="explore" options={{ title: '抽卡' }} />
      <Tabs.Screen name="favorites" options={{ title: '收藏' }} />
    </Tabs>
  );
}
