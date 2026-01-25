import { create } from 'zustand';
import type {
  Screen,
  CrewProject,
  ExecutionEvent,
  CrewOutput,
  AppSettings,
} from '../types/index.js';

interface Store {
  // Navigation
  currentScreen: Screen;
  screenHistory: Screen[];
  screenParams: Record<string, unknown>;
  navigate: (screen: Screen, params?: Record<string, unknown>) => void;
  goBack: () => void;

  // Projects
  projects: CrewProject[];
  selectedProject: CrewProject | null;
  setProjects: (projects: CrewProject[]) => void;
  selectProject: (project: CrewProject | null) => void;
  addProject: (project: CrewProject) => void;

  // Execution
  isExecuting: boolean;
  executionEvents: ExecutionEvent[];
  executionOutput: CrewOutput | null;
  streamingText: string;
  startExecution: () => void;
  stopExecution: () => void;
  addEvent: (event: ExecutionEvent) => void;
  clearEvents: () => void;
  setOutput: (output: CrewOutput | null) => void;
  appendStreamingText: (text: string) => void;
  clearStreamingText: () => void;

  // Settings
  settings: AppSettings;
  updateSettings: (settings: Partial<AppSettings>) => void;

  // Input state
  inputMode: 'normal' | 'input' | 'chat';
  setInputMode: (mode: 'normal' | 'input' | 'chat') => void;
  currentInput: string;
  setCurrentInput: (input: string) => void;

  // Messages for chat
  chatMessages: Array<{ role: 'user' | 'assistant' | 'system'; content: string }>;
  addChatMessage: (message: { role: 'user' | 'assistant' | 'system'; content: string }) => void;
  clearChatMessages: () => void;
}

export const useStore = create<Store>((set, get) => ({
  // Navigation
  currentScreen: 'home',
  screenHistory: [],
  screenParams: {},
  navigate: (screen, params = {}) => {
    const { currentScreen, screenHistory } = get();
    set({
      currentScreen: screen,
      screenHistory: [...screenHistory, currentScreen],
      screenParams: params,
    });
  },
  goBack: () => {
    const { screenHistory } = get();
    if (screenHistory.length > 0) {
      const newHistory = [...screenHistory];
      const previousScreen = newHistory.pop()!;
      set({
        currentScreen: previousScreen,
        screenHistory: newHistory,
        screenParams: {},
      });
    }
  },

  // Projects
  projects: [],
  selectedProject: null,
  setProjects: (projects) => set({ projects }),
  selectProject: (project) => set({ selectedProject: project }),
  addProject: (project) => set((state) => ({ projects: [...state.projects, project] })),

  // Execution
  isExecuting: false,
  executionEvents: [],
  executionOutput: null,
  streamingText: '',
  startExecution: () => set({ isExecuting: true, executionEvents: [], executionOutput: null }),
  stopExecution: () => set({ isExecuting: false }),
  addEvent: (event) =>
    set((state) => ({
      executionEvents: [...state.executionEvents, event].slice(-state.settings.maxHistoryEvents),
    })),
  clearEvents: () => set({ executionEvents: [] }),
  setOutput: (output) => set({ executionOutput: output }),
  appendStreamingText: (text) => set((state) => ({ streamingText: state.streamingText + text })),
  clearStreamingText: () => set({ streamingText: '' }),

  // Settings
  settings: {
    theme: 'dark',
    verbose: true,
    showTokenUsage: true,
    maxHistoryEvents: 1000,
  },
  updateSettings: (newSettings) =>
    set((state) => ({ settings: { ...state.settings, ...newSettings } })),

  // Input
  inputMode: 'normal',
  setInputMode: (mode) => set({ inputMode: mode }),
  currentInput: '',
  setCurrentInput: (input) => set({ currentInput: input }),

  // Chat
  chatMessages: [],
  addChatMessage: (message) =>
    set((state) => ({ chatMessages: [...state.chatMessages, message] })),
  clearChatMessages: () => set({ chatMessages: [] }),
}));
