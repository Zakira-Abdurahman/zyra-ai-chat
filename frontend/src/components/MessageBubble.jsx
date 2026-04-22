import { memo } from 'react';

const MessageBubble = memo(({ role, content }) => {
  const isUser = role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 animate-fade-in`}>
      <div
        className={`
          max-w-[80%] px-4 py-3 rounded-2xl shadow-sm transition-all duration-200
          ${isUser 
            ? 'bg-gradient-to-br from-primary to-primary-dark text-white rounded-br-md' 
            : 'bg-white/80 backdrop-blur-sm border border-primary/20 text-dark rounded-bl-md'
          }
        `}
      >
        <p className="text-sm leading-relaxed whitespace-pre-wrap break-words">
          {content}
        </p>
      </div>
    </div>
  );
});

MessageBubble.displayName = 'MessageBubble';

export default MessageBubble;