'use client';

import { useState, useRef, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/nextjs';
import { Message, ChatResponse as APIResponse, Conversation } from '@/lib/types';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { Loader2 } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';
import { useSearchParams } from 'next/navigation';

import { useImperativeHandle, forwardRef } from 'react';

interface ChatInterfaceProps {
  initialMessage?: string;
  onConversationsChange?: (conversations: Conversation[]) => void;
}

interface ConversationSummary {
  id: string;
  title: string;
  updatedAt: string;
}

const MAX_CONVERSATIONS = 20;
const INTERNAL_PAYMENT_VERIFIED_MESSAGE = '__internal_payment_verified__';
const LEGACY_ENGLISH_WELCOME_SNIPPETS = [
  'welcome to stayai',
  'welcome to ttrip',
  'مرحبًا بك في ttrip',
  "i'm your personal hotel booking assistant",
  'try asking me things like',
  'what kind of hotel are you looking for',
  'حدثت مشكلة أثناء معالجة طلبك',
  'do you want help with hotels, flights, travel insurance, or a combined trip',
  'i need the city or destination, country before i can search hotels',
  'i can help with travel planning, but booking actions should go through',
  'i will plan hotels, flights',
];

interface SendMessageOptions {
  silentUserMessage?: boolean;
  paymentCompleted?: boolean;
  paymentTransactionId?: string;
  paymentPrebookId?: string;
}

const isLegacyEnglishWelcomeMessage = (message: Message): boolean => {
  if (message.role !== 'assistant') return false;
  const text = (message.content || '').toLowerCase();
  return LEGACY_ENGLISH_WELCOME_SNIPPETS.some((snippet) => text.includes(snippet));
};

const detectFallbackLanguage = (value: string): 'ar' | 'en' => {
  if (/[\u0600-\u06ff]/.test(value)) return 'ar';
  return 'en';
};

const fallbackErrorMessage = (value: string): string => {
  if (detectFallbackLanguage(value) === 'ar') {
    return 'لم يصل رد من ttrip. تحقق من الاتصال وحاول مرة أخرى.';
  }
  return 'ttrip did not return a response. Check the connection and try again.';
};

export const ChatInterface = forwardRef(({ onConversationsChange }: ChatInterfaceProps, ref) => {
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();
  const searchParams = useSearchParams();
  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [initialized, setInitialized] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  const summariesKey = user ? `ttrip:conversations:${user.id}` : '';
  const activeConversationKey = user ? `ttrip:active_conversation:${user.id}` : '';
  const conversationMessagesKey = (id: string) => (user ? `ttrip:messages:${user.id}:${id}` : '');

  const toConversationList = (items: ConversationSummary[]): Conversation[] =>
    items.map((item) => ({
      id: item.id,
      title: item.title,
      createdAt: new Date(item.updatedAt),
      updatedAt: new Date(item.updatedAt),
      messageCount: 0,
    }));


  const loadSummaries = (): ConversationSummary[] => {
    if (!summariesKey) return [];
    try {
      const raw = localStorage.getItem(summariesKey);
      if (!raw) return [];
      const parsed = JSON.parse(raw) as ConversationSummary[];
      return Array.isArray(parsed) ? parsed : [];
    } catch {
      return [];
    }
  };

  const saveSummaries = (items: ConversationSummary[]) => {
    if (!summariesKey) return;
    localStorage.setItem(summariesKey, JSON.stringify(items.slice(0, MAX_CONVERSATIONS)));
    onConversationsChange?.(toConversationList(items.slice(0, MAX_CONVERSATIONS)));
  };

  const loadMessages = (id: string): Message[] => {
    const key = conversationMessagesKey(id);
    if (!key) return [];
    try {
      const raw = localStorage.getItem(key);
      if (!raw) return [];
      const parsed = JSON.parse(raw) as Array<Omit<Message, 'timestamp'> & { timestamp: string }>;
      if (!Array.isArray(parsed)) return [];
      const restored = parsed.map((m) => ({ ...m, timestamp: new Date(m.timestamp) }));
      const cleaned = restored.filter((m) => !isLegacyEnglishWelcomeMessage(m));
      return cleaned;
    } catch {
      return [];
    }
  };

  const saveMessages = (id: string, value: Message[]) => {
    const key = conversationMessagesKey(id);
    if (!key) return;
    localStorage.setItem(
      key,
      JSON.stringify(value.map((m) => ({ ...m, timestamp: m.timestamp.toISOString() })))
    );
  };

  const buildTitle = (value: Message[]) => {
    const firstUserMessage = value.find((m) => m.role === 'user')?.content?.trim();
    if (!firstUserMessage) return 'New trip';
    return firstUserMessage.length > 50
      ? `${firstUserMessage.slice(0, 50)}...`
      : firstUserMessage;
  };

  const upsertConversationSummary = (id: string, value: Message[]) => {
    const summaries = loadSummaries();
    const updatedSummary: ConversationSummary = {
      id,
      title: buildTitle(value),
      updatedAt: new Date().toISOString(),
    };
    const next = [updatedSummary, ...summaries.filter((s) => s.id !== id)];
    saveSummaries(next);
  };

  const startNewConversation = () => {
    const id = uuidv4();
    setConversationId(id);
    setMessages([]);
    if (activeConversationKey) {
      localStorage.setItem(activeConversationKey, id);
    }
  };

  const selectConversation = (id: string) => {
    const stored = loadMessages(id);
    if (stored.length === 0) {
      startNewConversation();
      return;
    }
    setConversationId(id);
    setMessages(stored);
    if (activeConversationKey) {
      localStorage.setItem(activeConversationKey, id);
    }
  };

  useImperativeHandle(ref, () => ({
    reset: () => {
      startNewConversation();
    },
    selectConversation: (id: string) => {
      selectConversation(id);
    },
  }));

  // Initialize from persisted conversation state.
  useEffect(() => {
    if (!isLoaded || !user || initialized) return;

    const summaries = loadSummaries();
    onConversationsChange?.(toConversationList(summaries));

    if (summaries.length === 0) {
      startNewConversation();
      setInitialized(true);
      return;
    }

    const activeId = activeConversationKey ? localStorage.getItem(activeConversationKey) : null;
    const selectedId = activeId && summaries.some((s) => s.id === activeId) ? activeId : summaries[0].id;
    const storedMessages = loadMessages(selectedId);

    if (storedMessages.length > 0) {
      setConversationId(selectedId);
      setMessages(storedMessages);
      if (activeConversationKey) {
        localStorage.setItem(activeConversationKey, selectedId);
      }
    } else {
      startNewConversation();
    }

    setInitialized(true);
  }, [isLoaded, user, initialized, onConversationsChange]);

  useEffect(() => {
    if (!initialized || !user || !conversationId || messages.length === 0) return;
    saveMessages(conversationId, messages);
    upsertConversationSummary(conversationId, messages);
    if (activeConversationKey) {
      localStorage.setItem(activeConversationKey, conversationId);
    }
  }, [messages, conversationId, initialized, user]);

  // If user returns from Stripe with success params, auto-continue the booking flow.
  useEffect(() => {
    if (!initialized || !isLoaded || !user) return;
    const convoFromReturn = searchParams.get('conversation_id');
    if (!convoFromReturn || convoFromReturn === conversationId) return;

    const storedMessages = loadMessages(convoFromReturn);
    if (storedMessages.length > 0) {
      setConversationId(convoFromReturn);
      setMessages(storedMessages);
      if (activeConversationKey) {
        localStorage.setItem(activeConversationKey, convoFromReturn);
      }
    }
  }, [initialized, isLoaded, user, conversationId, searchParams]);

  // If user returns from payment success params, auto-continue the booking flow.
  useEffect(() => {
    if (!initialized || !isLoaded || !user || !conversationId || isLoading) return;

    const paymentSuccess = searchParams.get('payment_success');
    const sessionId = searchParams.get('session_id');
    const liteapi = searchParams.get('liteapi');
    const liteTransactionId = searchParams.get('transaction_id');
    const litePrebookId = searchParams.get('prebook_id');

    if (paymentSuccess !== '1') return;

    const dedupeId = sessionId || liteTransactionId || 'unknown';
    const dedupeKey = `ttrip:payment_processed:${dedupeId}`;
    if (sessionStorage.getItem(dedupeKey)) return;
    sessionStorage.setItem(dedupeKey, '1');

    const clearPaymentParams = () => {
      const currentUrl = new URL(window.location.href);
      currentUrl.searchParams.delete('payment_success');
      currentUrl.searchParams.delete('session_id');
      currentUrl.searchParams.delete('liteapi');
      currentUrl.searchParams.delete('transaction_id');
      currentUrl.searchParams.delete('prebook_id');
      currentUrl.searchParams.delete('conversation_id');
      const cleanUrl = `${currentUrl.pathname}${currentUrl.search}${currentUrl.hash}`;
      window.history.replaceState({}, '', cleanUrl);
    };

    const appendAssistantNotice = (content: string) => {
      const noticeMessage: Message = {
        id: (Date.now() + 2).toString(),
        role: 'assistant',
        content,
        timestamp: new Date(),
        metadata: { type: 'error' }
      };
      setMessages((prev) => [...prev, noticeMessage]);
    };

    const verifyAndContinue = async () => {
      try {
        if (liteapi === '1' && liteTransactionId) {
          await handleSendMessage(INTERNAL_PAYMENT_VERIFIED_MESSAGE, {
            silentUserMessage: true,
            paymentCompleted: true,
            paymentTransactionId: liteTransactionId,
            paymentPrebookId: litePrebookId || undefined,
          });
          clearPaymentParams();
          return;
        }

        if (!sessionId) {
          throw new Error('Missing payment callback identifiers');
        }

        await handleSendMessage(`Payment completed for session ${sessionId}. Continue the booking if the backend has enough context.`, {
          silentUserMessage: true,
        });
        clearPaymentParams();
      } catch (error) {
        console.error('[ttrip] Payment continuation error:', error);
        sessionStorage.removeItem(dedupeKey);
        appendAssistantNotice(
          'تعذر التحقق من الدفع الآن. أعد المحاولة من صفحة النجاح، أو اكتب "لقد دفعت" بعد تأكيد الدفع.'
        );
      }
    };

    void verifyAndContinue();
  }, [initialized, isLoaded, user, conversationId, isLoading, searchParams]);

  // Auto scroll to bottom
  useEffect(() => {
    const scrollContainer = scrollRef.current?.parentElement;
    if (scrollContainer) {
      setTimeout(() => {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }, 0);
    }
  }, [messages]);

  const handleSendMessage = async (userInput: string, options?: SendMessageOptions) => {
    if (!user || !isLoaded) return;

    if (!options?.silentUserMessage) {
      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: userInput,
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, userMessage]);
    }
    setIsLoading(true);

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Failed to get authentication token');
      }

      const response = await fetch('/api/v1/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: userInput,
          conversation_id: conversationId,
        }),
      });

      const data: APIResponse & { error?: string; message?: string; detail?: unknown } =
        await response.json().catch(() => ({}));

      if (!response.ok) {
        console.error('[ttrip] Backend chat error:', response.status, data);
        throw new Error(
          data.error ||
          data.message ||
          (typeof data.detail === 'string' ? data.detail : `Server error: ${response.status}`)
        );
      }

      console.log('[ttrip] Received data:', data);

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: String(data.response || ''),
        timestamp: new Date(),
        metadata: {
          type: (Array.isArray(data.hotels) && data.hotels.length > 0) ? 'hotel-results' :
            (data.payment_url || data.payment_sdk_secret_key) ? 'payment-link' : 'text',
          hotels: Array.isArray(data.hotels) ? data.hotels : [],
          payment_url: data.payment_url,
          payment_sdk_secret_key: data.payment_sdk_secret_key,
          payment_sdk_public_key: data.payment_sdk_public_key,
          payment_transaction_id: data.payment_transaction_id,
          payment_prebook_id: data.payment_prebook_id,
          booking_status: data.booking_status,
          state: data.state,
          conversation_id: data.conversation_id || conversationId,
        },
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('[ttrip] Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: fallbackErrorMessage(userInput),
        timestamp: new Date(),
        metadata: { type: 'error' }
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSelectHotel = async (selection: number) => {
    if (isLoading) return;
    await handleSendMessage(String(selection));
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-1">
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              message={message}
              onSelectHotel={handleSelectHotel}
              isLoading={isLoading}
            />
          ))}

          {messages.length === 0 && !isLoading && (
            <div className="flex min-h-[55vh] flex-col items-center justify-center text-center">
              <h1 className="text-3xl font-bold tracking-tight text-foreground sm:text-4xl">
                What trip are we planning?
              </h1>
              <p className="mt-3 max-w-md text-sm text-muted-foreground">
                Ask about hotels, flights, travel dates, budgets, or a full itinerary.
              </p>
            </div>
          )}

          {isLoading && (
            <div className="flex justify-start mb-4 animate-fade-in">
              <div className="bg-card border border-border rounded-2xl rounded-tl-none px-4 py-3 flex items-center gap-2">
                <Loader2 className="h-4 w-4 animate-spin text-primary" />
                <span className="text-sm text-muted-foreground font-medium">ttrip is thinking...</span>
              </div>
            </div>
          )}

          <div ref={scrollRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="sticky bottom-0 border-t border-border bg-background/95 backdrop-blur-sm py-4 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <ChatInput onSubmit={handleSendMessage} isLoading={isLoading} />
        </div>
      </div>
    </div>
  );
});

ChatInterface.displayName = 'ChatInterface';
