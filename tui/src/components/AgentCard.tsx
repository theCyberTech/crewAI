import React from 'react';
import { Box, Text } from 'ink';
import type { Agent } from '../types/index.js';

interface AgentCardProps {
  agent: Agent;
  isSelected?: boolean;
  showDetails?: boolean;
}

export function AgentCard({ agent, isSelected = false, showDetails = false }: AgentCardProps) {
  return (
    <Box
      flexDirection="column"
      borderStyle={isSelected ? 'double' : 'single'}
      borderColor={isSelected ? 'cyan' : 'gray'}
      paddingX={1}
      marginBottom={1}
    >
      <Box gap={1} alignItems="center">
        <Text>🤖</Text>
        <Text bold color={isSelected ? 'cyan' : 'white'}>
          {agent.role}
        </Text>
        {agent.llm && (
          <Text dimColor>[{agent.llm}]</Text>
        )}
      </Box>

      <Box marginTop={1}>
        <Text color="yellow">Goal: </Text>
        <Text wrap="wrap">{agent.goal}</Text>
      </Box>

      {showDetails && (
        <>
          {agent.backstory && (
            <Box marginTop={1}>
              <Text color="magenta">Backstory: </Text>
              <Text dimColor wrap="wrap">{agent.backstory}</Text>
            </Box>
          )}

          {agent.tools && agent.tools.length > 0 && (
            <Box marginTop={1}>
              <Text color="green">Tools: </Text>
              <Text>{agent.tools.join(', ')}</Text>
            </Box>
          )}

          <Box marginTop={1} gap={2}>
            {agent.maxIter && (
              <Box>
                <Text dimColor>Max Iterations: </Text>
                <Text>{agent.maxIter}</Text>
              </Box>
            )}
            {agent.maxRpm && (
              <Box>
                <Text dimColor>Max RPM: </Text>
                <Text>{agent.maxRpm}</Text>
              </Box>
            )}
            {agent.allowDelegation !== undefined && (
              <Box>
                <Text dimColor>Delegation: </Text>
                <Text color={agent.allowDelegation ? 'green' : 'red'}>
                  {agent.allowDelegation ? 'Enabled' : 'Disabled'}
                </Text>
              </Box>
            )}
          </Box>
        </>
      )}
    </Box>
  );
}

interface AgentListProps {
  agents: Agent[];
  selectedIndex?: number;
  onSelect?: (agent: Agent) => void;
}

export function AgentList({ agents, selectedIndex, onSelect }: AgentListProps) {
  if (agents.length === 0) {
    return (
      <Box>
        <Text dimColor>No agents configured</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column">
      {agents.map((agent, index) => (
        <AgentCard
          key={agent.id}
          agent={agent}
          isSelected={selectedIndex === index}
          showDetails={selectedIndex === index}
        />
      ))}
    </Box>
  );
}
