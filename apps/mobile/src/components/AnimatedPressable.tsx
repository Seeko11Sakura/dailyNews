import { useRef } from 'react';
import {
  Animated,
  Pressable,
  type PressableProps,
  type StyleProp,
  type ViewStyle
} from 'react-native';

type AnimatedPressableProps = PressableProps & {
  children: React.ReactNode;
  style?: StyleProp<ViewStyle>;
  pressedStyle?: StyleProp<ViewStyle>;
};

export function AnimatedPressable({
  children,
  onPressIn,
  onPressOut,
  style,
  pressedStyle,
  ...props
}: AnimatedPressableProps) {
  const scale = useRef(new Animated.Value(1)).current;

  function animate(toValue: number) {
    Animated.spring(scale, {
      toValue,
      useNativeDriver: true,
      speed: 28,
      bounciness: 5
    }).start();
  }

  return (
    <Pressable
      {...props}
      onPressIn={(event) => {
        animate(0.96);
        onPressIn?.(event);
      }}
      onPressOut={(event) => {
        animate(1);
        onPressOut?.(event);
      }}
    >
      {({ pressed }) => (
        <Animated.View
          style={[
            style,
            pressed ? pressedStyle : null,
            {
              transform: [{ scale }]
            }
          ]}
        >
          {typeof children === 'function' ? children({ pressed }) : children}
        </Animated.View>
      )}
    </Pressable>
  );
}
