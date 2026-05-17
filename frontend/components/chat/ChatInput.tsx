'use client';

import { useState } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';

interface ChatInputProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSubmit, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSubmit(input);
      setInput('');
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <Input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Message ttrip..."
        disabled={isLoading}
        className="flex-1 text-sm rounded-xl"
      />
      <Button
        type="submit"
        disabled={isLoading || !input.trim()}
        size="icon"
        className="rounded-xl h-11 px-4 bg-primary hover:bg-primary/90 text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-soft hover:shadow-soft-lg active:scale-95"
      >
        <Send className="h-4 w-4" />
      </Button>
    </form>
  );
}
