'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';

interface ChatInputProps {
  onSubmit: (message: string) => void;
  isLoading: boolean;
}

export function ChatInput({ onSubmit, isLoading }: ChatInputProps) {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = `${Math.min(el.scrollHeight, 140)}px`;
  }, [input]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const trimmed = input.trim();
    if (trimmed && !isLoading) {
      onSubmit(trimmed);
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as unknown as React.FormEvent);
    }
  };

  const canSend = input.trim().length > 0 && !isLoading;

  return (
    <form
      onSubmit={handleSubmit}
      className="flex items-end gap-2.5 rounded-2xl border border-border/70 bg-card px-3 py-2.5 shadow-sm focus-within:border-primary/50 focus-within:shadow-md focus-within:shadow-primary/5 transition-all duration-200"
    >
      <textarea
        ref={textareaRef}
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Message ttrip… (Shift+Enter for new line)"
        disabled={isLoading}
        rows={1}
        className="flex-1 resize-none bg-transparent text-sm text-foreground placeholder:text-muted-foreground/60 outline-none border-none min-h-[36px] max-h-[140px] py-1.5 leading-relaxed scrollbar-thin disabled:opacity-60"
        style={{ height: '36px' }}
      />

      <button
        type="submit"
        disabled={!canSend}
        className={`flex-shrink-0 h-9 w-9 rounded-xl flex items-center justify-center transition-all duration-200 ${
          canSend
            ? 'bg-primary text-primary-foreground shadow-sm hover:bg-primary/90 hover:shadow-md hover:shadow-primary/25 active:scale-90'
            : 'bg-muted text-muted-foreground cursor-not-allowed'
        }`}
      >
        {isLoading
          ? <Loader2 className="h-4 w-4 animate-spin" />
          : <Send className="h-4 w-4" />
        }
      </button>
    </form>
  );
}
