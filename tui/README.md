# CrewAI TUI

A modern Terminal User Interface for CrewAI, built with [Ink](https://github.com/vadimdemedes/ink) (React for CLIs).

Similar to Claude Code, Codex, and Gemini CLI, this TUI provides an interactive and visually appealing way to manage and execute your CrewAI projects directly from the terminal.

## Features

- 🏠 **Dashboard** - Overview of your CrewAI projects
- 👥 **Crew Management** - Browse, create, and run crews
- 🔄 **Flow Orchestration** - Manage and execute flows
- 💬 **Interactive Chat** - Chat with your crew in real-time
- 🤖 **Agent Viewer** - View agent configurations
- 📋 **Task Viewer** - View task configurations
- 🧠 **Memory Management** - View and clear crew memory
- ⚡ **Real-time Execution** - Watch crews run with live output
- ⚙️ **Settings** - Configure TUI preferences

## Installation

```bash
cd tui
npm install
npm run build
```

## Usage

```bash
# Run the TUI
npm start

# Or after global installation
crewai-tui

# Start on a specific screen
crewai-tui --screen crews

# Open with a specific project
crewai-tui --project ./my-crew
```

## Keyboard Shortcuts

### Global
| Key | Action |
|-----|--------|
| `q` | Quit (from home screen) |
| `h` | Open help |
| `Esc` | Go back |

### Navigation
| Key | Action |
|-----|--------|
| `↑`/`↓` | Navigate lists |
| `←`/`→` | Switch tabs / Adjust values |
| `Enter` | Select / Confirm |
| `Tab` | Next field (in forms) |

### Quick Actions
| Key | Action |
|-----|--------|
| `c` | Create new crew/flow |
| `r` | Run crew/flow |
| `s` | Select project |
| `t` | Run tests |

## Screens

### Home
The main dashboard showing:
- Available projects (crews and flows)
- Quick actions
- Currently selected project

### Crews
Browse and manage your crew projects:
- View crew details
- See agents and tasks
- Run crews with inputs

### Flows
Manage flow-based orchestration:
- View flow details
- Run flows
- Generate flow diagrams

### Chat
Interactive chat interface:
- Real-time conversation with your crew
- Streaming responses
- Session management

### Agents
View agent configurations:
- Role, goal, backstory
- Tools and LLM settings
- Execution parameters

### Tasks
View task definitions:
- Description and expected output
- Agent assignments
- Context dependencies

### Memory
Manage crew memory:
- Short-term memory (execution context)
- Long-term memory (persistent knowledge)
- Entity memory (tracked entities)

### Settings
Configure TUI preferences:
- Theme (dark/light)
- Verbose output
- Token usage display
- Event history limit

## Architecture

```
tui/
├── src/
│   ├── cli.tsx              # CLI entry point
│   ├── App.tsx              # Main application component
│   ├── components/          # Reusable UI components
│   │   ├── Box.tsx          # Layout components
│   │   ├── Header.tsx       # Header and breadcrumbs
│   │   ├── StatusBar.tsx    # Status bar and progress
│   │   ├── Menu.tsx         # Navigation menus
│   │   ├── AgentCard.tsx    # Agent display
│   │   ├── TaskCard.tsx     # Task display
│   │   ├── EventLog.tsx     # Execution event log
│   │   └── Input.tsx        # Form inputs
│   ├── screens/             # Screen components
│   │   ├── HomeScreen.tsx
│   │   ├── CrewsScreen.tsx
│   │   ├── CrewRunScreen.tsx
│   │   ├── FlowsScreen.tsx
│   │   ├── ChatScreen.tsx
│   │   ├── AgentsScreen.tsx
│   │   ├── TasksScreen.tsx
│   │   ├── HelpScreen.tsx
│   │   ├── SettingsScreen.tsx
│   │   └── MemoryScreen.tsx
│   ├── hooks/
│   │   └── useStore.ts      # Global state management (Zustand)
│   ├── utils/
│   │   └── crewai.ts        # CrewAI CLI integration
│   └── types/
│       └── index.ts         # TypeScript type definitions
├── package.json
├── tsconfig.json
└── README.md
```

## Development

```bash
# Watch mode for development
npm run dev

# Type checking
npm run typecheck

# Build
npm run build

# Clean build artifacts
npm run clean
```

## Requirements

- Node.js >= 18
- CrewAI CLI installed (`pip install crewai`)
- A terminal that supports ANSI colors and Unicode

## License

MIT
