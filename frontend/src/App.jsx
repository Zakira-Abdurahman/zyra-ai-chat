import { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import InputArea from './components/InputArea';

function App() {
  const [messages, setMessages] = useState([
    { role: 'assistant', content: 'Hey Zaku... I’m here 😌 How are you feeling today?' }
  ]);
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const streamingMessageRef = useRef(null);
  const socketRef = useRef(null);
  const reconnectTimerRef = useRef(null);

  useEffect(() => {
    // Prevent multiple connections in StrictMode
    if (socketRef.current?.readyState === WebSocket.OPEN) return;

    const connect = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');
      socketRef.current = ws;

      ws.onopen = () => {
        console.log('✅ Connected to Zyra backend');
        setIsConnected(true);
        if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
      };

      ws.onerror = (err) => {
        console.error('❌ WebSocket error:', err);
        setIsConnected(false);
      };

      ws.onclose = () => {
        console.log('🔌 Disconnected from Zyra backend');
        setIsConnected(false);
        // Auto‑reconnect after 3 seconds
        reconnectTimerRef.current = setTimeout(connect, 3000);
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        const { type, role, content, value } = data;

        if (type === 'typing') {
          setIsTyping(value);
        } else if (type === 'message' && role === 'assistant') {
          setMessages(prev => [...prev, { role: 'assistant', content }]);
          streamingMessageRef.current = null;
          setIsTyping(false);
        } else if (type === 'stream') {
          if (streamingMessageRef.current === null) {
            streamingMessageRef.current = { role: 'assistant', content: '' };
            setMessages(prev => [...prev, streamingMessageRef.current]);
          }
          streamingMessageRef.current.content += content;
          setMessages(prev => [...prev]);
        }
      };
    };

    connect();

    return () => {
      // Cleanup only on unmount, not on every render
      if (socketRef.current) {
        socketRef.current.close();
      }
      if (reconnectTimerRef.current) clearTimeout(reconnectTimerRef.current);
    };
  }, []); // Empty dependency array – run once

  const sendMessage = (text) => {
    if (!socketRef.current || socketRef.current.readyState !== WebSocket.OPEN) {
      console.error('WebSocket not connected');
      alert('Backend not running. Start it with: uvicorn app.main:app --reload --port 8000');
      return;
    }
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    socketRef.current.send(JSON.stringify({ type: 'message', content: text }));
  };

  return (
    <div className="h-screen flex flex-col bg-secondary">
      <Header />
      <ChatContainer messages={messages} isTyping={isTyping} />
      <InputArea onSendMessage={sendMessage} disabled={!isConnected || isTyping} />
    </div>
  );
}

export default App;