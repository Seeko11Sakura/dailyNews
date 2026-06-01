import { render, screen } from '@testing-library/react';
import { AppDock } from '../components/AppDock';
import { appStore } from '../store/app-store';

const props = {
  state: {
    index: 0,
    routes: [
      { key: 'today-key', name: 'today' },
      { key: 'explore-key', name: 'explore' },
      { key: 'favorites-key', name: 'favorites' }
    ]
  },
  descriptors: {
    'today-key': { options: { title: '今日' } },
    'explore-key': { options: { title: '抽卡' } },
    'favorites-key': { options: { title: '收藏' } }
  },
  navigation: {
    emit: () => ({}),
    navigate: () => undefined
  }
};

it('hides dock while reader is open', () => {
  appStore.setState({ isReaderOpen: true });

  render(<AppDock {...props} />);

  expect(screen.queryByLabelText('今日')).toBeNull();
});
