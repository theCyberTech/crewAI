import React, { useState, useEffect } from 'react';
import { Box, Text, useInput } from 'ink';
import { format } from 'date-fns';
import type { ExecutionEvent, ExecutionEventType } from '../types/index.js';

interface EventLogProps {
  events: ExecutionEvent[];
  maxVisible?: number;
  autoScroll?: boolean;
  showTimestamps?: boolean;
  filter?: ExecutionEventType[];
}

export function EventLog({
  events,
  maxVisible = 15,
  autoScroll = true,
  showTimestamps = true,
  filter,
}: EventLogProps) {
  const [scrollOffset, setScrollOffset] = useState(0);

  const filteredEvents = filter
    ? events.filter((event) => filter.includes(event.type))
    : events;

  useEffect(() => {
    if (autoScroll) {
      setScrollOffset(Math.max(0, filteredEvents.length - maxVisible));
    }
  }, [filteredEvents.length, maxVisible, autoScroll]);

  useInput((input, key) => {
    if (!autoScroll) {
      if (key.upArrow) {
        setScrollOffset((prev) => Math.max(0, prev - 1));
      } else if (key.downArrow) {
        setScrollOffset((prev) => Math.min(filteredEvents.length - maxVisible, prev + 1));
      } else if (key.pageUp) {
        setScrollOffset((prev) => Math.max(0, prev - maxVisible));
      } else if (key.pageDown) {
        setScrollOffset((prev) =>
          Math.min(filteredEvents.length - maxVisible, prev + maxVisible)
        );
      }
    }
  });

  const visibleEvents = filteredEvents.slice(scrollOffset, scrollOffset + maxVisible);

  const eventColors: Record<ExecutionEventType, string> = {
    crew_kickoff_started: 'cyan',
    crew_kickoff_completed: 'green',
    task_started: 'yellow',
    task_completed: 'green',
    agent_action: 'blue',
    tool_usage: 'magenta',
    llm_call: 'gray',
    error: 'red',
    warning: 'yellow',
    info: 'white',
  };

  const eventIcons: Record<ExecutionEventType, string> = {
    crew_kickoff_started: '🚀',
    crew_kickoff_completed: '✅',
    task_started: '📋',
    task_completed: '✓',
    agent_action: '🤖',
    tool_usage: '🔧',
    llm_call: '💭',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  };

  if (filteredEvents.length === 0) {
    return (
      <Box>
        <Text dimColor>No events yet</Text>
      </Box>
    );
  }

  return (
    <Box flexDirection="column">
      <Box marginBottom={1}>
        <Text dimColor>
          Events: {filteredEvents.length} (showing {scrollOffset + 1}-
          {Math.min(scrollOffset + maxVisible, filteredEvents.length)})
        </Text>
      </Box>

      {visibleEvents.map((event, index) => (
        <EventLogEntry
          key={scrollOffset + index}
          event={event}
          showTimestamp={showTimestamps}
          color={eventColors[event.type]}
          icon={eventIcons[event.type]}
        />
      ))}

      {filteredEvents.length > maxVisible && (
        <Box marginTop={1}>
          <Text dimColor>
            Use ↑↓ to scroll • Page Up/Down for fast scroll
          </Text>
        </Box>
      )}
    </Box>
  );
}

interface EventLogEntryProps {
  event: ExecutionEvent;
  showTimestamp?: boolean;
  color?: string;
  icon?: string;
}

function EventLogEntry({ event, showTimestamp = true, color = 'white', icon }: EventLogEntryProps) {
  const message = event.data.message as string || JSON.stringify(event.data);

  return (
    <Box gap={1}>
      {showTimestamp && (
        <Text dimColor>
          [{format(event.timestamp, 'HH:mm:ss')}]
        </Text>
      )}
      {icon && <Text>{icon}</Text>}
      <Text color={color}>
        {message}
      </Text>
    </Box>
  );
}

interface StreamingOutputProps {
  text: string;
  isActive?: boolean;
}

export function StreamingOutput({ text, isActive = true }: StreamingOutputProps) {
  const lines = text.split('\n').slice(-20);

  return (
    <Box flexDirection="column" borderStyle="single" borderColor={isActive ? 'cyan' : 'gray'} paddingX={1}>
      <Box marginBottom={1}>
        <Text bold color="cyan">
          {isActive ? '● Live Output' : '○ Output'}
        </Text>
      </Box>
      {lines.map((line, index) => (
        <Text key={index} wrap="wrap">
          {line}
        </Text>
      ))}
      {isActive && (
        <Text color="cyan">▌</Text>
      )}
    </Box>
  );
}

interface OutputViewerProps {
  output: string;
  title?: string;
  maxLines?: number;
}

export function OutputViewer({ output, title = 'Output', maxLines = 30 }: OutputViewerProps) {
  const [scrollOffset, setScrollOffset] = useState(0);
  const lines = output.split('\n');

  useInput((input, key) => {
    if (key.upArrow) {
      setScrollOffset((prev) => Math.max(0, prev - 1));
    } else if (key.downArrow) {
      setScrollOffset((prev) => Math.min(lines.length - maxLines, prev + 1));
    }
  });

  const visibleLines = lines.slice(scrollOffset, scrollOffset + maxLines);

  return (
    <Box flexDirection="column" borderStyle="round" borderColor="green" paddingX={1}>
      <Box marginBottom={1} justifyContent="space-between">
        <Text bold color="green">{title}</Text>
        <Text dimColor>
          Lines {scrollOffset + 1}-{Math.min(scrollOffset + maxLines, lines.length)} of {lines.length}
        </Text>
      </Box>
      {visibleLines.map((line, index) => (
        <Text key={scrollOffset + index} wrap="wrap">
          {line}
        </Text>
      ))}
    </Box>
  );
}
