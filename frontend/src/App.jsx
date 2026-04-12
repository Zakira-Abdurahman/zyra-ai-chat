// frontend/src/App.jsx
import { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import InputArea from './components/InputArea';
import useWebSocket from 'react-use-websocket';

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hey Zaku... I’m here 😌 How are you feeling today?' }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const streamingMessageRef = useRef(null);
  
  const { sendJsonMessage, lastJsonMessage, readyState } = useWebSocket('ws://localhost:8000/ws', {
    onOpen: () => console.log('Connected to Zyra backend 💜'),
    onError: (err) => console.error('WebSocket error:', err),
    shouldReconnect: () => true,
  });

  // This effect listens for all messages from the backend
  useEffect(() => {
    if (lastJsonMessage) {
      const { type, role, content, value } = lastJsonMessage;
      
      if (type === 'typing') {
        setIsTyping(value);
      } 
      // This handles the final, complete message
      else if (type === 'message' && role === 'assistant') {
        setMessages(prev => [...prev, { role: 'assistant', content }]);
        streamingMessageRef.current = null; // Reset streaming message ref
        setIsTyping(false);
      }
      // This is the new 'stream' message for word-by-word updates
      else if (type === 'stream') {
        if (streamingMessageRef.current === null) {
          // If this is the first piece of the stream, create a new message object
          streamingMessageRef.current = { role: 'assistant', content: '' };
          setMessages(prev => [...prev, streamingMessageRef.current]);
        }
        // Append the new content piece to the streaming message
        streamingMessageRef.current.content += content;
        // Force a re-render by creating a new array
        setMessages(prev => [...prev]);
      }
    }
  }, [lastJsonMessage]);

  const handleSendMessage = (text) => {
    // Add user message to UI immediately
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    // Send to backend
    sendJsonMessage({ type: 'message', content: text });
  };

  const isConnected = readyState === 1;

  return (
    <div className="h-screen flex flex-col bg-secondary">
      <Header />
      <ChatContainer messages={messages} isTyping={isTyping} />
      <InputArea onSendMessage={handleSendMessage} disabled={!isConnected || isTyping} />
    </div>
  );
}

export default App;