import { execa, type ExecaChildProcess } from 'execa';
import * as fs from 'fs';
import * as path from 'path';
import YAML from 'yaml';
import type { CrewProject, Agent, Task, ExecutionEvent } from '../types/index.js';

const CREWAI_CMD = 'crewai';

export interface CommandResult {
  success: boolean;
  stdout: string;
  stderr: string;
  exitCode: number;
}

export async function runCrewAICommand(
  args: string[],
  cwd?: string,
  onOutput?: (data: string, isError: boolean) => void
): Promise<CommandResult> {
  try {
    const subprocess = execa(CREWAI_CMD, args, {
      cwd,
      env: { ...process.env, FORCE_COLOR: '1' },
      reject: false,
    });

    let stdout = '';
    let stderr = '';

    if (subprocess.stdout) {
      subprocess.stdout.on('data', (data: Buffer) => {
        const text = data.toString();
        stdout += text;
        onOutput?.(text, false);
      });
    }

    if (subprocess.stderr) {
      subprocess.stderr.on('data', (data: Buffer) => {
        const text = data.toString();
        stderr += text;
        onOutput?.(text, true);
      });
    }

    const result = await subprocess;

    return {
      success: result.exitCode === 0,
      stdout: result.stdout || stdout,
      stderr: result.stderr || stderr,
      exitCode: result.exitCode ?? 1,
    };
  } catch (error) {
    const err = error as Error;
    return {
      success: false,
      stdout: '',
      stderr: err.message,
      exitCode: 1,
    };
  }
}

export function spawnCrewAICommand(
  args: string[],
  cwd?: string
): ExecaChildProcess {
  return execa(CREWAI_CMD, args, {
    cwd,
    env: { ...process.env, FORCE_COLOR: '1' },
    reject: false,
  });
}

