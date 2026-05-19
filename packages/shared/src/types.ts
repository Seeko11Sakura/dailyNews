export type DomainId =
  | 'technology'
  | 'ai'
  | 'gadgets'
  | 'business'
  | 'finance'
  | 'career'
  | 'education'
  | 'games'
  | 'media'
  | 'health'
  | 'society'
  | 'lifestyle';

export interface Domain {
  id: DomainId;
  name: string;
  emoji: string;
}
