import { StyleSheet, View } from 'react-native';
import { AnimatedPressable } from './AnimatedPressable';
import { useAppStore } from '../store/app-store';
import { getTheme } from '../theme/tokens';

type DockRoute = {
  key: string;
  name: string;
  params?: object;
};

type DockProps = {
  state: {
    index: number;
    routes: DockRoute[];
  };
  descriptors: Record<string, { options?: { title?: string } } | undefined>;
  navigation: {
    emit: (event: {
      type: 'tabPress';
      target: string;
      canPreventDefault: true;
    }) => { defaultPrevented?: boolean };
    navigate: (name: string, params?: object) => void;
  };
};

export function AppDock({ state, descriptors, navigation }: DockProps) {
  const themeMode = useAppStore((value) => value.themeMode);
  const isReaderOpen = useAppStore((value) => value.isReaderOpen);
  const theme = getTheme(themeMode);
  const styles = createStyles(theme);

  if (isReaderOpen) {
    return null;
  }

  return (
    <View style={styles.safeArea}>
      <View style={styles.dock}>
        {state.routes.map((route, index) => {
          const focused = state.index === index;
          const options = descriptors[route.key]?.options;
          const label =
            typeof options?.title === 'string' ? options.title : route.name;

          return (
            <AnimatedPressable
              key={route.key}
              accessibilityRole="button"
              accessibilityLabel={label}
              accessibilityState={{ selected: focused }}
              onPress={() => {
                const event = navigation.emit({
                  type: 'tabPress',
                  target: route.key,
                  canPreventDefault: true
                });

                if (!focused && !event.defaultPrevented) {
                  navigation.navigate(route.name, route.params);
                }
              }}
              style={[styles.item, focused ? styles.activeItem : null]}
              pressedStyle={styles.pressed}
            >
              <DockIcon name={route.name} active={focused} />
            </AnimatedPressable>
          );
        })}
      </View>
    </View>
  );
}

function DockIcon({ name, active }: { name: string; active: boolean }) {
  if (name === 'today') {
    return <NewsIcon active={active} />;
  }

  if (name === 'favorites') {
    return <WandIcon active={active} />;
  }

  return <CrystalIcon active={active} />;
}

function NewsIcon({ active }: { active: boolean }) {
  const ink = active ? '#8d90a1' : '#aeb7ca';
  return (
    <View style={[iconStyles.newsPage, { borderColor: ink }]}>
      <View style={[iconStyles.newsHeader, { backgroundColor: ink }]} />
      <View style={iconStyles.newsRows}>
        <View style={[iconStyles.newsRow, { backgroundColor: ink }]} />
        <View style={[iconStyles.newsRow, { backgroundColor: ink }]} />
        <View style={[iconStyles.newsRowShort, { backgroundColor: ink }]} />
      </View>
    </View>
  );
}

function CrystalIcon({ active }: { active: boolean }) {
  const main = active ? '#b58cff' : '#9a7ad8';
  const accent = active ? '#ffd365' : '#c8a84e';
  return (
    <View style={iconStyles.crystalWrap}>
      <View style={[iconStyles.crystalOrb, { backgroundColor: main }]}>
        <View style={[iconStyles.crystalSpark, { backgroundColor: accent }]} />
      </View>
      <View style={[iconStyles.crystalStem, { backgroundColor: '#d8c6a5' }]} />
      <View style={[iconStyles.crystalBase, { backgroundColor: '#d8c6a5' }]} />
    </View>
  );
}

function WandIcon({ active }: { active: boolean }) {
  const red = active ? '#ff3f42' : '#ff595c';
  const gold = active ? '#ffd365' : '#dcb85a';
  return (
    <View style={iconStyles.wandWrap}>
      <View style={[iconStyles.wand, { backgroundColor: red }]} />
      <View style={[iconStyles.wandTip, { backgroundColor: gold }]} />
      <View style={[iconStyles.starLarge, { borderBottomColor: red }]} />
      <View style={[iconStyles.starSmall, { backgroundColor: gold }]} />
    </View>
  );
}

function createStyles(theme: ReturnType<typeof getTheme>) {
  return StyleSheet.create({
    safeArea: {
      minHeight: 96,
      paddingHorizontal: 20,
      paddingTop: 8,
      paddingBottom: 18,
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: theme.color.background
    },
    dock: {
      width: '100%',
      maxWidth: 334,
      height: 70,
      paddingHorizontal: 28,
      flexDirection: 'row',
      alignItems: 'center',
      justifyContent: 'space-between',
      borderRadius: 23,
      backgroundColor:
        theme === getTheme('dark') ? 'rgba(20,26,36,0.92)' : theme.color.surfaceStrong,
      borderWidth: 1,
      borderColor: theme.color.border,
      ...theme.shadow.glass
    },
    item: {
      width: 54,
      height: 54,
      alignItems: 'center',
      justifyContent: 'center',
      borderRadius: 27
    },
    activeItem: {
      backgroundColor: theme.color.primary,
      shadowColor: theme.color.primary,
      shadowOpacity: 0.32,
      shadowRadius: 22,
      shadowOffset: { width: 0, height: 12 },
      elevation: 7
    },
    pressed: {
      opacity: 0.82
    }
  });
}

const iconStyles = StyleSheet.create({
  newsPage: {
    width: 23,
    height: 20,
    borderRadius: 2,
    borderWidth: 2,
    backgroundColor: '#f2edf3',
    padding: 3
  },
  newsHeader: {
    width: 6,
    height: 11,
    borderRadius: 1,
    position: 'absolute',
    left: 4,
    top: 5
  },
  newsRows: {
    marginLeft: 8,
    gap: 2
  },
  newsRow: {
    width: 8,
    height: 2,
    borderRadius: 2
  },
  newsRowShort: {
    width: 6,
    height: 2,
    borderRadius: 2
  },
  crystalWrap: {
    width: 28,
    height: 30,
    alignItems: 'center',
    justifyContent: 'center'
  },
  crystalOrb: {
    width: 18,
    height: 18,
    borderTopLeftRadius: 10,
    borderTopRightRadius: 10,
    borderBottomLeftRadius: 4,
    borderBottomRightRadius: 4
  },
  crystalSpark: {
    width: 4,
    height: 4,
    borderRadius: 2,
    marginLeft: 3,
    marginTop: 4
  },
  crystalStem: {
    width: 4,
    height: 5
  },
  crystalBase: {
    width: 14,
    height: 3,
    borderRadius: 2
  },
  wandWrap: {
    width: 28,
    height: 28
  },
  wand: {
    position: 'absolute',
    width: 22,
    height: 6,
    borderRadius: 3,
    left: 3,
    top: 12,
    transform: [{ rotate: '-42deg' }]
  },
  wandTip: {
    position: 'absolute',
    width: 4,
    height: 6,
    borderRadius: 2,
    left: 7,
    top: 15,
    transform: [{ rotate: '-42deg' }]
  },
  starLarge: {
    position: 'absolute',
    left: 17,
    top: 3,
    width: 0,
    height: 0,
    borderLeftWidth: 4,
    borderRightWidth: 4,
    borderBottomWidth: 8,
    borderLeftColor: 'transparent',
    borderRightColor: 'transparent',
    transform: [{ rotate: '32deg' }]
  },
  starSmall: {
    position: 'absolute',
    width: 4,
    height: 4,
    borderRadius: 2,
    left: 2,
    top: 7
  }
});
