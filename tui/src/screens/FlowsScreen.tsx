import React, { useState, useEffect } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar } from '../components/StatusBar.js';
import { StreamingOutput, OutputViewer } from '../components/EventLog.js';
import { useStore } from '../hooks/useStore.js';
import { kickoffFlow, plotFlow } from '../utils/crewai.js';
import type { CrewProject } from '../types/index.js';

type FlowPhase = 'list' | 'detail' | 'running' | 'completed' | 'error';

export function FlowsScreen() {
  const {
    navigate,
    goBack,
    projects,
    selectProject,
    selectedProject,
    startExecution,
    stopExecution,
    streamingText,
    appendStreamingText,
    clearStreamingText,
  } = useStore();

  const [selectedIndex, setSelectedIndex] = useState(0);
  const [phase, setPhase] = useState<FlowPhase>('list');
  const [output, setOutput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [mermaidDiagram, setMermaidDiagram] = useState<string | null>(null);

  const flowProjects = projects.filter((p) => p.type === 'flow');

  useInput((input, key) => {
    if (key.escape) {
      if (phase === 'detail' || phase === 'completed' || phase === 'error') {
        setPhase('list');
        setOutput('');
        setError(null);
        setMermaidDiagram(null);
      } else if (phase === 'list') {
        goBack();
      }
    } else if (key.upArrow && phase === 'list') {
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : flowProjects.length - 1));
    } else if (key.downArrow && phase === 'list') {
      setSelectedIndex((prev) => (prev < flowProjects.length - 1 ? prev + 1 : 0));
    } else if (key.return && phase === 'list' && flowProjects[selectedIndex]) {
      selectProject(flowProjects[selectedIndex]!);
      setPhase('detail');
    } else if (input === 'r' && phase === 'detail') {
      handleRunFlow();
    } else if (input === 'p' && phase === 'detail') {
      handlePlotFlow();
    }
  });

  const handleRunFlow = async () => {
    if (!selectedProject) return;

    setPhase('running');
    startExecution();
    clearStreamingText();

    try {
      const result = await kickoffFlow(
        selectedProject.path,
        (data) => {
          appendStreamingText(data);
        }
      );

      stopExecution();
      setOutput(result.stdout);

      if (result.success) {
        setPhase('completed');
      } else {
        setPhase('error');
        setError(result.stderr || 'Unknown error occurred');
      }
    } catch (err) {
      stopExecution();
      setPhase('error');
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  const handlePlotFlow = async () => {
    if (!selectedProject) return;

    const result = await plotFlow(selectedProject.path);
    if (result.success) {
      setMermaidDiagram(result.stdout);
    }
  };

  if (flowProjects.length === 0) {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle="Flows" />
        <Breadcrumb items={['Home', 'Flows']} />

        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor="yellow"
          paddingX={2}
          paddingY={1}
          marginTop={1}
        >
          <Text color="yellow">No flows found in the current directory.</Text>
          <Box marginTop={1}>
            <Text>Create a new flow with:</Text>
          </Box>
          <Box marginTop={1}>
            <Text color="cyan">crewai create flow my_flow</Text>
          </Box>
        </Box>

        <StatusBar />
      </Box>
    );
  }

  if (phase === 'running') {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle={`Running: ${selectedProject?.name}`} />
        <Breadcrumb items={['Home', 'Flows', selectedProject?.name || '', 'Running']} />

        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor="yellow"
          paddingX={2}
          paddingY={1}
          marginTop={1}
        >
          <Box gap={1} alignItems="center">
            <Text color="yellow">
              <Spinner type="dots" />
            </Text>
            <Text bold color="yellow">
              Flow Running...
            </Text>
          </Box>
        </Box>

        <Box marginTop={1}>
          <StreamingOutput text={streamingText} isActive={true} />
        </Box>

        <StatusBar hints={[{ key: 'Esc', action: 'Cancel' }]} />
      </Box>
    );
  }

  if (phase === 'completed' || phase === 'error') {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle={selectedProject?.name || ''} />
        <Breadcrumb items={['Home', 'Flows', selectedProject?.name || '', phase === 'completed' ? 'Done' : 'Error']} />

        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor={phase === 'completed' ? 'green' : 'red'}
          paddingX={2}
          paddingY={1}
          marginTop={1}
        >
          <Text bold color={phase === 'completed' ? 'green' : 'red'}>
            {phase === 'completed' ? '✅ Flow Completed Successfully' : '❌ Flow Failed'}
          </Text>
          {error && (
            <Box marginTop={1}>
              <Text color="red">{error}</Text>
            </Box>
          )}
        </Box>

        <Box marginTop={1}>
          <OutputViewer output={output} title="Flow Output" />
        </Box>

        <StatusBar hints={[{ key: 'r', action: 'Run Again' }, { key: 'Esc', action: 'Back' }]} />
      </Box>
    );
  }

  if (phase === 'detail') {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle={selectedProject?.name || ''} />
        <Breadcrumb items={['Home', 'Flows', selectedProject?.name || '']} />

        <Box flexDirection="row" marginTop={1}>
          <Box flexDirection="column" width="50%">
            <Box
              flexDirection="column"
              borderStyle="round"
              borderColor="magenta"
              paddingX={2}
              paddingY={1}
            >
              <Text bold color="magenta">🔄 Flow Details</Text>
              <Box marginTop={1} flexDirection="column">
                <Box>
                  <Text>Name: </Text>
                  <Text bold>{selectedProject?.name}</Text>
                </Box>
                <Box>
                  <Text>Path: </Text>
                  <Text dimColor>{selectedProject?.path}</Text>
                </Box>
              </Box>
            </Box>

            <Box
              flexDirection="column"
              borderStyle="single"
              borderColor="gray"
              paddingX={2}
              paddingY={1}
              marginTop={1}
            >
              <Text bold>Actions</Text>
              <Box marginTop={1} flexDirection="column">
                <Text>
                  <Text color="cyan">r</Text> - Run flow
                </Text>
                <Text>
                  <Text color="cyan">p</Text> - Plot flow diagram
                </Text>
              </Box>
            </Box>
          </Box>

          <Box flexDirection="column" width="50%" marginLeft={2}>
            {mermaidDiagram && (
              <Box
                flexDirection="column"
                borderStyle="round"
                borderColor="blue"
                paddingX={2}
                paddingY={1}
              >
                <Text bold color="blue">Flow Diagram (Mermaid)</Text>
                <Box marginTop={1}>
                  <Text dimColor>{mermaidDiagram}</Text>
                </Box>
              </Box>
            )}
          </Box>
        </Box>

        <StatusBar hints={[{ key: 'r', action: 'Run' }, { key: 'p', action: 'Plot' }, { key: 'Esc', action: 'Back' }]} />
      </Box>
    );
  }

  // List view
  return (
    <Box flexDirection="column" padding={1}>
      <Header subtitle="Flows" />
      <Breadcrumb items={['Home', 'Flows']} />

      <Box flexDirection="column" marginTop={1}>
        <Text bold color="magenta">Available Flows ({flowProjects.length})</Text>
        <Box marginTop={1} flexDirection="column">
          {flowProjects.map((project, index) => (
            <FlowListItem
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
        ]}
      />
    </Box>
  );
}

interface FlowListItemProps {
  project: CrewProject;
  isSelected: boolean;
  isActive: boolean;
}

function FlowListItem({ project, isSelected, isActive }: FlowListItemProps) {
  return (
    <Box
      borderStyle={isSelected ? 'double' : 'single'}
      borderColor={isSelected ? 'magenta' : isActive ? 'green' : 'gray'}
      paddingX={1}
      marginBottom={1}
    >
      <Box gap={1} alignItems="center">
        <Text>{isSelected ? '❯' : ' '}</Text>
        <Text>🔄</Text>
        <Text bold color={isSelected ? 'magenta' : 'white'}>
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
