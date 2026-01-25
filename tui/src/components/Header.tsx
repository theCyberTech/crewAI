import React from 'react';
import { Box, Text } from 'ink';

const LOGO = `
 ██████╗██████╗ ███████╗██╗    ██╗ █████╗ ██╗
██╔════╝██╔══██╗██╔════╝██║    ██║██╔══██╗██║
██║     ██████╔╝█████╗  ██║ █╗ ██║███████║██║
██║     ██╔══██╗██╔══╝  ██║███╗██║██╔══██║██║
╚██████╗██║  ██║███████╗╚███╔███╔╝██║  ██║██║
 ╚═════╝╚═╝  ╚═╝╚══════╝ ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝
`;

const MINI_LOGO = '🚀 CrewAI';

interface HeaderProps {
  showFullLogo?: boolean;
  subtitle?: string;
  showVersion?: boolean;
}

export function Header({ showFullLogo = false, subtitle, showVersion = true }: HeaderProps) {
  if (showFullLogo) {
    return (
      <Box flexDirection="column" alignItems="center" marginBottom={1}>
        <Text color="cyan">{LOGO}</Text>
        {subtitle && (
          <Text color="gray" italic>
            {subtitle}
          </Text>
        )}
        {showVersion && (
          <Text dimColor>
            AI Agent Framework • Terminal User Interface
          </Text>
        )}
      </Box>
    );
  }

  return (
    <Box
      flexDirection="row"
      justifyContent="space-between"
      alignItems="center"
      paddingX={1}
      marginBottom={1}
      borderStyle="single"
      borderColor="cyan"
    >
      <Box>
        <Text color="cyan" bold>
          {MINI_LOGO}
        </Text>
        {subtitle && (
          <Text color="gray"> • {subtitle}</Text>
        )}
      </Box>
      {showVersion && (
        <Text dimColor>v1.0.0</Text>
      )}
    </Box>
  );
}

interface BreadcrumbProps {
  items: string[];
}

export function Breadcrumb({ items }: BreadcrumbProps) {
  return (
    <Box marginBottom={1}>
      {items.map((item, index) => (
        <React.Fragment key={index}>
          <Text color={index === items.length - 1 ? 'white' : 'gray'} bold={index === items.length - 1}>
            {item}
          </Text>
          {index < items.length - 1 && (
            <Text color="gray"> › </Text>
          )}
        </React.Fragment>
      ))}
    </Box>
  );
}
