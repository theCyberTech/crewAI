import React from 'react';
import { Box, Text } from 'ink';
import Spinner from 'ink-spinner';
import { useStore } from '../hooks/useStore.js';

interface KeyHint {
  key: string;
  action: string;
}

interface StatusBarProps {
  hints?: KeyHint[];
  status?: string;
}

export function StatusBar({ hints = [], status }: StatusBarProps) {
  const { isExecuting, selectedProject } = useStore();

  const defaultHints: KeyHint[] = [
    { key: 'q', action: 'Quit' },
    { key: 'h', action: 'Help' },
    { key: 'Esc', action: 'Back' },
  ];

  const allHints = [...hints, ...defaultHints];

  return (
    <Box
      flexDirection="row"
      justifyContent="space-between"
      alignItems="center"
      paddingX={1}
      borderStyle="single"
      borderColor="gray"
      marginTop={1}
    >
      <Box gap={2}>
        {allHints.map((hint, index) => (
          <Box key={index} gap={1}>
            <Text backgroundColor="gray" color="black">
              {' '}{hint.key}{' '}
            </Text>
            <Text dimColor>{hint.action}</Text>
          </Box>
        ))}
      </Box>

      <Box gap={2}>
        {isExecuting && (
          <Box gap={1}>
            <Text color="yellow">
              <Spinner type="dots" />
            </Text>
            <Text color="yellow">Running</Text>
          </Box>
        )}
        {selectedProject && (
          <Text color="cyan">{selectedProject.name}</Text>
        )}
        {status && (
          <Text dimColor>{status}</Text>
        )}
      </Box>
    </Box>
  );
}

interface ProgressBarProps {
  value: number;
  total: number;
  width?: number;
  showPercentage?: boolean;
  color?: string;
}

export function ProgressBar({
  value,
  total,
  width = 30,
  showPercentage = true,
  color = 'cyan',
}: ProgressBarProps) {
  const percentage = Math.round((value / total) * 100);
  const filled = Math.round((value / total) * width);
  const empty = width - filled;

  return (
    <Box gap={1}>
      <Text color={color}>
        {'█'.repeat(filled)}
        {'░'.repeat(empty)}
      </Text>
      {showPercentage && (
        <Text dimColor>{percentage}%</Text>
      )}
    </Box>
  );
}

interface LoadingIndicatorProps {
  text?: string;
}

export function LoadingIndicator({ text = 'Loading...' }: LoadingIndicatorProps) {
  return (
    <Box gap={1}>
      <Text color="cyan">
        <Spinner type="dots" />
      </Text>
      <Text>{text}</Text>
    </Box>
  );
}
