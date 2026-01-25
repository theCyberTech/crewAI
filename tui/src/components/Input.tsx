import React, { useState } from 'react';
import { Box, Text, useInput } from 'ink';
import TextInput from 'ink-text-input';

interface InputFieldProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  onSubmit?: (value: string) => void;
  placeholder?: string;
  isActive?: boolean;
  multiline?: boolean;
}

export function InputField({
  label,
  value,
  onChange,
  onSubmit,
  placeholder = '',
  isActive = true,
}: InputFieldProps) {
  return (
    <Box flexDirection="column" marginBottom={1}>
      <Text color="cyan">{label}:</Text>
      <Box borderStyle={isActive ? 'single' : 'single'} borderColor={isActive ? 'cyan' : 'gray'} paddingX={1}>
        {isActive ? (
          <TextInput
            value={value}
            onChange={onChange}
            onSubmit={onSubmit}
            placeholder={placeholder}
          />
        ) : (
          <Text color={value ? 'white' : 'gray'}>{value || placeholder}</Text>
        )}
      </Box>
    </Box>
  );
}

interface FormField {
  name: string;
  label: string;
  placeholder?: string;
  required?: boolean;
  value?: string;
}

interface FormProps {
  fields: FormField[];
  onSubmit: (values: Record<string, string>) => void;
  onCancel?: () => void;
  submitLabel?: string;
}

export function Form({ fields, onSubmit, onCancel, submitLabel = 'Submit' }: FormProps) {
  const [values, setValues] = useState<Record<string, string>>(
    Object.fromEntries(fields.map((f) => [f.name, f.value || '']))
  );
  const [activeFieldIndex, setActiveFieldIndex] = useState(0);
  const [isSubmitFocused, setIsSubmitFocused] = useState(false);

  const handleFieldChange = (name: string, value: string) => {
    setValues((prev) => ({ ...prev, [name]: value }));
  };

  const handleFieldSubmit = () => {
    if (activeFieldIndex < fields.length - 1) {
      setActiveFieldIndex(activeFieldIndex + 1);
    } else {
      setIsSubmitFocused(true);
    }
  };

  useInput((input, key) => {
    if (key.tab) {
      if (isSubmitFocused) {
        setIsSubmitFocused(false);
        setActiveFieldIndex(0);
      } else if (activeFieldIndex < fields.length - 1) {
        setActiveFieldIndex(activeFieldIndex + 1);
      } else {
        setIsSubmitFocused(true);
      }
    } else if (key.escape && onCancel) {
      onCancel();
    } else if (key.return && isSubmitFocused) {
      const allRequiredFilled = fields
        .filter((f) => f.required)
        .every((f) => values[f.name] && values[f.name]!.trim().length > 0);

      if (allRequiredFilled) {
        onSubmit(values);
      }
    }
  });

  return (
    <Box flexDirection="column">
      {fields.map((field, index) => (
        <InputField
          key={field.name}
          label={`${field.label}${field.required ? ' *' : ''}`}
          value={values[field.name] || ''}
          onChange={(value) => handleFieldChange(field.name, value)}
          onSubmit={handleFieldSubmit}
          placeholder={field.placeholder}
          isActive={!isSubmitFocused && activeFieldIndex === index}
        />
      ))}

      <Box marginTop={1} gap={2}>
        <Box
          borderStyle={isSubmitFocused ? 'double' : 'single'}
          borderColor={isSubmitFocused ? 'green' : 'gray'}
          paddingX={2}
        >
          <Text color={isSubmitFocused ? 'green' : 'white'} bold={isSubmitFocused}>
            {submitLabel}
          </Text>
        </Box>
        {onCancel && (
          <Box borderStyle="single" borderColor="gray" paddingX={2}>
            <Text dimColor>Cancel (Esc)</Text>
          </Box>
        )}
      </Box>

      <Box marginTop={1}>
        <Text dimColor>Tab to navigate • Enter to submit</Text>
      </Box>
    </Box>
  );
}

interface ConfirmDialogProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
  confirmLabel?: string;
  cancelLabel?: string;
  isDangerous?: boolean;
}

export function ConfirmDialog({
  message,
  onConfirm,
  onCancel,
  confirmLabel = 'Yes',
  cancelLabel = 'No',
  isDangerous = false,
}: ConfirmDialogProps) {
  const [selected, setSelected] = useState<'confirm' | 'cancel'>('cancel');

  useInput((input, key) => {
    if (key.leftArrow || key.rightArrow) {
      setSelected((prev) => (prev === 'confirm' ? 'cancel' : 'confirm'));
    } else if (key.return) {
      if (selected === 'confirm') {
        onConfirm();
      } else {
        onCancel();
      }
    } else if (key.escape) {
      onCancel();
    } else if (input === 'y' || input === 'Y') {
      onConfirm();
    } else if (input === 'n' || input === 'N') {
      onCancel();
    }
  });

  return (
    <Box
      flexDirection="column"
      borderStyle="round"
      borderColor={isDangerous ? 'red' : 'yellow'}
      paddingX={2}
      paddingY={1}
    >
      <Text color={isDangerous ? 'red' : 'yellow'}>{message}</Text>
      <Box marginTop={1} gap={2}>
        <Box
          borderStyle={selected === 'confirm' ? 'double' : 'single'}
          borderColor={selected === 'confirm' ? (isDangerous ? 'red' : 'green') : 'gray'}
          paddingX={2}
        >
          <Text color={selected === 'confirm' ? (isDangerous ? 'red' : 'green') : 'white'}>
            {confirmLabel} (Y)
          </Text>
        </Box>
        <Box
          borderStyle={selected === 'cancel' ? 'double' : 'single'}
          borderColor={selected === 'cancel' ? 'cyan' : 'gray'}
          paddingX={2}
        >
          <Text color={selected === 'cancel' ? 'cyan' : 'white'}>
            {cancelLabel} (N)
          </Text>
        </Box>
      </Box>
    </Box>
  );
}

interface ChatInputProps {
  onSend: (message: string) => void;
  placeholder?: string;
  isDisabled?: boolean;
}

export function ChatInput({ onSend, placeholder = 'Type a message...', isDisabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('');

  const handleSubmit = () => {
    if (message.trim() && !isDisabled) {
      onSend(message.trim());
      setMessage('');
    }
  };

  return (
    <Box
      borderStyle="round"
      borderColor={isDisabled ? 'gray' : 'cyan'}
      paddingX={1}
    >
      <Text color="cyan">{'> '}</Text>
      <TextInput
        value={message}
        onChange={setMessage}
        onSubmit={handleSubmit}
        placeholder={isDisabled ? 'Waiting...' : placeholder}
      />
    </Box>
  );
}
