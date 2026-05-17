'use client';

import { Plus, HelpCircle, MessageSquare, Clock } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { Conversation } from '@/lib/types';

interface SidebarProps {
  conversations?: Conversation[];
  onNewSearch?: () => void;
  onSelectConversation?: (id: string) => void;
  activeConversationId?: string;
}

export function Sidebar({ conversations = [], onNewSearch, onSelectConversation, activeConversationId }: SidebarProps) {
  const router = useRouter();

  return (
    <aside className="hidden lg:flex flex-col w-60 border-r border-border/60 bg-background h-screen sticky top-0 scrollbar-thin overflow-y-auto">
      {/* Logo row */}
      <div className="flex items-center gap-2.5 px-5 h-14 border-b border-border/60 flex-shrink-0">
        <div className="relative w-7 h-7 flex items-center justify-center">
          <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-primary to-teal-600" />
          <svg className="relative h-3.5 w-3.5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
            <line x1="2" y1="12" x2="22" y2="12" />
          </svg>
        </div>
        <span className="font-bold text-sm text-foreground">ttrip</span>
      </div>

      {/* New trip button */}
      <div className="px-4 pt-4 pb-3 flex-shrink-0">
        <Button
          onClick={() => {
            onNewSearch?.();
            router.refresh();
          }}
          className="w-full rounded-xl bg-primary hover:bg-primary/90 text-primary-foreground gap-2 font-semibold h-9 text-sm shadow-sm hover:shadow-primary/25 hover:shadow-md transition-all duration-300"
        >
          <Plus className="h-4 w-4" />
          New trip
        </Button>
      </div>

      {/* Conversations */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-3 pb-4">
        <p className="text-[10px] font-bold uppercase tracking-widest text-muted-foreground/70 mb-2 px-2 pt-2">
          Recent
        </p>
        <nav className="space-y-0.5">
          {conversations.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-8 text-center px-4">
              <div className="h-10 w-10 rounded-full bg-secondary flex items-center justify-center mb-3">
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </div>
              <p className="text-xs text-muted-foreground">No trips yet. Start a new conversation.</p>
            </div>
          ) : (
            conversations.map((conv) => {
              const active = conv.id === activeConversationId;
              return (
                <button
                  key={conv.id}
                  onClick={() => onSelectConversation?.(conv.id)}
                  className={`w-full text-left px-3 py-2.5 rounded-xl transition-all duration-200 group ${
                    active
                      ? 'bg-primary/10 text-primary'
                      : 'text-muted-foreground hover:text-foreground hover:bg-secondary/60'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <MessageSquare className={`h-3.5 w-3.5 mt-0.5 flex-shrink-0 ${active ? 'text-primary' : 'text-muted-foreground/60 group-hover:text-muted-foreground'}`} />
                    <div className="min-w-0">
                      <p className="text-xs font-medium truncate leading-snug">{conv.title}</p>
                      <p className="text-[10px] text-muted-foreground/60 mt-0.5 flex items-center gap-1">
                        <Clock className="h-2.5 w-2.5" />
                        {new Date(conv.updatedAt).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                </button>
              );
            })
          )}
        </nav>
      </div>

      {/* Footer */}
      <div className="border-t border-border/60 p-3 flex-shrink-0">
        <Button
          variant="ghost"
          className="w-full justify-start rounded-xl gap-2 text-muted-foreground hover:text-foreground hover:bg-secondary/60 h-9 text-xs font-medium transition-colors"
        >
          <HelpCircle className="h-4 w-4" />
          Help & support
        </Button>
      </div>
    </aside>
  );
}
