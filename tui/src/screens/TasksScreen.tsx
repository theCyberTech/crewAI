import React, { useState, useEffect } from 'react';
import { Box, Text, useInput } from 'ink';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar } from '../components/StatusBar.js';
import { TaskCard } from '../components/TaskCard.js';
import { useStore } from '../hooks/useStore.js';
import { loadTasksConfig } from '../utils/crewai.js';
import type { Task } from '../types/index.js';

export function TasksScreen() {
  const { goBack, selectedProject } = useStore();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    if (selectedProject?.config?.tasks) {
      const loaded = loadTasksConfig(selectedProject.config.tasks);
      setTasks(loaded);
    }
  }, [selectedProject]);

  useInput((input, key) => {
    if (key.escape) {
      goBack();
    } else if (key.upArrow) {
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : tasks.length - 1));
    } else if (key.downArrow) {
      setSelectedIndex((prev) => (prev < tasks.length - 1 ? prev + 1 : 0));
    }
  });

  if (!selectedProject) {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle="Tasks" />
        <Text color="red">No project selected. Please select a crew first.</Text>
        <StatusBar />
      </Box>
    );
  }

  return (
    <Box flexDirection="column" padding={1}>
      <Header subtitle="Tasks" />
      <Breadcrumb items={['Home', selectedProject.name, 'Tasks']} />

      {tasks.length === 0 ? (
        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor="yellow"
          paddingX={2}
          paddingY={1}
          marginTop={1}
        >
          <Text color="yellow">No tasks found in this project.</Text>
          <Box marginTop={1}>
            <Text dimColor>Check your tasks.yaml configuration file.</Text>
          </Box>
        </Box>
      ) : (
        <Box flexDirection="column" marginTop={1}>
          <Text bold color="yellow">
            📋 Tasks ({tasks.length})
          </Text>
          <Text dimColor>Use ↑↓ to navigate and view details</Text>

          <Box flexDirection="column" marginTop={1}>
            {tasks.map((task, index) => (
              <TaskCard
                key={task.id}
                task={task}
                index={index}
                isSelected={index === selectedIndex}
                showDetails={index === selectedIndex}
              />
            ))}
          </Box>
        </Box>
      )}

      <StatusBar
        hints={[
          { key: '↑↓', action: 'Navigate' },
        ]}
      />
    </Box>
  );
}
