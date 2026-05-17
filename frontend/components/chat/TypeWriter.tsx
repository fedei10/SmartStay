'use client';

import { useEffect, useState } from 'react';

interface TypeWriterProps {
  text: string;
  speed?: number;
  delay?: number;
}

export function TypeWriter({ text, speed = 30, delay = 0 }: TypeWriterProps) {
  const [displayedText, setDisplayedText] = useState('');
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    if (!text || text.length === 0) {
      setDisplayedText('');
      setIsComplete(true);
      return;
    }

    let timeout: NodeJS.Timeout;
    let charIndex = 0;

    const startTimer = setTimeout(() => {
      const interval = setInterval(() => {
        if (text && charIndex < text.length) {
          setDisplayedText(text.slice(0, charIndex + 1));
          charIndex++;
        } else {
          clearInterval(interval);
          setIsComplete(true);
        }
      }, speed);

      return () => clearInterval(interval);
    }, delay);

    return () => clearTimeout(startTimer);
  }, [text, speed, delay]);

  return (
    <>
      {displayedText}
      {!isComplete && <span className="animate-pulse">▊</span>}
    </>
  );
}
