import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar } from '../components/StatusBar.js';
import { ConfirmDialog } from '../components/Input.js';
import { Tabs } from '../components/Menu.js';
import { useStore } from '../hooks/useStore.js';
import { resetMemories } from '../utils/crewai.js';

type MemoryType = 'short_term' | 'long_term' | 'entity' | 'all';

interface MemoryTypeInfo {
  key: MemoryType;
  label: string;
  icon: string;
  description: string;
  flag: string;
}

const MEMORY_TYPES: MemoryTypeInfo[] = [
  {
    key: 'short_term',
    label: 'Short-Term',
    icon: '⚡',
    description: 'Current execution context and recent interactions',
    flag: 's',
  },
  {
    key: 'long_term',
    label: 'Long-Term',
    icon: '📚',
    description: 'Persistent knowledge across executions',
    flag: 'l',
  },
  {
    key: 'entity',
    label: 'Entity',
    icon: '🏷️',
    description: 'Tracked entities and their relationships',
    flag: 'e',
  },
  {
    key: 'all',
    label: 'All Memories',
    icon: '🗑️',
    description: 'Clear all memory types at once',
    flag: 'a',
  },
];

export function MemoryScreen() {
  const { goBack, selectedProject } = useStore();
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [isClearing, setIsClearing] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [clearResult, setClearResult] = useState<{ success: boolean; message: string } | null>(null);

  useInput((input, key) => {
    if (showConfirm) return;

    if (key.escape) {
      if (clearResult) {
        setClearResult(null);
      } else {
        goBack();
      }
    } else if (key.upArrow) {
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : MEMORY_TYPES.length - 1));
    } else if (key.downArrow) {
      setSelectedIndex((prev) => (prev < MEMORY_TYPES.length - 1 ? prev + 1 : 0));
    } else if (key.return || input === 'd') {
      setShowConfirm(true);
    }
  });

  const handleClear = async () => {
    if (!selectedProject) return;

    setShowConfirm(false);
    setIsClearing(true);

    const memoryType = MEMORY_TYPES[selectedIndex];
    if (!memoryType) return;

    try {
      const result = await resetMemories(
        selectedProject.path,
        memoryType.key === 'all',
        memoryType.key !== 'all' ? [memoryType.key] : undefined
      );

      setClearResult({
        success: result.success,
        message: result.success
          ? `Successfully cleared ${memoryType.label.toLowerCase()} memory.`
          : result.stderr || 'Failed to clear memory.',
      });
    } catch (error) {
      setClearResult({
        success: false,
        message: error instanceof Error ? error.message : 'Unknown error',
      });
    } finally {
      setIsClearing(false);
    }
  };

  if (!selectedProject) {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle="Memory" />
        <Text color="red">No project selected. Please select a crew first.</Text>
        <StatusBar />
      </Box>
    );
  }

  return (
    <Box flexDirection="column" padding={1}>
      <Header subtitle="Memory Management" />
      <Breadcrumb items={['Home', selectedProject.name, 'Memory']} />

      {showConfirm && (
        <Box marginTop={1}>
          <ConfirmDialog
            message={`Are you sure you want to clear ${MEMORY_TYPES[selectedIndex]?.label.toLowerCase()} memory?`}
            onConfirm={handleClear}
            onCancel={() => setShowConfirm(false)}
            confirmLabel="Clear"
            cancelLabel="Cancel"
            isDangerous
          />
        </Box>
      )}

      {clearResult && (
        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor={clearResult.success ? 'green' : 'red'}
          paddingX={2}
          paddingY={1}
          marginTop={1}
        >
          <Text bold color={clearResult.success ? 'green' : 'red'}>
            {clearResult.success ? '✅ Success' : '❌ Error'}
          </Text>
          <Box marginTop={1}>
            <Text>{clearResult.message}</Text>
          </Box>
          <Box marginTop={1}>
            <Text dimColor>Press Esc to continue</Text>
          </Box>
        </Box>
      )}

      {isClearing && (
        <Box marginTop={1} gap={1}>
          <Text color="yellow">
            <Spinner type="dots" />
          </Text>
          <Text>Clearing memory...</Text>
        </Box>
      )}

      {!showConfirm && !clearResult && !isClearing && (
        <Box flexDirection="column" marginTop={1}>
          <Text bold color="cyan">🧠 Memory Management</Text>
          <Text dimColor>
            Manage crew memory storage. Select a memory type to clear.
          </Text>

          <Box
            flexDirection="column"
            borderStyle="round"
            borderColor="yellow"
            paddingX={2}
            paddingY={1}
            marginTop={1}
          >
            <Text color="yellow">⚠️ Warning</Text>
            <Text wrap="wrap">
              Clearing memory is irreversible. The crew will lose learned
              information and context from previous executions.
            </Text>
          </Box>

          <Box flexDirection="column" marginTop={1}>
            {MEMORY_TYPES.map((memType, index) => (
              <MemoryTypeRow
                key={memType.key}
                memoryType={memType}
                isSelected={index === selectedIndex}
              />
            ))}
          </Box>
        </Box>
      )}

      <StatusBar
        hints={[
          { key: '↑↓', action: 'Navigate' },
          { key: 'Enter', action: 'Clear Selected' },
          { key: 'd', action: 'Delete' },
        ]}
      />
    </Box>
  );
}

interface MemoryTypeRowProps {
  memoryType: MemoryTypeInfo;
  isSelected: boolean;
}

function MemoryTypeRow({ memoryType, isSelected }: MemoryTypeRowProps) {
  return (
    <Box
      borderStyle={isSelected ? 'double' : 'single'}
      borderColor={isSelected ? 'cyan' : 'gray'}
      paddingX={1}
      marginBottom={1}
      flexDirection="column"
    >
      <Box gap={1} alignItems="center">
        <Text color={isSelected ? 'cyan' : 'white'}>
          {isSelected ? '❯' : ' '}
        </Text>
        <Text>{memoryType.icon}</Text>
        <Text bold color={isSelected ? 'cyan' : 'white'}>
          {memoryType.label}
        </Text>
      </Box>
      <Box marginLeft={4}>
        <Text dimColor>{memoryType.description}</Text>
      </Box>
    </Box>
  );
}
