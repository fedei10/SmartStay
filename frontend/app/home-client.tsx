'use client';

import { useRef, useState } from 'react';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';
import { ChatInterface } from '@/components/chat/ChatInterface';
import { Conversation } from '@/lib/types';

export default function HomeClient() {
    const chatRef = useRef<{ reset: () => void; selectConversation: (id: string) => void }>(null);
    const [conversations, setConversations] = useState<Conversation[]>([]);

    return (
        <div className="flex h-screen bg-background overflow-hidden relative">
            <Sidebar
                conversations={conversations}
                onNewSearch={() => chatRef.current?.reset()}
                onSelectConversation={(id) => chatRef.current?.selectConversation(id)}
            />
            <div className="flex flex-col flex-1 w-full relative">
                <Header />
                <main className="flex-1 overflow-hidden relative">
                    <ChatInterface ref={chatRef} onConversationsChange={setConversations} />
                </main>
            </div>
        </div>
    );
}
