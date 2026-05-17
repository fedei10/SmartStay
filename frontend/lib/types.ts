export interface HotelRate {
  price?: number;
  currency?: string;
  room_type?: string;
  board_type?: string;
  offer_id?: string;
  offerId?: string;
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

export interface FlightSegment {
  from?: string;
  to?: string;
  departure_time?: string;
  arrival_time?: string;
  carrier?: string;
  flight_number?: string;
  duration?: string;
}

export interface FlightOffer {
  id?: string;
  offer_id?: string;
  offerId?: string;
  airline?: string;
  price?: number;
  currency?: string;
  departure_time?: string;
  arrival_time?: string;
  duration?: string;
  stops?: number;
  segments?: FlightSegment[];
}

export interface TravelState {
  origin?: string;
  destination?: string;
  departure_date?: string;
  return_date?: string;
  trip_type?: 'one_way' | 'round_trip' | string;
  travelers?: number;

  hotel_needed?: boolean;
  checkin_date?: string;
  checkout_date?: string;
  guests?: number;
  rooms?: number;

  budget_level?: 'budget' | 'mid_range' | 'luxury' | string;
  budget_amount?: number;
  currency?: string;

  selected_hotel_id?: string;
  selected_hotel_offer_id?: string;
  selected_flight_offer_id?: string;

  prebook_id?: string;
  transaction_id?: string;
  payment_status?: string;
  booking_status?: string;

  next_action?: string;
  missing_fields?: string[];

  [key: string]: unknown;
}

export interface ChatMetadata {
  type?:
    | 'text'
    | 'hotel-results'
    | 'flight-results'
    | 'combined-results'
    | 'payment-link'
    | 'booking-status'
    | 'error';

  hotels?: Hotel[];
  flights?: FlightOffer[];

  payment_url?: string;
  payment_sdk_secret_key?: string;
  payment_sdk_public_key?: string;
  payment_transaction_id?: string;
  payment_prebook_id?: string;

  booking_status?: string;
  state?: TravelState | unknown;
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
  flights?: FlightOffer[];

  payment_url?: string;
  payment_sdk_secret_key?: string;
  payment_sdk_public_key?: string;
  payment_transaction_id?: string;
  payment_prebook_id?: string;

  booking_status?: string;
  state?: TravelState | unknown;

  intent?: string;
  agent?: string;
  next_action?: string;
  metadata?: Record<string, unknown>;
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
  // Optional fields for combined/flight bookings
  flight_reference?: string;
}
