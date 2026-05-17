'use client';
import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle2, Clock } from 'lucide-react';

import { Message } from '@/lib/types';
import { HotelSelectionModal } from './HotelSelectionModal';
import { LiteAPIPaymentWidget } from './LiteAPIPaymentWidget';
import { TypeWriter } from './TypeWriter';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';

interface ChatMessageProps {
  message: Message;
  onSelectHotel?: (selection: number) => void;
  isLoading?: boolean;
}

export function ChatMessage({ message, onSelectHotel, isLoading }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const metadata = message.metadata;
  const messageTime = new Date(message.timestamp).getTime();
  const shouldAnimateTyping =
    !isUser &&
    Number.isFinite(messageTime) &&
    Date.now() - messageTime < 10000;

  const [mounted, setMounted] = useState(false);
  const [showHotelsModal, setShowHotelsModal] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  // Determine message type for styling
  const getMessageIcon = () => {
    if (isUser) return null;
    
    if (metadata?.type === 'error') {
      return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
    if (metadata?.booking_status === 'confirm') {
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    }
    return null;
  };

  const messageIcon = getMessageIcon();
  const hotels = Array.isArray(metadata?.hotels) ? metadata.hotels : [];
  const hasHotels = hotels.length > 0;

  const handleSelectHotel = (selection: number) => {
    setShowHotelsModal(false);
    onSelectHotel?.(selection);
  };

  const paymentContent =
    metadata?.payment_sdk_secret_key && metadata?.payment_transaction_id && metadata?.payment_prebook_id ? (
      <LiteAPIPaymentWidget
        secretKey={metadata.payment_sdk_secret_key}
        publicKey={metadata.payment_sdk_public_key || 'sandbox'}
        transactionId={metadata.payment_transaction_id}
        prebookId={metadata.payment_prebook_id}
        conversationId={metadata.conversation_id}
      />
    ) : metadata?.payment_url ? (
      <div className="mt-4">
        <button
          type="button"
          onClick={(event) => {
            event.preventDefault();
            event.stopPropagation();
            const paymentUrl = metadata.payment_url;
            if (!paymentUrl) return;
            window.open(paymentUrl, '_blank', 'noopener,noreferrer');
          }}
          className="group relative inline-flex w-full items-center justify-center overflow-hidden rounded-2xl border border-primary/30 bg-gradient-to-r from-primary via-primary/90 to-primary/80 px-6 py-4 font-bold text-primary-foreground shadow-lg shadow-primary/20 transition-all hover:scale-[1.01] hover:shadow-xl hover:shadow-primary/30"
        >
          <span className="absolute inset-0 bg-white/10 opacity-0 transition-opacity group-hover:opacity-100" />
          <span className="relative flex items-center gap-2 text-sm sm:text-base">💳 ابدأ الدفع الآمن الآن</span>
        </button>
        <p className="mt-2 text-center text-xs text-foreground/60">دفع آمن</p>
      </div>
    ) : null;

  return (
    <div
      className={`flex w-full mb-4 animate-fade-in ${isUser ? 'justify-end' : 'justify-start'
        }`}
    >
      <div
        className={`max-w-2xl ${isUser
          ? 'bg-primary text-primary-foreground rounded-2xl rounded-tr-none px-4 py-2.5 shadow-md'
          : 'bg-card text-foreground border border-border rounded-2xl rounded-tl-none px-4 py-3'
          }`}
      >
        {/* Header with icon */}
        {messageIcon && !isUser && (
          <div className="flex items-center gap-2 mb-2">
            {messageIcon}
          </div>
        )}

        <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap break-words">
          {isUser ? (
            message.content
          ) : (
            shouldAnimateTyping ? <TypeWriter text={message.content} speed={20} /> : message.content
          )}
        </p>

        {/* Hotels Available Badge and Button */}
        {hasHotels && !isUser && (
          <div className="mt-4">
            <button
              type="button"
              onClick={() => setShowHotelsModal(true)}
              disabled={isLoading}
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-all font-semibold text-sm disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <span>🏨</span>
            <span>عرض {hotels.length} فندق</span>
          </button>
          <Badge variant="secondary" className="ml-2 text-xs">
              {isLoading ? 'جاري التحميل...' : 'جاهز للاختيار'}
          </Badge>
        </div>
      )}

        {/* Hotels Selection Modal */}
        {hasHotels && (
          <HotelSelectionModal
            open={showHotelsModal}
            hotels={hotels}
            onSelectHotel={handleSelectHotel}
            onOpenChange={setShowHotelsModal}
            isLoading={isLoading}
          />
        )}

        {paymentContent}

        {/* Timestamp */}
        {mounted && (
          <span className="text-xs text-foreground/50 mt-2 flex items-center gap-1">
            <Clock className="h-3 w-3" />
            {format(new Date(message.timestamp), 'HH:mm')}
          </span>
        )}
      </div>
    </div>
  );
}
