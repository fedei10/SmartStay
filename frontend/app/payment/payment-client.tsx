'use client';

import { useState } from 'react';
import { Header } from '@/components/layout/Header';
import { Sidebar } from '@/components/layout/Sidebar';
import Checkout from '@/components/checkout/Checkout';
import { PRODUCTS } from '@/lib/products';
import { Check } from 'lucide-react';

export default function PaymentClient() {
    const [selectedProductId, setSelectedProductId] = useState<string | null>(null);

    return (
        <div className="flex w-full min-h-screen bg-background">
            <Sidebar />
            <div className="flex-1 flex flex-col w-full">
                <Header />
                <main className="flex-1 overflow-y-auto">
                    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
                        <div className="mb-12">
                            <h1 className="text-4xl sm:text-5xl font-bold text-foreground mb-3">
                                اختر <span className="text-primary">الباقة</span>
                            </h1>
                            <p className="text-lg text-muted-foreground">
                                اختر الباقة المناسبة لاحتياجات حجز الفنادق
                            </p>
                        </div>

                        <div className="grid md:grid-cols-3 gap-8 mb-12">
                            {PRODUCTS.map((product) => (
                                <div
                                    key={product.id}
                                    className={`rounded-xl border transition-all duration-300 p-8 flex flex-col ${selectedProductId === product.id
                                        ? 'bg-card border-primary shadow-lg shadow-primary/20'
                                        : 'bg-card border-border hover:border-primary/50'
                                        }`}
                                >
                                    {product.id === 'premium-package' && (
                                        <div className="mb-4 inline-block">
                                            <span className="bg-primary text-primary-foreground text-xs font-bold px-3 py-1 rounded-full">
                                                الأكثر شيوعًا
                                            </span>
                                        </div>
                                    )}

                                    <h2 className="text-2xl font-bold text-foreground mb-2">{product.name}</h2>
                                    <p className="text-muted-foreground text-sm mb-6">{product.description}</p>

                                    <div className="mb-6">
                                        <span className="text-5xl font-bold text-foreground">
                                            ${(product.priceInCents / 100).toFixed(2)}
                                        </span>
                                        <span className="text-muted-foreground ml-2 text-sm">مرة واحدة</span>
                                    </div>

                                    <div className="border-t border-border mb-6" />

                                    <ul className="space-y-3 mb-8 flex-1">
                                        {product.features.map((feature, idx) => (
                                            <li key={idx} className="flex items-start gap-3">
                                                <Check className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
                                                <span className="text-foreground/90 text-sm">{feature}</span>
                                            </li>
                                        ))}
                                    </ul>

                                    <button
                                        onClick={() => setSelectedProductId(product.id)}
                                        className={`w-full py-3 px-4 rounded-lg font-bold transition-all duration-300 ${selectedProductId === product.id
                                            ? 'bg-primary text-primary-foreground'
                                            : 'bg-secondary text-foreground hover:bg-primary hover:text-primary-foreground'
                                            }`}
                                    >
                                        {selectedProductId === product.id ? 'تم الاختيار' : 'اختيار الباقة'}
                                    </button>
                                </div>
                            ))}
                        </div>

                        {selectedProductId && (
                            <div className="max-w-2xl mx-auto">
                                <div className="bg-card border border-border rounded-xl p-8">
                                    <h3 className="text-2xl font-bold text-foreground mb-2">
                                        أكمل عملية الشراء
                                    </h3>
                                    <p className="text-muted-foreground mb-8">
                                        {PRODUCTS.find((p) => p.id === selectedProductId)?.name}
                                    </p>
                                    <Checkout productId={selectedProductId} />
                                </div>
                            </div>
                        )}

                        {!selectedProductId && (
                            <div className="max-w-2xl mx-auto">
                                <div className="bg-card border border-border rounded-xl p-8 text-center">
                                    <p className="text-muted-foreground">
                                        اختر باقة من الأعلى للمتابعة إلى الدفع
                                    </p>
                                </div>
                            </div>
                        )}
                    </div>
                </main>
            </div>
        </div>
    );
}
