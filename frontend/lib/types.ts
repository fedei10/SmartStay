export interface HotelRate {
  price?: number;
  currency?: string;
  room_type?: string;
  board_type?: string;
}

export interface Hotel {
  hotel_id: string;
  name: string;
  address?: string;
  city?: string;
  country?: string;
  stars?: number;
  rating?: number;
  description?: string;
  image_url?: string;
  image_urls?: string[];
  rates?: HotelRate[];
}

export interface ChatMetadata {
  type?: 'text' | 'hotel-results' | 'payment-link' | 'error';
  hotels?: Hotel[];
  payment_url?: string;
  payment_sdk_secret_key?: string;
  payment_sdk_public_key?: string;
  payment_transaction_id?: string;
  payment_prebook_id?: string;
  booking_status?: string;
  state?: unknown;
  conversation_id?: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  metadata?: ChatMetadata;
}

export interface Conversation {
  id: string;
  title: string;
  createdAt: Date;
  updatedAt: Date;
  messageCount: number;
}

export interface ChatResponse {
  conversation_id?: string;
  response?: string;
  hotels?: Hotel[];
  payment_url?: string;
  payment_sdk_secret_key?: string;
  payment_sdk_public_key?: string;
  payment_transaction_id?: string;
  payment_prebook_id?: string;
  booking_status?: string;
  state?: unknown;
}

export interface Booking {
  id: string | number;
  booking_reference: string;
  hotel_name: string;
  checkin_date: string;
  checkout_date: string;
  status: 'confirmed' | 'pending' | 'cancelled' | string;
  currency: string;
  total_amount: number | string;
  payment_status: 'succeeded' | 'pending' | string;
  updated_at: string;
}
