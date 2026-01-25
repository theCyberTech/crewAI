import React from 'react';
import { Box as InkBox, Text } from 'ink';

interface BorderBoxProps {
  title?: string;
  children: React.ReactNode;
  width?: number | string;
  height?: number | string;
  padding?: number;
  borderColor?: string;
  borderStyle?: 'single' | 'double' | 'round' | 'bold' | 'singleDouble' | 'doubleSingle' | 'classic';
}

export function BorderBox({
  title,
  children,
  width,
  height,
  padding = 1,
  borderColor = 'cyan',
  borderStyle = 'round',
}: BorderBoxProps) {
  return (
    <InkBox
      flexDirection="column"
      width={width}
      height={height}
      borderStyle={borderStyle}
      borderColor={borderColor}
      paddingX={padding}
    >
      {title && (
        <InkBox marginBottom={1}>
          <Text bold color={borderColor}>
            {title}
          </Text>
        </InkBox>
      )}
      {children}
    </InkBox>
  );
}

interface CardProps {
  children: React.ReactNode;
  marginBottom?: number;
}

export function Card({ children, marginBottom = 0 }: CardProps) {
  return (
    <InkBox
      flexDirection="column"
      marginBottom={marginBottom}
      paddingX={1}
      borderStyle="single"
      borderColor="gray"
    >
      {children}
    </InkBox>
  );
}

interface RowProps {
  children: React.ReactNode;
  gap?: number;
  alignItems?: 'flex-start' | 'center' | 'flex-end' | 'stretch';
  justifyContent?: 'flex-start' | 'center' | 'flex-end' | 'space-between' | 'space-around';
}

export function Row({ children, gap = 1, alignItems = 'center', justifyContent = 'flex-start' }: RowProps) {
  return (
    <InkBox flexDirection="row" alignItems={alignItems} justifyContent={justifyContent} gap={gap}>
      {children}
    </InkBox>
  );
}

interface ColumnProps {
  children: React.ReactNode;
  gap?: number;
  alignItems?: 'flex-start' | 'center' | 'flex-end' | 'stretch';
}

export function Column({ children, gap = 0, alignItems = 'stretch' }: ColumnProps) {
  return (
    <InkBox flexDirection="column" alignItems={alignItems} gap={gap}>
      {children}
    </InkBox>
  );
}

interface SpacerProps {
  size?: number;
}

export function Spacer({ size = 1 }: SpacerProps) {
  return <InkBox marginY={size} />;
}

interface DividerProps {
  char?: string;
  color?: string;
}

export function Divider({ char = '─', color = 'gray' }: DividerProps) {
  return (
    <InkBox marginY={1}>
      <Text color={color}>{char.repeat(60)}</Text>
    </InkBox>
  );
}
