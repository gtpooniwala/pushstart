"use client";

import React from 'react';

interface LinkifiedTextProps {
  text: string;
  truncateLinks?: boolean;
  className?: string;
}

export default function LinkifiedText({ text, truncateLinks = false, className = "" }: LinkifiedTextProps) {
  // Regex to match URLs (http/https)
  const urlRegex = /(https?:\/\/[^\s]+)/g;
  
  const parts = text.split(urlRegex);

  return (
    <span className={className}>
      {parts.map((part, i) => {
        if (part.match(urlRegex)) {
          let displayText = part;
          if (truncateLinks && part.length > 15) {
            displayText = part.substring(0, 15) + "...";
          }
          
          return (
            <a 
              key={i} 
              href={part} 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 hover:underline cursor-pointer relative z-20"
              onClick={(e) => e.stopPropagation()}
            >
              {displayText}
            </a>
          );
        }
        return <span key={i}>{part}</span>;
      })}
    </span>
  );
}
