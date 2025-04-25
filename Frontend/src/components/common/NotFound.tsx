// src/components/common/NotFound.tsx
"use client";

interface NotFoundProps {
    message?: string;
}

export default function NotFound({ message = "Page not found" }: NotFoundProps) {
    return (
        <div className="text-center text-muted-foreground p-8">
            <h2 className="text-xl font-semibold">🚫 404</h2>
            <p>{message}</p>
        </div>
    );
}
