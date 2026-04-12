const MessageBubble = ({ role, content }) => {
  const isUser = role === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-3 animate-fade-in`}>
      <div className={`max-w-[75%] px-4 py-2 rounded-2xl shadow-sm ${
        isUser 
          ? 'bg-primary text-white rounded-br-sm' 
          : 'bg-white border border-secondary text-dark rounded-bl-sm'
      }`}>
        <p className="text-sm leading-relaxed">{content}</p>
      </div>
    </div>
  );
};

export default MessageBubble;