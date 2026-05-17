import { clerkMiddleware, createRouteMatcher } from "@clerk/nextjs/server";
import { NextResponse } from "next/server";

const isProtectedRoute = createRouteMatcher([
    "/chat(.*)",
    "/payment(.*)",
    "/bookings(.*)",
    "/complete-profile(.*)",
]);

export default clerkMiddleware(async (auth, req) => {
    const paymentSuccess = req.nextUrl.searchParams.get("payment_success");
    const sessionId = req.nextUrl.searchParams.get("session_id");
    const liteapi = req.nextUrl.searchParams.get("liteapi");
    const transactionId = req.nextUrl.searchParams.get("transaction_id");
    const prebookId = req.nextUrl.searchParams.get("prebook_id");
    const conversationId = req.nextUrl.searchParams.get("conversation_id");

    if (
        req.nextUrl.pathname === "/" &&
        paymentSuccess === "1" &&
        (sessionId || (liteapi === "1" && transactionId))
    ) {
        const redirectUrl = new URL("/chat", req.url);
        redirectUrl.searchParams.set("payment_success", "1");
        if (sessionId) redirectUrl.searchParams.set("session_id", sessionId);
        if (liteapi) redirectUrl.searchParams.set("liteapi", liteapi);
        if (transactionId) redirectUrl.searchParams.set("transaction_id", transactionId);
        if (prebookId) redirectUrl.searchParams.set("prebook_id", prebookId);
        if (conversationId) redirectUrl.searchParams.set("conversation_id", conversationId);
        return NextResponse.redirect(redirectUrl);
    }

    if (isProtectedRoute(req)) {
        await auth.protect();
    }
});

export const config = {
    matcher: [
        // Skip Next.js internals and all static files, unless found in search params
        "/((?!_next|[^?]*\\.(?:html?|css|js(?!on)|jpe?g|webp|png|gif|svg|ttf|woff2?|ico|csv|docx?|xlsx?|zip|webmanifest)).*)",
        // Always run for API routes
        "/(api|trpc)(.*)",
    ],
};
