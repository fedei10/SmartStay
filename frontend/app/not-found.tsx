export default function NotFound() {
    return (
        <div className="min-h-screen bg-background flex items-center justify-center p-4">
            <div className="text-center">
                <h1 className="text-6xl font-bold text-primary mb-4">404</h1>
                <h2 className="text-2xl font-semibold text-foreground mb-4">Page Not Found</h2>
                <p className="text-muted-foreground mb-8 max-w-md mx-auto">
                    Sorry, we couldn't find the page you're looking for.
                </p>
                <a href="/" className="px-6 py-3 bg-primary text-primary-foreground rounded-xl font-bold">
                    Back to Home
                </a>
            </div>
        </div>
    )
}
