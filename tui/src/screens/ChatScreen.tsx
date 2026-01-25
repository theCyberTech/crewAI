import React, { useState, useEffect, useRef } from 'react';
import { Box, Text, useInput } from 'ink';
import TextInput from 'ink-text-input';
import Spinner from 'ink-spinner';
import { Header, Breadcrumb } from '../components/Header.js';
import { StatusBar } from '../components/StatusBar.js';
import { useStore } from '../hooks/useStore.js';
import { spawnCrewAICommand } from '../utils/crewai.js';
import type { ChildProcess } from 'child_process';

interface ChatMessage {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
}

export function ChatScreen() {
  const { goBack, selectedProject, chatMessages, addChatMessage, clearChatMessages } = useStore();
  const [input, setInput] = useState('');
  const [isWaiting, setIsWaiting] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const [chatProcess, setChatProcess] = useState<ReturnType<typeof spawnCrewAICommand> | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (selectedProject) {
      startChatSession();
    }

    return () => {
      if (chatProcess) {
        chatProcess.kill();
      }
    };
  }, [selectedProject]);

  const startChatSession = async () => {
    if (!selectedProject) return;

    clearChatMessages();
    addChatMessage({
      role: 'system',
      content: `Starting chat session with ${selectedProject.name}...`,
    });

    try {
      const proc = spawnCrewAICommand(['chat'], selectedProject.path);
      setChatProcess(proc);

      if (proc.stdout) {
        proc.stdout.on('data', (data: Buffer) => {
          const text = data.toString();
          setCurrentResponse((prev) => prev + text);

          // Check for prompt indicator that response is complete
          if (text.includes('>') || text.includes('User:')) {
            const response = currentResponse.trim();
            if (response) {
              addChatMessage({
                role: 'assistant',
                content: response,
              });
            }
            setCurrentResponse('');
            setIsWaiting(false);
          }
        });
      }

      if (proc.stderr) {
        proc.stderr.on('data', (data: Buffer) => {
          addChatMessage({
            role: 'system',
            content: `Error: ${data.toString()}`,
          });
        });
      }

      proc.on('close', () => {
        setIsConnected(false);
        addChatMessage({
          role: 'system',
          content: 'Chat session ended.',
        });
      });

      setIsConnected(true);
      addChatMessage({
        role: 'system',
        content: 'Chat session started. Type your message and press Enter.',
      });
    } catch (error) {
      addChatMessage({
        role: 'system',
        content: `Failed to start chat: ${error instanceof Error ? error.message : 'Unknown error'}`,
      });
    }
  };

  useInput((inputChar, key) => {
    if (key.escape) {
      if (chatProcess) {
        chatProcess.kill();
      }
      goBack();
    } else if (key.ctrl && inputChar === 'c') {
      if (chatProcess) {
        chatProcess.kill();
      }
    }
  });

  const handleSend = () => {
    if (!input.trim() || !chatProcess || isWaiting) return;

    const message = input.trim();
    setInput('');

    addChatMessage({
      role: 'user',
      content: message,
    });

    setIsWaiting(true);

    // Send to the chat process
    if (chatProcess.stdin) {
      chatProcess.stdin.write(message + '\n');
    }
  };

  if (!selectedProject) {
    return (
      <Box flexDirection="column" padding={1}>
        <Header subtitle="Chat" />
        <Text color="red">No project selected. Please select a crew first.</Text>
        <StatusBar />
      </Box>
    );
  }

  const visibleMessages = chatMessages.slice(-15);

  return (
    <Box flexDirection="column" padding={1} height={process.stdout.rows - 2}>
      <Header subtitle={`Chat: ${selectedProject.name}`} />
      <Breadcrumb items={['Home', 'Chat', selectedProject.name]} />

      <Box
        flexDirection="column"
        flexGrow={1}
        borderStyle="round"
        borderColor={isConnected ? 'cyan' : 'gray'}
        paddingX={1}
        marginTop={1}
      >
        <Box flexDirection="column" flexGrow={1}>
          {visibleMessages.map((msg, idx) => (
            <ChatMessageItem key={idx} message={msg} />
          ))}

          {isWaiting && (
            <Box gap={1} marginTop={1}>
              <Text color="cyan">
                <Spinner type="dots" />
              </Text>
              <Text color="cyan">Thinking...</Text>
            </Box>
          )}

          {currentResponse && (
            <Box marginTop={1}>
              <Text color="green">🤖 </Text>
              <Text color="white">{currentResponse}</Text>
              <Text color="cyan">▌</Text>
            </Box>
          )}
        </Box>
      </Box>

      <Box
        borderStyle="round"
        borderColor={isWaiting ? 'gray' : 'cyan'}
        paddingX={1}
        marginTop={1}
      >
        <Text color="cyan">{'> '}</Text>
        <TextInput
          value={input}
          onChange={setInput}
          onSubmit={handleSend}
          placeholder={isWaiting ? 'Waiting for response...' : 'Type a message...'}
        />
      </Box>

      <StatusBar
        hints={[
          { key: 'Enter', action: 'Send' },
          { key: 'Ctrl+C', action: 'End Session' },
        ]}
        status={isConnected ? 'Connected' : 'Disconnected'}
      />
    </Box>
  );
}

interface ChatMessageItemProps {
  message: ChatMessage;
}

function ChatMessageItem({ message }: ChatMessageItemProps) {
  const roleColors = {
    user: 'blue',
    assistant: 'green',
    system: 'gray',
  } as const;

  const roleIcons = {
    user: '👤',
    assistant: '🤖',
    system: 'ℹ️',
  };

  return (
    <Box marginBottom={1}>
      <Box gap={1}>
        <Text>{roleIcons[message.role]}</Text>
        <Text color={roleColors[message.role]} bold>
          {message.role === 'user' ? 'You' : message.role === 'assistant' ? 'Crew' : 'System'}:
        </Text>
      </Box>
      <Box marginLeft={3}>
        <Text wrap="wrap" color={message.role === 'system' ? 'gray' : 'white'}>
          {message.content}
        </Text>
      </Box>
    </Box>
  );
}
