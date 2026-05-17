'use client';
import { useState, useEffect } from 'react';
import { AlertCircle, CheckCircle2, Clock, Sparkles } from 'lucide-react';

import { Message } from '@/lib/types';
import { HotelSelectionModal } from './HotelSelectionModal';
import { FlightSelectionList } from './FlightSelectionList';
import { LiteAPIPaymentWidget } from './LiteAPIPaymentWidget';
import { TypeWriter } from './TypeWriter';
import { format } from 'date-fns';
import { Badge } from '@/components/ui/badge';

interface ChatMessageProps {
  message: Message;
  onSelectHotel?: (selection: number) => void;
  onSelectFlight?: (selection: number) => void;
  isLoading?: boolean;
}

export function ChatMessage({ message, onSelectHotel, onSelectFlight, isLoading }: ChatMessageProps) {
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

  const hotels = Array.isArray(metadata?.hotels) ? metadata.hotels : [];
  const hasHotels = hotels.length > 0;
  const flights = Array.isArray(metadata?.flights) ? metadata.flights : [];
  const hasFlights = flights.length > 0;

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
          onClick={(e) => {
            e.preventDefault();
            e.stopPropagation();
            const url = metadata.payment_url;
            if (url) window.open(url as string, '_blank', 'noopener,noreferrer');
          }}
          className="group relative inline-flex w-full items-center justify-center overflow-hidden rounded-xl border border-primary/30 bg-gradient-to-r from-primary via-primary/90 to-primary/80 px-6 py-4 font-bold text-primary-foreground shadow-lg shadow-primary/20 transition-all hover:scale-[1.01] hover:shadow-xl hover:shadow-primary/30"
        >
          <span className="absolute inset-0 bg-white/10 opacity-0 transition-opacity group-hover:opacity-100" />
          <span className="relative flex items-center gap-2 text-sm sm:text-base">💳 Proceed to payment</span>
        </button>
      </div>
    ) : null;

  if (isUser) {
    return (
      <div className="flex w-full mb-3 justify-end animate-fade-in">
        <div className="max-w-[78%] sm:max-w-[65%]">
          <div className="bg-primary text-primary-foreground rounded-2xl rounded-tr-sm px-4 py-2.5 shadow-sm">
            <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">{message.content}</p>
          </div>
          {mounted && (
            <p className="text-[10px] text-muted-foreground/60 mt-1 text-right flex items-center justify-end gap-1">
              <Clock className="h-2.5 w-2.5" />
              {format(new Date(message.timestamp), 'HH:mm')}
            </p>
          )}
        </div>
      </div>
    );
  }

  const isError = metadata?.type === 'error';
  const isConfirmed = metadata?.booking_status === 'confirmed';

  return (
    <div className="flex w-full mb-3 justify-start animate-fade-in">
      {/* AI Avatar */}
      <div className="mr-2.5 mt-0.5 flex-shrink-0">
        <div className="h-7 w-7 rounded-full bg-gradient-to-br from-primary to-teal-600 flex items-center justify-center shadow-sm">
          <Sparkles className="h-3.5 w-3.5 text-white" />
        </div>
      </div>

      <div className="max-w-[78%] sm:max-w-[70%] space-y-0.5">
        <div className={`rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm ${
          isError
            ? 'bg-destructive/10 border border-destructive/20'
            : isConfirmed
            ? 'bg-green-500/10 border border-green-500/20'
            : 'bg-card border border-border/60'
        }`}>
          {/* Status icon */}
          {(isError || isConfirmed) && (
            <div className="flex items-center gap-1.5 mb-2">
              {isError && <AlertCircle className="h-3.5 w-3.5 text-destructive" />}
              {isConfirmed && <CheckCircle2 className="h-3.5 w-3.5 text-green-500" />}
              <span className={`text-xs font-medium ${isError ? 'text-destructive' : 'text-green-600'}`}>
                {isError ? 'Error' : 'Booking confirmed'}
              </span>
            </div>
          )}

          <p className="text-sm leading-relaxed whitespace-pre-wrap break-words text-foreground">
            {shouldAnimateTyping
              ? <TypeWriter text={message.content} speed={20} />
              : message.content}
          </p>

          {/* Hotels button */}
          {hasHotels && (
            <div className="mt-3 pt-3 border-t border-border/50">
              <button
                type="button"
                onClick={() => setShowHotelsModal(true)}
                disabled={isLoading}
                className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl bg-primary text-primary-foreground hover:bg-primary/90 transition-all font-semibold text-xs disabled:opacity-50 disabled:cursor-not-allowed shadow-sm hover:shadow-md"
              >
                <span>🏨</span>
                <span>View {hotels.length} hotel{hotels.length > 1 ? 's' : ''}</span>
              </button>
              <Badge variant="secondary" className="ml-2 text-[10px]">
                {isLoading ? 'Loading...' : 'Ready to select'}
              </Badge>
            </div>
          )}

          {/* Hotel modal */}
          {hasHotels && (
            <HotelSelectionModal
              open={showHotelsModal}
              hotels={hotels}
              onSelectHotel={handleSelectHotel}
              onOpenChange={setShowHotelsModal}
              isLoading={isLoading}
            />
          )}

          {/* Flight results */}
          {hasFlights && (
            <div className="mt-3 pt-3 border-t border-border/50">
              <FlightSelectionList
                flights={flights}
                onSelectFlight={onSelectFlight}
                isLoading={isLoading}
              />
            </div>
          )}

          {paymentContent}
        </div>

        {mounted && (
          <p className="text-[10px] text-muted-foreground/55 flex items-center gap-1 px-1">
            <Clock className="h-2.5 w-2.5" />
            {format(new Date(message.timestamp), 'HH:mm')}
          </p>
        )}
      </div>
    </div>
  );
}
