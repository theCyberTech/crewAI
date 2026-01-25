import React, { useEffect } from 'react';
import { Box, Text, useApp, useInput } from 'ink';
import { useStore } from './hooks/useStore.js';
import {
  HomeScreen,
  CrewsScreen,
  CrewRunScreen,
  FlowsScreen,
  ChatScreen,
  AgentsScreen,
  TasksScreen,
  HelpScreen,
  SettingsScreen,
  MemoryScreen,
} from './screens/index.js';
import type { Screen } from './types/index.js';

interface AppProps {
  initialScreen?: Screen;
  projectPath?: string;
}

export function App({ initialScreen = 'home', projectPath }: AppProps) {
  const { currentScreen, navigate } = useStore();
  const { exit } = useApp();

  useEffect(() => {
    if (initialScreen !== 'home') {
      navigate(initialScreen);
    }
  }, [initialScreen, navigate]);

  useInput((input, key) => {
    // Global quit shortcut
    if (input === 'q' && currentScreen === 'home') {
      exit();
    }
  });

  const renderScreen = () => {
    switch (currentScreen) {
      case 'home':
        return <HomeScreen />;
      case 'crews':
        return <CrewsScreen />;
      case 'crew-run':
        return <CrewRunScreen />;
      case 'flows':
        return <FlowsScreen />;
      case 'chat':
        return <ChatScreen />;
      case 'agents':
        return <AgentsScreen />;
      case 'tasks':
        return <TasksScreen />;
      case 'help':
        return <HelpScreen />;
      case 'settings':
        return <SettingsScreen />;
      case 'memory':
        return <MemoryScreen />;
      default:
        return <HomeScreen />;
    }
  };

  return (
    <Box flexDirection="column" minHeight={20}>
      {renderScreen()}
    </Box>
  );
}

export function ErrorBoundary({ error }: { error: Error }) {
  return (
    <Box flexDirection="column" padding={2} borderStyle="round" borderColor="red">
      <Text bold color="red">
        ❌ An error occurred
      </Text>
      <Box marginTop={1}>
        <Text color="red">{error.message}</Text>
      </Box>
      <Box marginTop={1}>
        <Text dimColor>{error.stack}</Text>
      </Box>
      <Box marginTop={1}>
        <Text>Press Ctrl+C to exit</Text>
      </Box>
    </Box>
  );
}
