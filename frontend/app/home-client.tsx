'use client';

import { useCallback, useRef, useState } from 'react';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';
import { ChatInterface, ChatInterfaceRef } from '@/components/chat/ChatInterface';
import { Conversation } from '@/lib/types';

export interface HomeClientProps {
  paymentSuccess?: boolean;
  sessionId?: string;
  liteapi?: string;
  transactionId?: string;
  prebookId?: string;
  conversationId?: string;
}

export default function HomeClient({
  paymentSuccess = false,
  sessionId,
  liteapi,
  transactionId,
  prebookId,
  conversationId,
}: HomeClientProps) {
  const chatRef = useRef<ChatInterfaceRef | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);

  const handleNewSearch = useCallback(() => {
    chatRef.current?.reset();
  }, []);

  const handleSelectConversation = useCallback((id: string) => {
    chatRef.current?.selectConversation(id);
  }, []);

  return (
    <div className="relative flex h-screen overflow-hidden bg-background">
      <Sidebar
        conversations={conversations}
        onNewSearch={handleNewSearch}
        onSelectConversation={handleSelectConversation}
      />

      <div className="relative flex min-w-0 flex-1 flex-col">
        <Header />

        <main className="relative flex-1 overflow-hidden">
          <ChatInterface
            ref={chatRef}
            onConversationsChange={setConversations}
            paymentSuccess={paymentSuccess}
            sessionId={sessionId}
            liteapi={liteapi}
            transactionId={transactionId}
            prebookId={prebookId}
            conversationId={conversationId}
          />
        </main>
      </div>
    </div>
  );
}
