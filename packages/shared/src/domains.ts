import type { Domain, DomainId } from './types';

export const domains: Domain[] = [
  { id: 'technology', name: '科技与互联网', emoji: '💻' },
  { id: 'ai', name: '人工智能', emoji: '🤖' },
  { id: 'gadgets', name: '手机数码', emoji: '📱' },
  { id: 'business', name: '商业与公司', emoji: '💼' },
  { id: 'finance', name: '财经与宏观', emoji: '📈' },
  { id: 'career', name: '职场与效率', emoji: '🚀' },
  { id: 'education', name: '教育与学习', emoji: '📚' },
  { id: 'games', name: '游戏', emoji: '🎮' },
  { id: 'media', name: '影视与流媒体', emoji: '🎬' },
  { id: 'health', name: '健康与心理', emoji: '🧠' },
  { id: 'society', name: '社会与热点', emoji: '🌍' },
  { id: 'lifestyle', name: '生活方式', emoji: '☕' }
];

export const edgeMap: Record<DomainId, DomainId[]> = {
  technology: ['ai', 'gadgets', 'business', 'career', 'media'],
  ai: ['technology', 'business', 'education', 'career', 'health'],
  gadgets: ['technology', 'ai', 'media', 'lifestyle', 'games'],
  business: ['technology', 'ai', 'finance', 'career', 'society'],
  finance: ['business', 'technology', 'society', 'career', 'lifestyle'],
  career: ['business', 'ai', 'education', 'finance', 'technology'],
  education: ['ai', 'career', 'society', 'technology', 'health'],
  games: ['media', 'technology', 'gadgets', 'lifestyle', 'ai'],
  media: ['technology', 'games', 'society', 'lifestyle', 'gadgets'],
  health: ['ai', 'lifestyle', 'education', 'society', 'technology'],
  society: ['business', 'media', 'education', 'finance', 'health'],
  lifestyle: ['health', 'media', 'gadgets', 'finance', 'games']
};
