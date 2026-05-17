'use client';

import { useState, useEffect } from 'react';
import { useUser, useAuth } from '@clerk/nextjs';
import { format } from 'date-fns';
import { ar } from 'date-fns/locale';
import { Bookmark, Calendar, Loader2 } from 'lucide-react';

import { Booking } from '@/lib/types';
import { useToast } from '@/hooks/use-toast';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';

export default function BookingsClient() {
  const { user, isLoaded } = useUser();
  const { getToken } = useAuth();
  const { toast } = useToast();

  const [bookings, setBookings] = useState<Booking[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCancellingReference, setIsCancellingReference] = useState<string | null>(null);
  const [cancelTarget, setCancelTarget] = useState<Booking | null>(null);

  const canCancelBooking = (booking: Booking) =>
    booking.status === 'confirmed' || booking.status === 'pending';

  const fetchBookings = async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Missing authentication token');
      }

      const response = await fetch(`/api/v1/bookings/${user.id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setBookings(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('[ttrip] Error fetching bookings:', error);
      toast({
        title: 'تعذر تحميل الحجوزات',
        description: 'يرجى تحديث الصفحة والمحاولة مرة أخرى.',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const confirmCancel = async () => {
    if (!cancelTarget || !user || isCancellingReference) return;

    const bookingReference = cancelTarget.booking_reference;
    const previousBookings = bookings;
    setCancelTarget(null);
    setIsCancellingReference(bookingReference);

    setBookings((prev) =>
      prev.map((booking) =>
        booking.booking_reference === bookingReference
          ? { ...booking, status: 'cancelled', updated_at: new Date().toISOString() }
          : booking
      )
    );

    try {
      const token = await getToken();
      if (!token) {
        throw new Error('Missing authentication token');
      }

      const response = await fetch(
        `/api/v1/bookings/reference/${encodeURIComponent(bookingReference)}/cancel`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({ reason: 'Cancelled by user from bookings page' }),
        }
      );

      const payload = await response.json().catch(() => ({}));
      if (!response.ok) {
        throw new Error(payload?.detail || `HTTP ${response.status}`);
      }

      setBookings((prev) =>
        prev.map((booking) =>
          booking.booking_reference === bookingReference ? payload : booking
        )
      );

      toast({
        title: 'تم إلغاء الحجز',
        description: 'تم إلغاء الحجز بنجاح.',
      });
    } catch (error) {
      console.error('[ttrip] Error cancelling booking:', error);
      setBookings(previousBookings);
      toast({
        title: 'فشل إلغاء الحجز',
        description:
          error instanceof Error
            ? error.message
            : 'تعذر إتمام عملية الإلغاء.',
        variant: 'destructive',
      });
    } finally {
      setIsCancellingReference(null);
    }
  };

  useEffect(() => {
    if (isLoaded && user) {
      void fetchBookings();
    }
  }, [isLoaded, user, getToken]);

  if (!isLoaded || isLoading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] gap-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
        <p className="text-muted-foreground font-medium">جاري تحميل حجوزاتك...</p>
      </div>
    );
  }

  if (bookings.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] text-center px-4">
        <div className="bg-secondary/50 p-6 rounded-full mb-6">
          <Bookmark className="h-12 w-12 text-muted-foreground" />
        </div>
        <h1 className="text-2xl font-bold text-foreground mb-2">لا توجد حجوزات</h1>
        <p className="text-muted-foreground max-w-md">
          لم تقم بأي حجز بعد. ابدأ المحادثة للبحث عن فندق وإتمام الحجز.
        </p>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="flex items-center justify-between mb-10">
        <h1 className="text-3xl font-bold text-foreground tracking-tight">حجوزاتي</h1>
        <div className="bg-primary/10 text-primary px-4 py-1.5 rounded-full text-sm font-semibold">
          {bookings.length} {bookings.length === 1 ? 'حجز' : 'حجوزات'}
        </div>
      </div>

      <div className="grid gap-6">
        {bookings.map((booking) => {
          const isCancelling = isCancellingReference === booking.booking_reference;
          const canCancel = canCancelBooking(booking) && !isCancelling;

          return (
            <div
              key={booking.id}
              className="bg-card border border-border rounded-2xl overflow-hidden hover:shadow-xl transition-all duration-300 group"
            >
              <div className="p-6 md:p-8">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div className="space-y-4">
                      <div>
                      <div className="text-xs font-bold uppercase tracking-widest text-primary mb-1">فندق</div>
                      <h3 className="text-xl font-bold text-foreground group-hover:text-primary transition-colors">
                        {booking.hotel_name}
                      </h3>
                      <p className="text-xs text-muted-foreground mt-1">
                        رقم الحجز: {booking.booking_reference}
                      </p>
                    </div>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <div className="flex items-center gap-3 text-sm text-foreground/70">
                        <div className="p-2 bg-secondary rounded-lg">
                          <Calendar className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="text-[10px] font-bold uppercase text-muted-foreground tracking-tighter">
                            تسجيل الدخول
                          </div>
                          <div className="font-medium">
                            {format(new Date(booking.checkin_date), 'dd MMM yyyy', { locale: ar })}
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 text-sm text-foreground/70">
                        <div className="p-2 bg-secondary rounded-lg">
                          <Calendar className="h-4 w-4" />
                        </div>
                        <div>
                          <div className="text-[10px] font-bold uppercase text-muted-foreground tracking-tighter">
                            تسجيل الخروج
                          </div>
                          <div className="font-medium">
                            {format(new Date(booking.checkout_date), 'dd MMM yyyy', { locale: ar })}
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-wrap md:flex-col items-center md:items-end gap-4 md:gap-3">
                    <div
                      className={`px-4 py-1.5 rounded-full text-xs font-bold uppercase tracking-widest ${
                        booking.status === 'confirmed'
                          ? 'bg-emerald-500/10 text-emerald-500 border border-emerald-500/20'
                          : booking.status === 'cancelled'
                            ? 'bg-destructive/10 text-destructive border border-destructive/20'
                            : 'bg-amber-500/10 text-amber-500 border border-amber-500/20'
                      }`}
                    >
                      {booking.status}
                    </div>

                    <div className="flex items-center gap-1.5 font-bold text-2xl text-foreground">
                      <span className="text-sm font-medium text-muted-foreground">
                        {booking.currency}
                      </span>
                      {booking.total_amount}
                    </div>

                    <div
                      className={`text-xs font-medium ${
                        booking.payment_status === 'succeeded'
                          ? 'text-emerald-500'
                          : 'text-amber-500'
                      }`}
                    >
                      ● {booking.payment_status === 'succeeded' ? 'مدفوع' : booking.payment_status}
                    </div>

                    {canCancel && (
                      <button
                        type="button"
                        onClick={() => setCancelTarget(booking)}
                        className="h-9 px-4 rounded-md bg-destructive text-destructive-foreground text-sm font-semibold hover:opacity-90 transition-opacity"
                      >
                        إلغاء الحجز
                      </button>
                    )}

                    {isCancelling && (
                      <div className="h-9 px-4 rounded-md border border-border text-sm flex items-center gap-2 text-muted-foreground">
                        <Loader2 className="h-3.5 w-3.5 animate-spin" />
                        جاري الإلغاء...
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <AlertDialog
        open={Boolean(cancelTarget)}
        onOpenChange={(open) => {
          if (!open) setCancelTarget(null);
        }}
      >
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>هل تريد إلغاء الحجز؟</AlertDialogTitle>
            <AlertDialogDescription>
              سيتم إلغاء الحجز نهائيًا، ولا يمكن التراجع عن هذه العملية.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel disabled={Boolean(isCancellingReference)}>الاحتفاظ بالحجز</AlertDialogCancel>
            <AlertDialogAction
              onClick={(event) => {
                event.preventDefault();
                void confirmCancel();
              }}
              className="bg-destructive text-destructive-foreground hover:bg-destructive/90"
              disabled={Boolean(isCancellingReference)}
            >
              تأكيد الإلغاء
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}
