export const tokens = {
  color: {
    primary: '#1296db',
    primaryDark: '#0d76ae',
    primarySoft: 'rgba(18,150,219,0.12)',
    glow: 'rgba(18,150,219,0.24)',
    background: '#f5faff',
    backgroundAlt: '#e8f4ff',
    surface: 'rgba(255,255,255,0.82)',
    surfaceStrong: 'rgba(255,255,255,0.94)',
    surfaceInner: 'rgba(255,255,255,0.58)',
    border: 'rgba(255,255,255,0.92)',
    text: '#2a313c',
    muted: '#7a8599',
    faint: 'rgba(122,133,153,0.18)',
    white: '#ffffff'
  },
  radius: {
    xl: 32,
    lg: 24,
    md: 16,
    sm: 8,
    pill: 999
  },
  space: {
    xs: 6,
    sm: 10,
    md: 16,
    lg: 20,
    xl: 24,
    xxl: 32
  },
  shadow: {
    glass: {
      shadowColor: '#1296db',
      shadowOpacity: 0.12,
      shadowRadius: 24,
      shadowOffset: { width: 0, height: 12 },
      elevation: 5
    },
    primary: {
      shadowColor: '#1296db',
      shadowOpacity: 0.28,
      shadowRadius: 20,
      shadowOffset: { width: 0, height: 10 },
      elevation: 6
    }
  }
} as const;

export type ThemeMode = 'light' | 'dark';

export const themes = {
  light: tokens,
  dark: {
    ...tokens,
    color: {
      ...tokens.color,
      primary: '#2ab0f5',
      primaryDark: '#78d4ff',
      primarySoft: 'rgba(42,176,245,0.16)',
      glow: 'rgba(42,176,245,0.22)',
      background: '#10141a',
      backgroundAlt: '#121822',
      surface: 'rgba(30,35,45,0.76)',
      surfaceStrong: 'rgba(25,30,40,0.94)',
      surfaceInner: 'rgba(0,0,0,0.24)',
      border: 'rgba(255,255,255,0.1)',
      text: '#f0f4f8',
      muted: '#a7b2c4',
      faint: 'rgba(167,178,196,0.18)',
      white: '#ffffff'
    },
    shadow: {
      glass: {
        shadowColor: '#000000',
        shadowOpacity: 0.34,
        shadowRadius: 28,
        shadowOffset: { width: 0, height: 14 },
        elevation: 6
      },
      primary: {
        shadowColor: '#2ab0f5',
        shadowOpacity: 0.22,
        shadowRadius: 22,
        shadowOffset: { width: 0, height: 10 },
        elevation: 6
      }
    }
  }
} as const;

export function getTheme(mode: ThemeMode) {
  return themes[mode];
}
