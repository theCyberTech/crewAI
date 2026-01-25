import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar } from '../components/StatusBar.js';
import { Tabs } from '../components/Menu.js';
import { useStore } from '../hooks/useStore.js';

const HELP_SECTIONS = {
  overview: {
    title: 'Overview',
    content: `
CrewAI TUI - Terminal User Interface

CrewAI is a cutting-edge framework for orchestrating role-playing,
autonomous AI agents. This TUI provides an interactive way to manage
and execute your CrewAI projects.

Key Features:
• Browse and manage crews and flows
• Run crews with interactive input
• Chat with your crew in real-time
• View agents and tasks configuration
• Monitor execution progress
• Manage crew memory
    `,
  },
  navigation: {
    title: 'Navigation',
    content: `
Keyboard Navigation:

  General:
    ↑/↓        Navigate menus and lists
    Enter      Select item / Confirm action
    Esc        Go back / Cancel
    Tab        Next field (in forms)
    q          Quit application
    h          Open help

  Shortcuts:
    c          Create new crew/flow
    r          Run crew/flow
    t          Run tests
    s          Select project

  In Chat:
    Enter      Send message
    Ctrl+C     End session
    `,
  },
  crews: {
    title: 'Crews',
    content: `
Working with Crews:

A Crew is a team of AI agents working together to accomplish tasks.
Each crew consists of:

  • Agents: AI entities with specific roles, goals, and tools
  • Tasks: Work items that agents execute sequentially or in parallel

Creating a Crew:
  crewai create crew my_crew

Running a Crew:
  1. Navigate to Crews screen
  2. Select your crew
  3. Press 'r' to run
  4. Provide required inputs
  5. Watch the execution progress

Configuration Files:
  src/<crew_name>/config/agents.yaml  - Agent definitions
  src/<crew_name>/config/tasks.yaml   - Task definitions
    `,
  },
  flows: {
    title: 'Flows',
    content: `
Working with Flows:

A Flow is an event-driven orchestration system for complex workflows.
Flows support:

  • Sequential and parallel execution
  • Conditional routing
  • State management
  • Method chaining with decorators

Flow Decorators:
  @start()     - Entry point method
  @listen()    - Listen for method completion
  @router()    - Conditional routing
  @and_()      - All conditions must be true
  @or_()       - Any condition can be true

Creating a Flow:
  crewai create flow my_flow

Running a Flow:
  1. Navigate to Flows screen
  2. Select your flow
  3. Press 'r' to run
  4. Monitor execution progress
    `,
  },
  commands: {
    title: 'CLI Commands',
    content: `
CrewAI CLI Commands:

  crewai create crew <name>    Create a new crew project
  crewai create flow <name>    Create a new flow project
  crewai run                   Run the crew
  crewai chat                  Interactive chat with crew
  crewai test                  Run crew tests
  crewai train                 Train crew agents
  crewai replay <task_id>      Replay from a specific task
  crewai reset-memories        Clear crew memories
  crewai kickoff               Run a flow
  crewai plot                  Generate flow diagram
  crewai deploy                Deploy to CrewAI Cloud
  crewai version               Show version info
    `,
  },
};

type HelpSection = keyof typeof HELP_SECTIONS;

export function HelpScreen() {
  const { goBack } = useStore();
  const [activeSection, setActiveSection] = useState<HelpSection>('overview');

  useInput((input, key) => {
    if (key.escape) {
      goBack();
    }
  });

  const tabs = Object.entries(HELP_SECTIONS).map(([key, section]) => ({
    label: section.title,
    value: key,
  }));

  return (
    <Box flexDirection="column" padding={1}>
      <Header subtitle="Help" />
      <Breadcrumb items={['Home', 'Help']} />

      <Box marginTop={1}>
        <Tabs
          tabs={tabs}
          activeTab={activeSection}
          onTabChange={(value) => setActiveSection(value as HelpSection)}
        />
      </Box>

      <Box
        flexDirection="column"
        borderStyle="round"
        borderColor="cyan"
        paddingX={2}
        paddingY={1}
        marginTop={1}
      >
        <Text bold color="cyan">
          {HELP_SECTIONS[activeSection].title}
        </Text>
        <Box marginTop={1}>
          <Text wrap="wrap">
            {HELP_SECTIONS[activeSection].content.trim()}
          </Text>
        </Box>
      </Box>

      <Box marginTop={1}>
        <Text dimColor>Use ← → to switch tabs</Text>
      </Box>

      <StatusBar
        hints={[
          { key: '←→', action: 'Switch Tab' },
        ]}
      />
    </Box>
  );
}
