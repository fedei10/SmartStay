'use client';

import { Plus, Map, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useRouter } from 'next/navigation';
import { Conversation } from '@/lib/types';

interface SidebarProps {
  conversations?: Conversation[];
  onNewSearch?: () => void;
  onSelectConversation?: (id: string) => void;
}

export function Sidebar({ conversations = [], onNewSearch, onSelectConversation }: SidebarProps) {
  const router = useRouter();

  return (
    <aside className="hidden lg:flex flex-col w-64 border-r border-border bg-background h-screen sticky top-0 overflow-y-auto">
      <div className="p-6 border-b border-border">
        <Button
          onClick={() => {
            if (onNewSearch) onNewSearch();
            router.refresh();
          }}
          className="w-full rounded-lg bg-primary hover:bg-primary/90 text-primary-foreground gap-2 font-medium transition-all"
        >
          <Plus className="h-4 w-4" />
          New trip
        </Button>
      </div>

      <div className="flex-1 overflow-y-auto px-4 py-6">
        <div className="mb-8">
          <h3 className="text-xs font-bold uppercase tracking-widest text-foreground/50 mb-4 px-2">
            Recent plans
          </h3>
          <nav className="space-y-1">
            {conversations.length === 0 ? (
              <div className="px-3 py-3 text-sm text-muted-foreground">
                No trip searches yet.
              </div>
            ) : (
              conversations.map((conv) => (
                <button
                  key={conv.id}
                  onClick={() => onSelectConversation?.(conv.id)}
                  className="w-full text-left px-3 py-3 rounded-lg hover:bg-secondary transition-colors text-sm text-foreground/75 hover:text-foreground group"
                >
                  <div className="font-medium truncate group-hover:text-primary transition-colors">
                    {conv.title}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {new Date(conv.updatedAt).toLocaleString()}
                  </div>
                </button>
              ))
            )}
          </nav>
        </div>
      </div>

      <div className="border-t border-border p-4 space-y-1">
        <Button
          variant="ghost"
          className="w-full justify-start rounded-lg gap-2 text-foreground/70 hover:text-foreground hover:bg-secondary transition-colors"
        >
          <Map className="h-4 w-4" />
          Trip board
        </Button>
        <Button
          variant="ghost"
          className="w-full justify-start rounded-lg gap-2 text-foreground/70 hover:text-foreground hover:bg-secondary transition-colors"
        >
          <HelpCircle className="h-4 w-4" />
          Help
        </Button>
      </div>
    </aside>
  );
}
