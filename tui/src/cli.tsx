#!/usr/bin/env node
import React from 'react';
import { render } from 'ink';
import meow from 'meow';
import { App } from './App.js';
import type { Screen } from './types/index.js';

const cli = meow(
  `
  Usage
    $ crewai-tui [options]

  Options
    --screen, -s    Start on a specific screen (home, crews, flows, chat, help)
    --project, -p   Path to a CrewAI project
    --version, -v   Show version number
    --help, -h      Show this help message

  Examples
    $ crewai-tui
    $ crewai-tui --screen crews
    $ crewai-tui --project ./my-crew
    $ crewai-tui -s chat -p ./my-crew

  Keyboard Shortcuts
    q          Quit (from home screen)
    h          Help
    Esc        Go back
    ↑↓         Navigate
    Enter      Select
    Tab        Next field

  For more information, visit:
    https://docs.crewai.com
`,
  {
    importMeta: import.meta,
    flags: {
      screen: {
        type: 'string',
        shortFlag: 's',
        default: 'home',
      },
      project: {
        type: 'string',
        shortFlag: 'p',
      },
      version: {
        type: 'boolean',
        shortFlag: 'v',
      },
    },
  }
);

const validScreens: Screen[] = [
  'home',
  'crews',
  'flows',
  'chat',
  'agents',
  'tasks',
  'memory',
  'settings',
  'help',
];

const initialScreen = validScreens.includes(cli.flags.screen as Screen)
  ? (cli.flags.screen as Screen)
  : 'home';

// Clear console for clean start
console.clear();

// Render the app
const { waitUntilExit } = render(
  <App initialScreen={initialScreen} projectPath={cli.flags.project} />
);

// Wait for app to exit
waitUntilExit().then(() => {
  console.log('\n👋 Thanks for using CrewAI TUI!\n');
});
