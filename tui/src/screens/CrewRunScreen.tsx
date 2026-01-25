import React, { useState, useEffect, useRef } from 'react';
import { Box, Text, useInput } from 'ink';
import Spinner from 'ink-spinner';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar, ProgressBar } from '../components/StatusBar.js';
import { Form } from '../components/Input.js';
import { TaskTimeline } from '../components/TaskCard.js';
import { StreamingOutput, OutputViewer } from '../components/EventLog.js';
import { useStore } from '../hooks/useStore.js';
import {
  runCrew,
  loadTasksConfig,
  getProjectInputPlaceholders,
} from '../utils/crewai.js';
import type { Task } from '../types/index.js';

type RunPhase = 'input' | 'running' | 'completed' | 'error';

export function CrewRunScreen() {
  const {
    goBack,
    selectedProject,
    isExecuting,
    startExecution,
    stopExecution,
    streamingText,
    appendStreamingText,
    clearStreamingText,
  } = useStore();

  const [phase, setPhase] = useState<RunPhase>('input');
  const [inputFields, setInputFields] = useState<string[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [currentTaskIndex, setCurrentTaskIndex] = useState(-1);
  const [output, setOutput] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [startTime, setStartTime] = useState<Date | null>(null);
  const [endTime, setEndTime] = useState<Date | null>(null);

  useEffect(() => {
    if (selectedProject) {
      const placeholders = getProjectInputPlaceholders(selectedProject.path);
      setInputFields(placeholders);

      const loadedTasks = loadTasksConfig(selectedProject.config?.tasks || '');
      setTasks(loadedTasks);
    }
  }, [selectedProject]);

  useInput((input, key) => {
    if (key.escape) {
      if (phase === 'running') {
        // TODO: Implement cancellation
      } else {
        goBack();
      }
    } else if (input === 'r' && (phase === 'completed' || phase === 'error')) {
      setPhase('input');
      setOutput('');
      setError(null);
      setCurrentTaskIndex(-1);
      clearStreamingText();
    }
  });

  const handleSubmit = async (values: Record<string, string>) => {
    if (!selectedProject) return;

    setPhase('running');
    startExecution();
    setStartTime(new Date());
    clearStreamingText();

    try {
      const result = await runCrew(
        selectedProject.path,
        values,
        (data, isError) => {
          appendStreamingText(data);

          // Try to detect task progress from output
          if (data.includes('Task:') || data.includes('Starting')) {
            const taskMatch = data.match(/Task:\s*(\w+)/);
            if (taskMatch) {
              const taskId = taskMatch[1];
              const idx = tasks.findIndex((t) => t.id === taskId);
              if (idx >= 0) {
                setCurrentTaskIndex(idx);
              }
            }
          }
        }
      );

      setEndTime(new Date());
      stopExecution();
      setOutput(result.stdout);

      if (result.success) {
        setPhase('completed');
        setCurrentTaskIndex(tasks.length); // All done
      } else {
        setPhase('error');
        setError(result.stderr || 'Unknown error occurred');
      }
    } catch (err) {
      setEndTime(new Date());
      stopExecution();
      setPhase('error');
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  };

  if (!selectedProject) {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle="Run Crew" />
        <Text color="red">No project selected. Please select a crew first.</Text>
        <StatusBar />
      </Box>
    );
  }

  const formFields = inputFields.map((field) => ({
    name: field,
    label: field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' '),
    placeholder: `Enter ${field}...`,
    required: true,
  }));

  return (
    <Box flexDirection="column" padding={1}>
      <Header subtitle={`Run: ${selectedProject.name}`} />
      <Breadcrumb items={['Home', 'Crews', selectedProject.name, 'Run']} />

      {phase === 'input' && (
        <Box flexDirection="column" marginTop={1}>
          <Box
            flexDirection="column"
            borderStyle="round"
            borderColor="cyan"
            paddingX={2}
            paddingY={1}
          >
            <Text bold color="cyan">
              🚀 Crew Inputs
            </Text>
            <Text dimColor>
              Provide the required inputs for this crew run.
            </Text>

            <Box marginTop={1}>
              {formFields.length === 0 ? (
                <Box flexDirection="column">
                  <Text>No inputs required for this crew.</Text>
                  <Box marginTop={1}>
                    <Form
                      fields={[]}
                      onSubmit={handleSubmit}
                      onCancel={goBack}
                      submitLabel="Start Crew"
                    />
                  </Box>
                </Box>
              ) : (
                <Form
                  fields={formFields}
                  onSubmit={handleSubmit}
                  onCancel={goBack}
                  submitLabel="Start Crew"
                />
              )}
            </Box>
          </Box>

          {tasks.length > 0 && (
            <Box
              flexDirection="column"
              borderStyle="single"
              borderColor="gray"
              paddingX={2}
              paddingY={1}
              marginTop={1}
            >
              <Text bold>📋 Tasks to Execute ({tasks.length})</Text>
              <Box marginTop={1}>
                <TaskTimeline tasks={tasks} currentTaskIndex={-1} />
              </Box>
            </Box>
          )}
        </Box>
      )}

      {phase === 'running' && (
        <Box flexDirection="column" marginTop={1}>
          <Box
            flexDirection="column"
            borderStyle="round"
            borderColor="yellow"
            paddingX={2}
            paddingY={1}
          >
            <Box gap={1} alignItems="center">
              <Text color="yellow">
                <Spinner type="dots" />
              </Text>
              <Text bold color="yellow">
                Crew Running...
              </Text>
            </Box>

            {startTime && (
              <Text dimColor>
                Started: {startTime.toLocaleTimeString()}
              </Text>
            )}
          </Box>

          {tasks.length > 0 && (
            <Box
              flexDirection="column"
              borderStyle="single"
              borderColor="yellow"
              paddingX={2}
              paddingY={1}
              marginTop={1}
            >
              <Text bold>Task Progress</Text>
              <Box marginTop={1}>
                <ProgressBar
                  value={Math.max(0, currentTaskIndex + 1)}
                  total={tasks.length}
                  color="yellow"
                />
              </Box>
              <Box marginTop={1}>
                <TaskTimeline tasks={tasks} currentTaskIndex={currentTaskIndex} />
              </Box>
            </Box>
          )}

          <Box marginTop={1}>
            <StreamingOutput text={streamingText} isActive={true} />
          </Box>
        </Box>
      )}

      {phase === 'completed' && (
        <Box flexDirection="column" marginTop={1}>
          <Box
            flexDirection="column"
            borderStyle="round"
            borderColor="green"
            paddingX={2}
            paddingY={1}
          >
            <Text bold color="green">
              ✅ Crew Completed Successfully
            </Text>
            {startTime && endTime && (
              <Text dimColor>
                Duration: {((endTime.getTime() - startTime.getTime()) / 1000).toFixed(1)}s
              </Text>
            )}
          </Box>

          <Box marginTop={1}>
            <OutputViewer output={output} title="Crew Output" />
          </Box>
        </Box>
      )}

      {phase === 'error' && (
        <Box flexDirection="column" marginTop={1}>
          <Box
            flexDirection="column"
            borderStyle="round"
            borderColor="red"
            paddingX={2}
            paddingY={1}
          >
            <Text bold color="red">
              ❌ Crew Failed
            </Text>
            <Box marginTop={1}>
              <Text color="red">{error}</Text>
            </Box>
          </Box>

          {output && (
            <Box marginTop={1}>
              <OutputViewer output={output} title="Partial Output" />
            </Box>
          )}
        </Box>
      )}

      <StatusBar
        hints={
          phase === 'running'
            ? [{ key: 'Esc', action: 'Cancel' }]
            : phase === 'completed' || phase === 'error'
            ? [{ key: 'r', action: 'Run Again' }, { key: 'Esc', action: 'Back' }]
            : [{ key: 'Enter', action: 'Submit' }, { key: 'Tab', action: 'Next Field' }]
        }
      />
    </Box>
  );
}
