import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';

export interface MenuItem {
  label: string;
  value: string;
  icon?: string;
  description?: string;
  disabled?: boolean;
}

interface MenuProps {
  items: MenuItem[];
  onSelect: (value: string) => void;
  title?: string;
  showIcons?: boolean;
  showDescriptions?: boolean;
  columns?: number;
}

export function Menu({
  items,
  onSelect,
  title,
  showIcons = true,
  showDescriptions = true,
  columns = 1,
}: MenuProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const enabledItems = items.filter((item) => !item.disabled);
  const itemsPerColumn = Math.ceil(enabledItems.length / columns);

  useInput((input, key) => {
    if (key.upArrow) {
      setSelectedIndex((prev) => (prev > 0 ? prev - 1 : enabledItems.length - 1));
    } else if (key.downArrow) {
      setSelectedIndex((prev) => (prev < enabledItems.length - 1 ? prev + 1 : 0));
    } else if (key.leftArrow && columns > 1) {
      setSelectedIndex((prev) => {
        const newIndex = prev - itemsPerColumn;
        return newIndex >= 0 ? newIndex : prev;
      });
    } else if (key.rightArrow && columns > 1) {
      setSelectedIndex((prev) => {
        const newIndex = prev + itemsPerColumn;
        return newIndex < enabledItems.length ? newIndex : prev;
      });
    } else if (key.return) {
      const selectedItem = enabledItems[selectedIndex];
      if (selectedItem) {
        onSelect(selectedItem.value);
      }
    } else {
      // Check for number shortcuts
      const num = parseInt(input, 10);
      if (!isNaN(num) && num >= 1 && num <= enabledItems.length) {
        setSelectedIndex(num - 1);
        onSelect(enabledItems[num - 1]!.value);
      }
    }
  });

  const renderItem = (item: MenuItem, index: number, globalIndex: number) => {
    const isSelected = globalIndex === selectedIndex;

    return (
      <Box key={item.value} flexDirection="column" marginBottom={showDescriptions ? 1 : 0}>
        <Box>
          <Text color={isSelected ? 'cyan' : 'white'}>
            {isSelected ? '❯ ' : '  '}
          </Text>
          {showIcons && item.icon && (
            <Text>{item.icon} </Text>
          )}
          <Text color={item.disabled ? 'gray' : isSelected ? 'cyan' : 'white'} bold={isSelected}>
            {item.label}
          </Text>
          <Text dimColor> [{globalIndex + 1}]</Text>
        </Box>
        {showDescriptions && item.description && (
          <Box marginLeft={4}>
            <Text dimColor>{item.description}</Text>
          </Box>
        )}
      </Box>
    );
  };

  if (columns === 1) {
    return (
      <Box flexDirection="column">
        {title && (
          <Box marginBottom={1}>
            <Text bold color="yellow">
              {title}
            </Text>
          </Box>
        )}
        {enabledItems.map((item, index) => renderItem(item, index, index))}
      </Box>
    );
  }

  // Multi-column layout
  const columnItems: MenuItem[][] = [];
  for (let i = 0; i < columns; i++) {
    columnItems.push(enabledItems.slice(i * itemsPerColumn, (i + 1) * itemsPerColumn));
  }

  return (
    <Box flexDirection="column">
      {title && (
        <Box marginBottom={1}>
          <Text bold color="yellow">
            {title}
          </Text>
        </Box>
      )}
      <Box flexDirection="row" gap={4}>
        {columnItems.map((colItems, colIndex) => (
          <Box key={colIndex} flexDirection="column">
            {colItems.map((item, index) => {
              const globalIndex = colIndex * itemsPerColumn + index;
              return renderItem(item, index, globalIndex);
            })}
          </Box>
        ))}
      </Box>
    </Box>
  );
}

interface TabsProps {
  tabs: { label: string; value: string }[];
  activeTab: string;
  onTabChange: (value: string) => void;
}

export function Tabs({ tabs, activeTab, onTabChange }: TabsProps) {
  useInput((input, key) => {
    const currentIndex = tabs.findIndex((tab) => tab.value === activeTab);
    if (key.leftArrow && currentIndex > 0) {
      onTabChange(tabs[currentIndex - 1]!.value);
    } else if (key.rightArrow && currentIndex < tabs.length - 1) {
      onTabChange(tabs[currentIndex + 1]!.value);
    }
  });

  return (
    <Box gap={1} marginBottom={1}>
      {tabs.map((tab) => (
        <Box key={tab.value}>
          <Text
            color={tab.value === activeTab ? 'cyan' : 'gray'}
            bold={tab.value === activeTab}
            underline={tab.value === activeTab}
          >
            {tab.label}
          </Text>
          <Text color="gray"> | </Text>
        </Box>
      ))}
    </Box>
  );
}
