import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar } from '../components/StatusBar.js';
import { useStore } from '../hooks/useStore.js';

interface SettingItem {
  key: keyof ReturnType<typeof useStore>['settings'];
  label: string;
  description: string;
  type: 'boolean' | 'string' | 'number' | 'select';
  options?: string[];
}

const SETTINGS: SettingItem[] = [
  {
    key: 'theme',
    label: 'Theme',
    description: 'Color theme for the TUI',
    type: 'select',
    options: ['dark', 'light'],
  },
  {
    key: 'verbose',
    label: 'Verbose Output',
    description: 'Show detailed execution logs',
    type: 'boolean',
  },
  {
    key: 'showTokenUsage',
    label: 'Show Token Usage',
    description: 'Display token usage statistics',
    type: 'boolean',
  },
  {
    key: 'maxHistoryEvents',
    label: 'Max History Events',
    description: 'Maximum number of events to keep in history',
    type: 'number',
  },
];

export function SettingsScreen() {
  const { goBack, settings, updateSettings } = useStore();
  const [selectedIndex, setSelectedIndex] = useState(0);

  useInput((input, key) => {
    if (key.escape) {
      goBack();
    } else if (key.upArrow) {
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : SETTINGS.length - 1));
    } else if (key.downArrow) {
      setSelectedIndex((prev) => (prev < SETTINGS.length - 1 ? prev + 1 : 0));
    } else if (key.return || input === ' ') {
      const setting = SETTINGS[selectedIndex];
      if (!setting) return;

      if (setting.type === 'boolean') {
        updateSettings({
          [setting.key]: !settings[setting.key],
        });
      } else if (setting.type === 'select' && setting.options) {
        const currentValue = settings[setting.key] as string;
        const currentIdx = setting.options.indexOf(currentValue);
        const nextIdx = (currentIdx + 1) % setting.options.length;
        updateSettings({
          [setting.key]: setting.options[nextIdx],
        });
      }
    } else if (key.leftArrow || key.rightArrow) {
      const setting = SETTINGS[selectedIndex];
      if (!setting) return;

      if (setting.type === 'number') {
        const currentValue = settings[setting.key] as number;
        const delta = key.leftArrow ? -100 : 100;
        updateSettings({
          [setting.key]: Math.max(100, currentValue + delta),
        });
      } else if (setting.type === 'select' && setting.options) {
        const currentValue = settings[setting.key] as string;
        const currentIdx = setting.options.indexOf(currentValue);
        const delta = key.leftArrow ? -1 : 1;
        const nextIdx = (currentIdx + delta + setting.options.length) % setting.options.length;
        updateSettings({
          [setting.key]: setting.options[nextIdx],
        });
      }
    }
  });

  return (
    <Box flexDirection="column" padding={1}>
      <Header subtitle="Settings" />
      <Breadcrumb items={['Home', 'Settings']} />

      <Box flexDirection="column" marginTop={1}>
        <Text bold color="cyan">⚙️ Settings</Text>
        <Text dimColor>Use ↑↓ to navigate, Enter/Space to toggle, ←→ to adjust values</Text>

        <Box flexDirection="column" marginTop={1}>
          {SETTINGS.map((setting, index) => (
            <SettingRow
              key={setting.key}
              setting={setting}
              value={settings[setting.key]}
              isSelected={index === selectedIndex}
            />
          ))}
        </Box>
      </Box>

      <StatusBar
        hints={[
          { key: '↑↓', action: 'Navigate' },
          { key: 'Enter', action: 'Toggle' },
          { key: '←→', action: 'Adjust' },
        ]}
      />
    </Box>
  );
}

interface SettingRowProps {
  setting: SettingItem;
  value: unknown;
  isSelected: boolean;
}

function SettingRow({ setting, value, isSelected }: SettingRowProps) {
  const renderValue = () => {
    if (setting.type === 'boolean') {
      return (
        <Text color={value ? 'green' : 'red'}>
          {value ? '● Enabled' : '○ Disabled'}
        </Text>
      );
    } else if (setting.type === 'select') {
      return (
        <Box gap={1}>
          <Text color="gray">{'<'}</Text>
          <Text color="cyan">{String(value)}</Text>
          <Text color="gray">{'>'}</Text>
        </Box>
      );
    } else if (setting.type === 'number') {
      return (
        <Box gap={1}>
          <Text color="gray">{'<'}</Text>
          <Text color="yellow">{String(value)}</Text>
          <Text color="gray">{'>'}</Text>
        </Box>
      );
    }
    return <Text>{String(value)}</Text>;
  };

  return (
    <Box
      borderStyle={isSelected ? 'double' : 'single'}
      borderColor={isSelected ? 'cyan' : 'gray'}
      paddingX={1}
      marginBottom={1}
      flexDirection="column"
    >
      <Box justifyContent="space-between" alignItems="center">
        <Box gap={1}>
          <Text color={isSelected ? 'cyan' : 'white'}>
            {isSelected ? '❯' : ' '}
          </Text>
          <Text bold color={isSelected ? 'cyan' : 'white'}>
            {setting.label}
          </Text>
        </Box>
        {renderValue()}
      </Box>
      <Box marginLeft={3}>
        <Text dimColor>{setting.description}</Text>
      </Box>
    </Box>
  );
}
