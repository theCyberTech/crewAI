import React, { useState, useEffect } from 'react';
import { Box, Text, useInput } from 'ink';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar } from '../components/StatusBar.js';
import { AgentCard } from '../components/AgentCard.js';
import { useStore } from '../hooks/useStore.js';
import { loadAgentsConfig } from '../utils/crewai.js';
import type { Agent } from '../types/index.js';

export function AgentsScreen() {
  const { goBack, selectedProject } = useStore();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    if (selectedProject?.config?.agents) {
      const loaded = loadAgentsConfig(selectedProject.config.agents);
      setAgents(loaded);
    }
  }, [selectedProject]);

  useInput((input, key) => {
    if (key.escape) {
      goBack();
    } else if (key.upArrow) {
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : agents.length - 1));
    } else if (key.downArrow) {
      setSelectedIndex((prev) => (prev < agents.length - 1 ? prev + 1 : 0));
    }
  });

  if (!selectedProject) {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle="Agents" />
        <Text color="red">No project selected. Please select a crew first.</Text>
        <StatusBar />
      </Box>
    );
  }

  return (
    <Box flexDirection="column" padding={1}>
      <Header subtitle="Agents" />
      <Breadcrumb items={['Home', selectedProject.name, 'Agents']} />

      {agents.length === 0 ? (
        <Box
          flexDirection="column"
          borderStyle="round"
          borderColor="yellow"
          paddingX={2}
          paddingY={1}
          marginTop={1}
        >
          <Text color="yellow">No agents found in this project.</Text>
          <Box marginTop={1}>
            <Text dimColor>Check your agents.yaml configuration file.</Text>
          </Box>
        </Box>
      ) : (
        <Box flexDirection="column" marginTop={1}>
          <Text bold color="blue">
            🤖 Agents ({agents.length})
          </Text>
          <Text dimColor>Use ↑↓ to navigate and view details</Text>

          <Box flexDirection="column" marginTop={1}>
            {agents.map((agent, index) => (
              <AgentCard
                key={agent.id}
                agent={agent}
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
