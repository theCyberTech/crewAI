import React, { useState, useEffect } from 'react';
import { Box, Text, useInput, useApp } from 'ink';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar, LoadingIndicator } from '../components/StatusBar.js';
import { useStore } from '../hooks/useStore.js';
import { loadAgentsConfig, loadTasksConfig } from '../utils/crewai.js';
import type { Agent, Task, CrewProject } from '../types/index.js';

export function CrewsScreen() {
  const { navigate, goBack, projects, selectProject, selectedProject } = useStore();
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [viewMode, setViewMode] = useState<'list' | 'detail'>('list');
  const [projectDetails, setProjectDetails] = useState<{
    agents: Agent[];
    tasks: Task[];
  } | null>(null);

  const crewProjects = projects.filter((p) => p.type === 'crew');

  useEffect(() => {
    if (viewMode === 'detail' && crewProjects[selectedIndex]) {
      const project = crewProjects[selectedIndex]!;
      const agents = loadAgentsConfig(project.config?.agents || '');
      const tasks = loadTasksConfig(project.config?.tasks || '');
      setProjectDetails({ agents, tasks });
    }
  }, [viewMode, selectedIndex, crewProjects]);

  useInput((input, key) => {
    if (key.escape) {
      if (viewMode === 'detail') {
        setViewMode('list');
        setProjectDetails(null);
      } else {
        goBack();
      }
    } else if (key.upArrow && viewMode === 'list') {
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : crewProjects.length - 1));
    } else if (key.downArrow && viewMode === 'list') {
      setSelectedIndex((prev) => (prev < crewProjects.length - 1 ? prev + 1 : 0));
    } else if (key.return && viewMode === 'list' && crewProjects[selectedIndex]) {
      setViewMode('detail');
    } else if (input === 's' && viewMode === 'detail' && crewProjects[selectedIndex]) {
      selectProject(crewProjects[selectedIndex]!);
    } else if (input === 'r' && viewMode === 'detail' && crewProjects[selectedIndex]) {
      selectProject(crewProjects[selectedIndex]!);
      navigate('crew-run');
    } else if (input === 'c') {
      navigate('crew-create' as any);
    } else if (input === 'h') {
      navigate('help');
    }
  });

  if (crewProjects.length === 0) {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle="Crews" />
        <Breadcrumb items={['Home', 'Crews']} />

        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor="yellow"
          paddingX={2}
          paddingY={1}
          marginTop={1}
        >
          <Text color="yellow">No crews found in the current directory.</Text>
          <Box marginTop={1}>
            <Text>Create a new crew with:</Text>
          </Box>
          <Box marginTop={1}>
            <Text color="cyan">crewai create crew my_crew</Text>
          </Box>
        </Box>

        <StatusBar
          hints={[
            { key: 'c', action: 'Create Crew' },
          ]}
        />
      </Box>
    );
  }

  if (viewMode === 'detail') {
    const project = crewProjects[selectedIndex]!;
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle={project.name} />
        <Breadcrumb items={['Home', 'Crews', project.name]} />

        <Box flexDirection="row" marginTop={1}>
          <Box flexDirection="column" width="50%">
            <Box
              flexDirection="column"
              borderStyle="round"
              borderColor="cyan"
              paddingX={1}
              marginBottom={1}
            >
              <Text bold color="cyan">📋 Crew Details</Text>
              <Box marginTop={1} flexDirection="column">
                <Box>
                  <Text>Name: </Text>
                  <Text bold>{project.name}</Text>
                </Box>
                <Box>
                  <Text>Path: </Text>
                  <Text dimColor>{project.path}</Text>
                </Box>
                <Box>
                  <Text>Type: </Text>
                  <Text color="green">{project.type}</Text>
                </Box>
              </Box>
            </Box>

            <Box
              flexDirection="column"
              borderStyle="single"
              borderColor={selectedProject?.path === project.path ? 'green' : 'gray'}
              paddingX={1}
            >
              {selectedProject?.path === project.path ? (
                <Text color="green">✓ Currently Selected</Text>
              ) : (
                <Text dimColor>Press 's' to select this project</Text>
              )}
            </Box>
          </Box>

          <Box flexDirection="column" width="50%" marginLeft={2}>
            <Box
              flexDirection="column"
              borderStyle="round"
              borderColor="blue"
              paddingX={1}
              marginBottom={1}
            >
              <Text bold color="blue">🤖 Agents ({projectDetails?.agents.length || 0})</Text>
              <Box marginTop={1} flexDirection="column">
                {projectDetails?.agents.slice(0, 5).map((agent) => (
                  <Box key={agent.id} gap={1}>
                    <Text color="blue">•</Text>
                    <Text>{agent.role}</Text>
                  </Box>
                ))}
                {(projectDetails?.agents.length || 0) > 5 && (
                  <Text dimColor>...and {(projectDetails?.agents.length || 0) - 5} more</Text>
                )}
              </Box>
            </Box>

            <Box
              flexDirection="column"
              borderStyle="round"
              borderColor="yellow"
              paddingX={1}
            >
              <Text bold color="yellow">📋 Tasks ({projectDetails?.tasks.length || 0})</Text>
              <Box marginTop={1} flexDirection="column">
                {projectDetails?.tasks.slice(0, 5).map((task, idx) => (
                  <Box key={task.id} gap={1}>
                    <Text color="yellow">#{idx + 1}</Text>
                    <Text>{task.id}</Text>
                  </Box>
                ))}
                {(projectDetails?.tasks.length || 0) > 5 && (
                  <Text dimColor>...and {(projectDetails?.tasks.length || 0) - 5} more</Text>
                )}
              </Box>
            </Box>
          </Box>
        </Box>

        <StatusBar
          hints={[
            { key: 'r', action: 'Run' },
            { key: 's', action: 'Select' },
            { key: 'Esc', action: 'Back' },
          ]}
        />
      </Box>
    );
  }

  return (
    <Box flexDirection="column" padding={1}>
      <Header subtitle="Crews" />
      <Breadcrumb items={['Home', 'Crews']} />

      <Box flexDirection="column" marginTop={1}>
        <Text bold color="cyan">Available Crews ({crewProjects.length})</Text>
        <Box marginTop={1} flexDirection="column">
          {crewProjects.map((project, index) => (
            <ProjectListItem
              key={project.path}
              project={project}
              isSelected={index === selectedIndex}
              isActive={selectedProject?.path === project.path}
            />
          ))}
        </Box>
      </Box>

      <StatusBar
        hints={[
          { key: '↑↓', action: 'Navigate' },
          { key: 'Enter', action: 'View Details' },
          { key: 'c', action: 'Create' },
        ]}
      />
    </Box>
  );
}

interface ProjectListItemProps {
  project: CrewProject;
  isSelected: boolean;
  isActive: boolean;
}

function ProjectListItem({ project, isSelected, isActive }: ProjectListItemProps) {
  return (
    <Box
      borderStyle={isSelected ? 'double' : 'single'}
      borderColor={isSelected ? 'cyan' : isActive ? 'green' : 'gray'}
      paddingX={1}
      marginBottom={1}
    >
      <Box gap={1} alignItems="center">
        <Text>{isSelected ? '❯' : ' '}</Text>
        <Text>👥</Text>
        <Text bold color={isSelected ? 'cyan' : 'white'}>
          {project.name}
        </Text>
        {isActive && (
          <Text color="green">[active]</Text>
        )}
      </Box>
      <Box marginLeft={4}>
        <Text dimColor wrap="truncate-end">{project.path}</Text>
      </Box>
    </Box>
  );
}
