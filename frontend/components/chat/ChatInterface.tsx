'use client';

import {
  forwardRef,
  useCallback,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from 'react';
import { useUser, useAuth } from '@clerk/nextjs';
import { useSearchParams } from 'next/navigation';
import { Loader2 } from 'lucide-react';
import { v4 as uuidv4 } from 'uuid';

import { ChatInput } from './ChatInput';
import { ChatMessage } from './ChatMessage';
import { type ChatResponse as APIResponse, type Conversation, type Message } from '@/lib/types';

// ─── Public ref type ────────────────────────────────────────────────────────

export interface ChatInterfaceRef {
  reset: () => void;
  selectConversation: (id: string) => void;
}

// ─── Props ───────────────────────────────────────────────────────────────────

export interface ChatInterfaceProps {
  initialMessage?: string;
  onConversationsChange?: (conversations: Conversation[]) => void;
  // Payment-return props forwarded from the server page component
  paymentSuccess?: boolean;
  sessionId?: string;
  liteapi?: string;
  transactionId?: string;
  prebookId?: string;
  conversationId?: string;
}

// ─── Constants ───────────────────────────────────────────────────────────────

const MAX_CONVERSATIONS = 20;
const INTERNAL_PAYMENT_VERIFIED_MESSAGE = '__internal_payment_verified__';

const LEGACY_WELCOME_SNIPPETS = [
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

interface ConversationSummary {
  id: string;
  title: string;
  updatedAt: string;
}

interface SendMessageOptions {
  silentUserMessage?: boolean;
  paymentCompleted?: boolean;
  paymentTransactionId?: string;
  paymentPrebookId?: string;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────

function getResponseType(data: APIResponse): NonNullable<Message['metadata']>['type'] {
  const hasHotels = Array.isArray(data.hotels) && data.hotels.length > 0;
  const hasFlights = Array.isArray(data.flights) && data.flights.length > 0;
  const hasPayment = Boolean(data.payment_url || data.payment_sdk_secret_key);

  if (hasPayment) return 'payment-link';
  if (hasHotels && hasFlights) return 'combined-results';
  if (hasFlights) return 'flight-results';
  if (hasHotels) return 'hotel-results';
  if (data.booking_status) return 'booking-status';
  return 'text';
}

function isLegacyWelcomeMessage(message: Message): boolean {
  if (message.role !== 'assistant') return false;
  const text = (message.content || '').toLowerCase();
  return LEGACY_WELCOME_SNIPPETS.some((s) => text.includes(s));
}

function detectFallbackLanguage(value: string): 'ar' | 'en' {
  return /[؀-ۿ]/.test(value) ? 'ar' : 'en';
}

function fallbackErrorMessage(value: string): string {
  return detectFallbackLanguage(value) === 'ar'
    ? 'لم يصل رد من ttrip. تحقق من الاتصال وحاول مرة أخرى.'
    : 'ttrip did not return a response. Check the connection and try again.';
}

// ─── Component ───────────────────────────────────────────────────────────────

export const ChatInterface = forwardRef<ChatInterfaceRef, ChatInterfaceProps>(
  (
    {
      onConversationsChange,
      paymentSuccess: paymentSuccessProp = false,
      sessionId: sessionIdProp,
      liteapi: liteapiProp,
      transactionId: transactionIdProp,
      prebookId: prebookIdProp,
      conversationId: conversationIdProp,
    },
    ref,
  ) => {
    const { user, isLoaded } = useUser();
    const { getToken } = useAuth();
    // useSearchParams is kept as fallback for cases where the page doesn't
    // resolve params server-side (e.g., direct navigation without Suspense).
    const searchParams = useSearchParams();

    const [messages, setMessages] = useState<Message[]>([]);
    const [conversationId, setConversationId] = useState<string>('');
    const [isLoading, setIsLoading] = useState(false);
    const [initialized, setInitialized] = useState(false);

    const scrollRef = useRef<HTMLDivElement>(null);
    // Prevents duplicate sends (e.g., React Strict Mode double-invoke or
    // rapid user taps).
    const isSendingRef = useRef(false);
    // Prevents the payment continuation effect from firing more than once per
    // component lifetime even if deps change.
    const paymentContinuationFiredRef = useRef(false);

    // ── Stable storage-key helpers ──────────────────────────────────────────

    const storageKeys = useMemo(() => {
      if (!user) {
        return {
          summariesKey: '',
          activeConversationKey: '',
          messagesKey: (_id: string) => '',
        };
      }
      return {
        summariesKey: `ttrip:conversations:${user.id}`,
        activeConversationKey: `ttrip:active_conversation:${user.id}`,
        messagesKey: (id: string) => `ttrip:messages:${user.id}:${id}`,
      };
    }, [user]);

    const toConversationList = useCallback(
      (items: ConversationSummary[]): Conversation[] =>
        items.map((item) => ({
          id: item.id,
          title: item.title,
          createdAt: new Date(item.updatedAt),
          updatedAt: new Date(item.updatedAt),
          messageCount: 0,
        })),
      [],
    );

    const loadSummaries = useCallback((): ConversationSummary[] => {
      if (!storageKeys.summariesKey) return [];
      try {
        const raw = localStorage.getItem(storageKeys.summariesKey);
        if (!raw) return [];
        const parsed = JSON.parse(raw) as ConversationSummary[];
        return Array.isArray(parsed) ? parsed : [];
      } catch {
        return [];
      }
    }, [storageKeys.summariesKey]);

    const saveSummaries = useCallback(
      (items: ConversationSummary[]) => {
        if (!storageKeys.summariesKey) return;
        const trimmed = items.slice(0, MAX_CONVERSATIONS);
        localStorage.setItem(storageKeys.summariesKey, JSON.stringify(trimmed));
        onConversationsChange?.(toConversationList(trimmed));
      },
      [storageKeys.summariesKey, onConversationsChange, toConversationList],
    );

    const loadMessages = useCallback(
      (id: string): Message[] => {
        const key = storageKeys.messagesKey(id);
        if (!key) return [];
        try {
          const raw = localStorage.getItem(key);
          if (!raw) return [];
          const parsed = JSON.parse(raw) as Array<
            Omit<Message, 'timestamp'> & { timestamp: string }
          >;
          if (!Array.isArray(parsed)) return [];
          const restored = parsed.map((m) => ({ ...m, timestamp: new Date(m.timestamp) }));
          return restored.filter((m) => !isLegacyWelcomeMessage(m));
        } catch {
          return [];
        }
      },
      [storageKeys],
    );

    const saveMessages = useCallback(
      (id: string, value: Message[]) => {
        const key = storageKeys.messagesKey(id);
        if (!key) return;
        localStorage.setItem(
          key,
          JSON.stringify(value.map((m) => ({ ...m, timestamp: m.timestamp.toISOString() }))),
        );
      },
      [storageKeys],
    );

    const buildTitle = useCallback((value: Message[]) => {
      const firstUser = value.find((m) => m.role === 'user')?.content?.trim();
      if (!firstUser) return 'New trip';
      return firstUser.length > 50 ? `${firstUser.slice(0, 50)}...` : firstUser;
    }, []);

    const upsertSummary = useCallback(
      (id: string, value: Message[]) => {
        const summaries = loadSummaries();
        const next = [
          { id, title: buildTitle(value), updatedAt: new Date().toISOString() },
          ...summaries.filter((s) => s.id !== id),
        ];
        saveSummaries(next);
      },
      [loadSummaries, buildTitle, saveSummaries],
    );

    // ── Conversation management ──────────────────────────────────────────────

    const startNewConversation = useCallback(() => {
      const id = uuidv4();
      setConversationId(id);
      setMessages([]);
      if (storageKeys.activeConversationKey) {
        localStorage.setItem(storageKeys.activeConversationKey, id);
      }
    }, [storageKeys.activeConversationKey]);

    const selectConversation = useCallback(
      (id: string) => {
        const stored = loadMessages(id);
        if (stored.length === 0) {
          startNewConversation();
          return;
        }
        setConversationId(id);
        setMessages(stored);
        if (storageKeys.activeConversationKey) {
          localStorage.setItem(storageKeys.activeConversationKey, id);
        }
      },
      [loadMessages, startNewConversation, storageKeys.activeConversationKey],
    );

    useImperativeHandle(
      ref,
      () => ({ reset: startNewConversation, selectConversation }),
      [startNewConversation, selectConversation],
    );

    // ── Initialization ───────────────────────────────────────────────────────

    useEffect(() => {
      if (!isLoaded || !user || initialized) return;

      const summaries = loadSummaries();
      onConversationsChange?.(toConversationList(summaries));

      if (summaries.length === 0) {
        startNewConversation();
        setInitialized(true);
        return;
      }

      // Prefer prop-provided conversationId (payment return) over last active.
      const activeKey = storageKeys.activeConversationKey;
      const storedActive = activeKey ? localStorage.getItem(activeKey) : null;
      const targetId = conversationIdProp || storedActive;
      const selectedId =
        targetId && summaries.some((s) => s.id === targetId) ? targetId : summaries[0].id;
      const storedMessages = loadMessages(selectedId);

      if (storedMessages.length > 0) {
        setConversationId(selectedId);
        setMessages(storedMessages);
        if (activeKey) localStorage.setItem(activeKey, selectedId);
      } else {
        startNewConversation();
      }

      setInitialized(true);
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [isLoaded, user, initialized]);

    // ── Persist messages on change ───────────────────────────────────────────

    useEffect(() => {
      if (!initialized || !user || !conversationId || messages.length === 0) return;
      saveMessages(conversationId, messages);
      upsertSummary(conversationId, messages);
      if (storageKeys.activeConversationKey) {
        localStorage.setItem(storageKeys.activeConversationKey, conversationId);
      }
    }, [messages, conversationId, initialized, user, saveMessages, upsertSummary, storageKeys]);

    // ── Auto-scroll ──────────────────────────────────────────────────────────

    useEffect(() => {
      const container = scrollRef.current?.parentElement;
      if (container) {
        setTimeout(() => {
          container.scrollTop = container.scrollHeight;
        }, 0);
      }
    }, [messages]);

    // ── Core send function ───────────────────────────────────────────────────

    const handleSendMessage = useCallback(
      async (userInput: string, options?: SendMessageOptions) => {
        if (!user || !isLoaded) return;
        if (isSendingRef.current) return;
        isSendingRef.current = true;

        // Use current conversationId or generate one if not yet set.
        const activeConversationId = conversationId || uuidv4();

        if (!options?.silentUserMessage) {
          setMessages((prev) => [
            ...prev,
            {
              id: uuidv4(),
              role: 'user',
              content: userInput,
              timestamp: new Date(),
            },
          ]);
        }
        setIsLoading(true);

        try {
          const token = await getToken();
          if (!token) throw new Error('Failed to get authentication token');

          const response = await fetch('/api/v1/chat', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              message: userInput,
              conversation_id: activeConversationId,
              payment_completed: options?.paymentCompleted ?? false,
              payment_transaction_id: options?.paymentTransactionId,
              payment_prebook_id: options?.paymentPrebookId,
            }),
          });

          const data: APIResponse & { error?: string; message?: string; detail?: unknown } =
            await response.json().catch(() => ({}));

          if (!response.ok) {
            console.error('[ttrip] Backend chat error:', response.status, data);
            throw new Error(
              data.error ||
                data.message ||
                (typeof data.detail === 'string' ? data.detail : `Server error: ${response.status}`),
            );
          }

          // KEY FIX: sync conversationId from backend response so that
          // subsequent messages share the same backend memory thread.
          const nextConversationId = data.conversation_id || activeConversationId;
          if (nextConversationId !== conversationId) {
            setConversationId(nextConversationId);
            if (storageKeys.activeConversationKey) {
              localStorage.setItem(storageKeys.activeConversationKey, nextConversationId);
            }
          }

          setMessages((prev) => [
            ...prev,
            {
              id: uuidv4(),
              role: 'assistant',
              content: String(data.response || ''),
              timestamp: new Date(),
              metadata: {
                type: getResponseType(data),
                hotels: Array.isArray(data.hotels) ? data.hotels : [],
                flights: Array.isArray(data.flights) ? data.flights : [],
                payment_url: data.payment_url,
                payment_sdk_secret_key: data.payment_sdk_secret_key,
                payment_sdk_public_key: data.payment_sdk_public_key,
                payment_transaction_id: data.payment_transaction_id,
                payment_prebook_id: data.payment_prebook_id,
                booking_status: data.booking_status,
                state: data.state,
                conversation_id: nextConversationId,
              },
            },
          ]);
        } catch (error) {
          console.error('[ttrip] Chat error:', error);
          setMessages((prev) => [
            ...prev,
            {
              id: uuidv4(),
              role: 'assistant',
              content: fallbackErrorMessage(userInput),
              timestamp: new Date(),
              metadata: { type: 'error' },
            },
          ]);
        } finally {
          setIsLoading(false);
          isSendingRef.current = false;
        }
      },
      // conversationId is intentionally included so we send the latest value.
      // eslint-disable-next-line react-hooks/exhaustive-deps
      [user, isLoaded, conversationId, getToken, storageKeys.activeConversationKey],
    );

    // Keep a ref so the payment effect can call the latest version without
    // being re-triggered every time handleSendMessage identity changes.
    const sendRef = useRef(handleSendMessage);
    useEffect(() => {
      sendRef.current = handleSendMessage;
    }, [handleSendMessage]);

    // ── Payment-return continuation ──────────────────────────────────────────

    useEffect(() => {
      if (!initialized || !isLoaded || !user || !conversationId || isLoading) return;
      if (paymentContinuationFiredRef.current) return;

      // Props (resolved server-side) take priority over searchParams.
      const isPaymentSuccess =
        paymentSuccessProp || searchParams.get('payment_success') === '1';
      if (!isPaymentSuccess) return;

      const isLiteapi = liteapiProp === '1' || searchParams.get('liteapi') === '1';
      const txId = transactionIdProp || searchParams.get('transaction_id');
      const pbId = prebookIdProp || searchParams.get('prebook_id');
      const sId = sessionIdProp || searchParams.get('session_id');

      // Deduplicate across re-renders using sessionStorage.
      const dedupeId = sId || txId || 'unknown';
      const dedupeKey = `ttrip:payment_processed:${dedupeId}`;
      if (sessionStorage.getItem(dedupeKey)) return;
      sessionStorage.setItem(dedupeKey, '1');

      paymentContinuationFiredRef.current = true;

      const clearPaymentParams = () => {
        const url = new URL(window.location.href);
        ['payment_success', 'session_id', 'liteapi', 'transaction_id', 'prebook_id', 'conversation_id'].forEach(
          (k) => url.searchParams.delete(k),
        );
        window.history.replaceState({}, '', `${url.pathname}${url.search}${url.hash}`);
      };

      const appendError = (content: string) => {
        setMessages((prev) => [
          ...prev,
          {
            id: uuidv4(),
            role: 'assistant',
            content,
            timestamp: new Date(),
            metadata: { type: 'error' },
          },
        ]);
      };

      void (async () => {
        try {
          if (isLiteapi && txId) {
            await sendRef.current(INTERNAL_PAYMENT_VERIFIED_MESSAGE, {
              silentUserMessage: true,
              paymentCompleted: true,
              paymentTransactionId: txId,
              paymentPrebookId: pbId || undefined,
            });
          } else if (sId) {
            await sendRef.current(
              `Payment completed for session ${sId}. Continue the booking.`,
              { silentUserMessage: true },
            );
          } else {
            throw new Error('Missing payment callback identifiers');
          }
          clearPaymentParams();
        } catch (error) {
          console.error('[ttrip] Payment continuation error:', error);
          sessionStorage.removeItem(dedupeKey);
          paymentContinuationFiredRef.current = false;
          appendError(
            'Could not verify payment. Please try again or type "I have paid" to continue.',
          );
        }
      })();
      // Fire once when the component is ready and conversationId is known.
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [initialized, isLoaded, user, conversationId, isLoading, paymentSuccessProp]);

    // ── Hotel selection ──────────────────────────────────────────────────────

    const handleSelectHotel = useCallback(
      async (selection: number) => {
        if (isLoading) return;
        await handleSendMessage(String(selection));
      },
      [isLoading, handleSendMessage],
    );

    // ── Render ───────────────────────────────────────────────────────────────

    return (
      <div className="flex flex-col h-screen bg-background">
        {/* Messages */}
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
                  <span className="text-sm text-muted-foreground font-medium">
                    ttrip is thinking...
                  </span>
                </div>
              </div>
            )}

            <div ref={scrollRef} />
          </div>
        </div>

        {/* Input */}
        <div className="sticky bottom-0 border-t border-border bg-background/95 backdrop-blur-sm py-4 px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto">
            <ChatInput onSubmit={handleSendMessage} isLoading={isLoading} />
          </div>
        </div>
      </div>
    );
  },
);

ChatInterface.displayName = 'ChatInterface';
