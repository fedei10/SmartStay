import { SignIn } from '@clerk/nextjs'

export default function UnauthorizedPage() {
    return (
        <div className="min-h-screen flex items-center justify-center bg-background px-4">
            <div className="w-full max-w-md">
                <div className="mb-8 text-center">
                    <h1 className="text-3xl font-bold text-foreground mb-2">
                        مرحبًا بك في <span className="text-primary">ttrip</span>
                    </h1>
                    <p className="text-muted-foreground mx-2">يرجى تسجيل الدخول للوصول إلى مساعد حجز الفنادق الذكي</p>
                </div>
                <SignIn />
            </div>
        </div>
    )
}
