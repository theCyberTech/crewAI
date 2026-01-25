import React from 'react';
import { Box, Text } from 'ink';
import type { Task } from '../types/index.js';

interface TaskCardProps {
  task: Task;
  index?: number;
  isSelected?: boolean;
  showDetails?: boolean;
  status?: 'pending' | 'running' | 'completed' | 'failed';
}

export function TaskCard({
  task,
  index,
  isSelected = false,
  showDetails = false,
  status = 'pending',
}: TaskCardProps) {
  const statusColors = {
    pending: 'gray',
    running: 'yellow',
    completed: 'green',
    failed: 'red',
  } as const;

  const statusIcons = {
    pending: '○',
    running: '◐',
    completed: '●',
    failed: '✗',
  };

  return (
    <Box
      flexDirection="column"
      borderStyle={isSelected ? 'double' : 'single'}
      borderColor={isSelected ? 'cyan' : statusColors[status]}
      paddingX={1}
      marginBottom={1}
    >
      <Box gap={1} alignItems="center">
        <Text color={statusColors[status]}>{statusIcons[status]}</Text>
        {index !== undefined && (
          <Text dimColor>#{index + 1}</Text>
        )}
        <Text bold color={isSelected ? 'cyan' : 'white'}>
          {task.id}
        </Text>
        {task.asyncExecution && (
          <Text color="magenta">[async]</Text>
        )}
      </Box>

      <Box marginTop={1}>
        <Text wrap="wrap">{task.description}</Text>
      </Box>

      <Box marginTop={1}>
        <Text color="yellow">Agent: </Text>
        <Text>{task.agent}</Text>
      </Box>

      {showDetails && (
        <>
          <Box marginTop={1}>
            <Text color="green">Expected Output: </Text>
            <Text dimColor wrap="wrap">{task.expectedOutput}</Text>
          </Box>

          {task.tools && task.tools.length > 0 && (
            <Box marginTop={1}>
              <Text color="blue">Tools: </Text>
              <Text>{task.tools.join(', ')}</Text>
            </Box>
          )}

          {task.context && task.context.length > 0 && (
            <Box marginTop={1}>
              <Text color="magenta">Context: </Text>
              <Text dimColor>{task.context.join(', ')}</Text>
            </Box>
          )}

          {task.outputFile && (
            <Box marginTop={1}>
              <Text dimColor>Output File: </Text>
              <Text>{task.outputFile}</Text>
            </Box>
          )}
        </>
      )}
    </Box>
  );
}

interface TaskListProps {
  tasks: Task[];
  selectedIndex?: number;
  taskStatuses?: Map<string, 'pending' | 'running' | 'completed' | 'failed'>;
  onSelect?: (task: Task) => void;
}

export function TaskList({ tasks, selectedIndex, taskStatuses, onSelect }: TaskListProps) {
  if (tasks.length === 0) {
    return (
      <Box>
        <Text dimColor>No tasks configured</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column">
      {tasks.map((task, index) => (
        <TaskCard
          key={task.id}
          task={task}
          index={index}
          isSelected={selectedIndex === index}
          showDetails={selectedIndex === index}
          status={taskStatuses?.get(task.id) || 'pending'}
        />
      ))}
    </Box>
  );
}

interface TaskTimelineProps {
  tasks: Task[];
  currentTaskIndex?: number;
  taskStatuses?: Map<string, 'pending' | 'running' | 'completed' | 'failed'>;
}

export function TaskTimeline({ tasks, currentTaskIndex = -1, taskStatuses }: TaskTimelineProps) {
  return (
    <Box flexDirection="column">
      {tasks.map((task, index) => {
        const status = taskStatuses?.get(task.id) || (
          index < currentTaskIndex ? 'completed' :
          index === currentTaskIndex ? 'running' :
          'pending'
        );

        const statusColors = {
          pending: 'gray',
          running: 'yellow',
          completed: 'green',
          failed: 'red',
        } as const;

        return (
          <Box key={task.id} flexDirection="row" gap={1}>
            <Box width={2}>
              <Text color={statusColors[status]}>
                {status === 'completed' ? '✓' :
                 status === 'running' ? '►' :
                 status === 'failed' ? '✗' : '○'}
              </Text>
            </Box>
            <Box width={3}>
              <Text dimColor>#{index + 1}</Text>
            </Box>
            <Text color={status === 'running' ? 'yellow' : 'white'}>
              {task.id}
            </Text>
            {index < tasks.length - 1 && (
              <Box marginLeft={2}>
                <Text dimColor>→</Text>
              </Box>
            )}
          </Box>
        );
      })}
    </Box>
  );
}
