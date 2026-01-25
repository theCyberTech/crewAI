// CrewAI Types for TUI

export interface Agent {
  id: string;
  role: string;
  goal: string;
  backstory: string;
  tools?: string[];
  llm?: string;
  maxIter?: number;
  maxRpm?: number;
  verbose?: boolean;
  allowDelegation?: boolean;
  cacheEnabled?: boolean;
}

export interface Task {
  id: string;
  description: string;
  expectedOutput: string;
  agent: string;
  tools?: string[];
  asyncExecution?: boolean;
  context?: string[];
  outputFile?: string;
  outputJson?: string;
  outputPydantic?: string;
}

export interface Crew {
  name: string;
  description?: string;
  agents: Agent[];
  tasks: Task[];
  process: 'sequential' | 'hierarchical';
  verbose?: boolean;
  memory?: boolean;
  embedder?: Record<string, unknown>;
  managerLlm?: string;
  managerAgent?: Agent;
  planning?: boolean;
  planningLlm?: string;
}

export interface Flow {
  name: string;
  description?: string;
  methods: FlowMethod[];
  state?: Record<string, unknown>;
}

export interface FlowMethod {
  name: string;
  type: 'start' | 'listen' | 'router';
  condition?: string;
  description?: string;
}

export interface CrewProject {
  name: string;
  path: string;
  type: 'crew' | 'flow';
  config?: {
    agents?: string;
    tasks?: string;
  };
}

export interface ExecutionEvent {
  type: ExecutionEventType;
  timestamp: Date;
  data: Record<string, unknown>;
  source?: string;
}

export type ExecutionEventType =
  | 'crew_kickoff_started'
  | 'crew_kickoff_completed'
  | 'task_started'
  | 'task_completed'
  | 'agent_action'
  | 'tool_usage'
  | 'llm_call'
  | 'error'
  | 'warning'
  | 'info';

export interface TaskOutput {
  taskId: string;
  taskDescription: string;
  raw: string;
  pydantic?: Record<string, unknown>;
  jsonDict?: Record<string, unknown>;
  agent: string;
}

export interface CrewOutput {
  raw: string;
  pydantic?: Record<string, unknown>;
  jsonDict?: Record<string, unknown>;
  tasksOutput: TaskOutput[];
  tokenUsage: UsageMetrics;
}

export interface UsageMetrics {
  totalTokens: number;
  promptTokens: number;
  completionTokens: number;
  cachedPromptTokens?: number;
  successfulRequests: number;
}

export interface MemoryEntry {
  id: string;
  content: string;
  timestamp: Date;
  type: 'short_term' | 'long_term' | 'entity';
  metadata?: Record<string, unknown>;
}

export interface KnowledgeSource {
  id: string;
  name: string;
  type: 'file' | 'directory' | 'url' | 'text';
  source: string;
  chunkSize?: number;
  chunkOverlap?: number;
}

export type Screen =
  | 'home'
  | 'crews'
  | 'crew-detail'
  | 'crew-run'
  | 'flows'
  | 'flow-detail'
  | 'flow-run'
  | 'agents'
  | 'tasks'
  | 'memory'
  | 'knowledge'
  | 'settings'
  | 'help'
  | 'chat';

export interface NavigationState {
  currentScreen: Screen;
  history: Screen[];
  params: Record<string, unknown>;
}

export interface AppState {
  navigation: NavigationState;
  projects: CrewProject[];
  selectedProject: CrewProject | null;
  execution: {
    running: boolean;
    events: ExecutionEvent[];
    output: CrewOutput | null;
  };
  settings: AppSettings;
}

export interface AppSettings {
  theme: 'dark' | 'light';
  verbose: boolean;
  showTokenUsage: boolean;
  maxHistoryEvents: number;
  pythonPath?: string;
  crewaiPath?: string;
}