export async function discoverProjects(searchPath: string): Promise<CrewProject[]> {
  const projects: CrewProject[] = [];

  try {
    const entries = fs.readdirSync(searchPath, { withFileTypes: true });

    for (const entry of entries) {
      if (entry.isDirectory()) {
        const projectPath = path.join(searchPath, entry.name);
        const pyprojectPath = path.join(projectPath, 'pyproject.toml');

        if (fs.existsSync(pyprojectPath)) {
          const content = fs.readFileSync(pyprojectPath, 'utf-8');

          // Check if it's a crewAI project
          if (content.includes('[tool.crewai]')) {
            const typeMatch = content.match(/type\s*=\s*["'](\w+)["']/);
            const projectType = typeMatch?.[1] as 'crew' | 'flow' || 'crew';

            projects.push({
              name: entry.name,
              path: projectPath,
              type: projectType,
              config: {
                agents: path.join(projectPath, 'src', entry.name, 'config', 'agents.yaml'),
                tasks: path.join(projectPath, 'src', entry.name, 'config', 'tasks.yaml'),
              },
            });
          }
        }
      }
    }
  } catch {
    // Directory doesn't exist or not accessible
  }

  return projects;
}

export function loadAgentsConfig(configPath: string): Agent[] {
  try {
    if (!fs.existsSync(configPath)) {
      return [];
    }
    const content = fs.readFileSync(configPath, 'utf-8');
    const parsed = YAML.parse(content);

    return Object.entries(parsed || {}).map(([id, config]) => {
      const cfg = config as Record<string, unknown>;
      return {
        id,
        role: (cfg.role as string) || id,
        goal: (cfg.goal as string) || '',
        backstory: (cfg.backstory as string) || '',
        tools: cfg.tools as string[] | undefined,
        llm: cfg.llm as string | undefined,
        maxIter: cfg.max_iter as number | undefined,
        maxRpm: cfg.max_rpm as number | undefined,
        verbose: cfg.verbose as boolean | undefined,
        allowDelegation: cfg.allow_delegation as boolean | undefined,
        cacheEnabled: cfg.cache as boolean | undefined,
      };
    });
  } catch {
    return [];
  }
}

export function loadTasksConfig(configPath: string): Task[] {
  try {
    if (!fs.existsSync(configPath)) {
      return [];
    }
    const content = fs.readFileSync(configPath, 'utf-8');
    const parsed = YAML.parse(content);

    return Object.entries(parsed || {}).map(([id, config]) => {
      const cfg = config as Record<string, unknown>;
      return {
        id,
        description: (cfg.description as string) || '',
        expectedOutput: (cfg.expected_output as string) || '',
        agent: (cfg.agent as string) || '',
        tools: cfg.tools as string[] | undefined,
        asyncExecution: cfg.async_execution as boolean | undefined,
        context: cfg.context as string[] | undefined,
        outputFile: cfg.output_file as string | undefined,
        outputJson: cfg.output_json as string | undefined,
        outputPydantic: cfg.output_pydantic as string | undefined,
      };
    });
  } catch {
    return [];
  }
}

export async function createCrewProject(
  name: string,
  targetPath: string
): Promise<CommandResult> {
  return runCrewAICommand(['create', 'crew', name], targetPath);
}

export async function createFlowProject(
  name: string,
  targetPath: string
): Promise<CommandResult> {
  return runCrewAICommand(['create', 'flow', name], targetPath);
}

export async function runCrew(
  projectPath: string,
  inputs?: Record<string, string>,
  onOutput?: (data: string, isError: boolean) => void
): Promise<CommandResult> {
  const args = ['run'];

  if (inputs) {
    for (const [key, value] of Object.entries(inputs)) {
      args.push('--input', `${key}=${value}`);
    }
  }

  return runCrewAICommand(args, projectPath, onOutput);
}

export async function trainCrew(
  projectPath: string,
  iterations: number,
  filename: string,
  onOutput?: (data: string, isError: boolean) => void
): Promise<CommandResult> {
  return runCrewAICommand(
    ['train', '-n', iterations.toString(), '-f', filename],
    projectPath,
    onOutput
  );
}

export async function testCrew(
  projectPath: string,
  iterations: number,
  model?: string,
  onOutput?: (data: string, isError: boolean) => void
): Promise<CommandResult> {
  const args = ['test', '-n', iterations.toString()];
  if (model) {
    args.push('-m', model);
  }
  return runCrewAICommand(args, projectPath, onOutput);
}

export async function replayCrew(
  projectPath: string,
  taskId: string,
  onOutput?: (data: string, isError: boolean) => void
): Promise<CommandResult> {
  return runCrewAICommand(['replay', '-t', taskId], projectPath, onOutput);
}

export async function resetMemories(
  projectPath: string,
  all?: boolean,
  types?: string[]
): Promise<CommandResult> {
  const args = ['reset-memories'];
  if (all) {
    args.push('-a');
  }
  if (types) {
    for (const type of types) {
      args.push(`-${type[0]}`); // -s for short, -l for long, etc.
    }
  }
  return runCrewAICommand(args, projectPath);
}

export async function chatWithCrew(
  projectPath: string,
  onOutput?: (data: string, isError: boolean) => void
): Promise<ExecaChildProcess> {
  return spawnCrewAICommand(['chat'], projectPath);
}

export async function kickoffFlow(
  projectPath: string,
  onOutput?: (data: string, isError: boolean) => void
): Promise<CommandResult> {
  return runCrewAICommand(['kickoff'], projectPath, onOutput);
}

export async function plotFlow(projectPath: string): Promise<CommandResult> {
  return runCrewAICommand(['plot'], projectPath);
}

export function parseCrewOutput(output: string): {
  events: ExecutionEvent[];
  result?: string;
} {
  const events: ExecutionEvent[] = [];
  let result: string | undefined;

  const lines = output.split('\n');

  for (const line of lines) {
    // Parse different event types from output
    if (line.includes('Agent:') || line.includes('Task:')) {
      const eventType = line.includes('started') ? 'task_started' :
                       line.includes('completed') ? 'task_completed' : 'info';
      events.push({
        type: eventType,
        timestamp: new Date(),
        data: { message: line.trim() },
      });
    } else if (line.includes('Tool:')) {
      events.push({
        type: 'tool_usage',
        timestamp: new Date(),
        data: { message: line.trim() },
      });
    } else if (line.includes('Error') || line.includes('error')) {
      events.push({
        type: 'error',
        timestamp: new Date(),
        data: { message: line.trim() },
      });
    } else if (line.includes('Final Answer:') || line.includes('Result:')) {
      result = line.replace(/^(Final Answer:|Result:)\s*/, '').trim();
    }
  }

  return { events, result };
}

export function getProjectInputPlaceholders(projectPath: string): string[] {
  const placeholders: string[] = [];

  // Check tasks.yaml for {placeholder} patterns
  const tasksPath = path.join(projectPath, 'src', path.basename(projectPath), 'config', 'tasks.yaml');

  try {
    if (fs.existsSync(tasksPath)) {
      const content = fs.readFileSync(tasksPath, 'utf-8');
      const matches = content.matchAll(/\{(\w+)\}/g);
      for (const match of matches) {
        if (!placeholders.includes(match[1])) {
          placeholders.push(match[1]);
        }
      }
    }
  } catch {
    // Ignore errors
  }

  // Also check agents.yaml
  const agentsPath = path.join(projectPath, 'src', path.basename(projectPath), 'config', 'agents.yaml');

  try {
    if (fs.existsSync(agentsPath)) {
      const content = fs.readFileSync(agentsPath, 'utf-8');
      const matches = content.matchAll(/\{(\w+)\}/g);
      for (const match of matches) {
        if (!placeholders.includes(match[1])) {
          placeholders.push(match[1]);
        }
      }
    }
  } catch {
    // Ignore errors
  }

  return placeholders;
}
