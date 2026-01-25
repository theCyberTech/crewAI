import React, { useEffect, useState } from 'react';
import { Box, Text, useInput, useApp } from 'ink';
import { Header } from '../components/Header.js';
import { Menu, type MenuItem } from '../components/Menu.js';
import { StatusBar } from '../components/StatusBar.js';
import { useStore } from '../hooks/useStore.js';
import { discoverProjects } from '../utils/crewai.js';
import * as path from 'path';

export function HomeScreen() {
  const { navigate, setProjects, projects, selectedProject } = useStore();
  const { exit } = useApp();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function loadProjects() {
      const cwd = process.cwd();
      const discovered = await discoverProjects(cwd);

      // Also check parent directory
      const parentDiscovered = await discoverProjects(path.dirname(cwd));

      const allProjects = [...discovered, ...parentDiscovered];
      setProjects(allProjects);
      setIsLoading(false);
    }
    loadProjects();
  }, [setProjects]);

  useInput((input, key) => {
    if (input === 'q') {
      exit();
    } else if (input === 'h') {
      navigate('help');
    }
  });

  const menuItems: MenuItem[] = [
    {
      label: 'Crews',
      value: 'crews',
      icon: '👥',
      description: 'Browse, create, and run crews',
    },
    {
      label: 'Flows',
      value: 'flows',
      icon: '🔄',
      description: 'Manage and execute flows',
    },
    {
      label: 'Run Crew',
      value: 'crew-run',
      icon: '▶️',
      description: 'Execute a crew with inputs',
      disabled: !selectedProject || selectedProject.type !== 'crew',
    },
    {
      label: 'Chat',
      value: 'chat',
      icon: '💬',
      description: 'Interactive chat with crew',
      disabled: !selectedProject,
    },
    {
      label: 'Agents',
      value: 'agents',
      icon: '🤖',
      description: 'View and manage agents',
      disabled: !selectedProject,
    },
    {
      label: 'Tasks',
      value: 'tasks',
      icon: '📋',
      description: 'View and manage tasks',
      disabled: !selectedProject,
    },
    {
      label: 'Memory',
      value: 'memory',
      icon: '🧠',
      description: 'View and manage crew memory',
      disabled: !selectedProject,
    },
    {
      label: 'Settings',
      value: 'settings',
      icon: '⚙️',
      description: 'Configure TUI settings',
    },
    {
      label: 'Help',
      value: 'help',
      icon: '❓',
      description: 'View help and documentation',
    },
  ];

  const handleSelect = (value: string) => {
    navigate(value as typeof useStore extends () => infer R ? R['currentScreen'] : never);
  };

  return (
    <Box flexDirection="column" padding={1}>
      <Header showFullLogo subtitle="AI Agent Framework" />

      <Box flexDirection="row" marginTop={1}>
        <Box flexDirection="column" width="60%">
          <Menu
            items={menuItems}
            onSelect={handleSelect}
            title="Main Menu"
            showIcons
            showDescriptions
          />
        </Box>

        <Box flexDirection="column" width="40%" marginLeft={2}>
          <Box
            flexDirection="column"
            borderStyle="round"
            borderColor="cyan"
            paddingX={1}
            paddingY={1}
          >
            <Text bold color="cyan">
              📁 Projects Found: {projects.length}
            </Text>

            {isLoading ? (
              <Text dimColor>Scanning for projects...</Text>
            ) : projects.length === 0 ? (
              <Box flexDirection="column" marginTop={1}>
                <Text dimColor>No CrewAI projects found.</Text>
                <Text dimColor>Create one with: crewai create crew my_crew</Text>
              </Box>
            ) : (
              <Box flexDirection="column" marginTop={1}>
                {projects.slice(0, 5).map((project) => (
                  <Box key={project.path} gap={1}>
                    <Text color={project.type === 'crew' ? 'green' : 'magenta'}>
                      {project.type === 'crew' ? '👥' : '🔄'}
                    </Text>
                    <Text>{project.name}</Text>
                    <Text dimColor>({project.type})</Text>
                  </Box>
                ))}
                {projects.length > 5 && (
                  <Text dimColor>...and {projects.length - 5} more</Text>
                )}
              </Box>
            )}
          </Box>

          {selectedProject && (
            <Box
              flexDirection="column"
              borderStyle="round"
              borderColor="green"
              paddingX={1}
              paddingY={1}
              marginTop={1}
            >
              <Text bold color="green">
                ✓ Selected Project
              </Text>
              <Box marginTop={1}>
                <Text>Name: </Text>
                <Text bold>{selectedProject.name}</Text>
              </Box>
              <Box>
                <Text>Type: </Text>
                <Text color={selectedProject.type === 'crew' ? 'green' : 'magenta'}>
                  {selectedProject.type}
                </Text>
              </Box>
              <Box>
                <Text dimColor wrap="truncate-end">{selectedProject.path}</Text>
              </Box>
            </Box>
          )}

          <Box
            flexDirection="column"
            borderStyle="single"
            borderColor="gray"
            paddingX={1}
            paddingY={1}
            marginTop={1}
          >
            <Text bold color="yellow">
              ⚡ Quick Actions
            </Text>
            <Box marginTop={1} flexDirection="column">
              <Text>
                <Text dimColor>c</Text> Create new crew
              </Text>
              <Text>
                <Text dimColor>r</Text> Run current crew
              </Text>
              <Text>
                <Text dimColor>t</Text> Run tests
              </Text>
            </Box>
          </Box>
        </Box>
      </Box>

      <StatusBar
        hints={[
          { key: '↑↓', action: 'Navigate' },
          { key: 'Enter', action: 'Select' },
          { key: 'c', action: 'Create' },
        ]}
      />
    </Box>
  );
}
