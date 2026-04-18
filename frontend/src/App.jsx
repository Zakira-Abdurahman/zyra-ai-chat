import { useState, useEffect, useRef } from 'react';
import Header from './components/Header';
import ChatContainer from './components/ChatContainer';
import InputArea from './components/InputArea';

function App() {
  const [messages, setMessages] = useState([]); // ← empty array, no initial message
  const [isTyping, setIsTyping] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    const ws = new WebSocket('ws://localhost:8000/ws');
    wsRef.current = ws;

    ws.onopen = () => {
      if (!mountedRef.current) return;
      console.log('✅ Connected to Zyra backend');
      setIsConnected(true);
    };

    ws.onclose = () => {
      if (!mountedRef.current) return;
      console.log('🔌 Disconnected from Zyra backend');
      setIsConnected(false);
    };

    ws.onerror = (err) => console.error('WebSocket error:', err);

    ws.onmessage = (event) => {
      if (!mountedRef.current) return;
      const data = JSON.parse(event.data);
      const { type, role, content, value } = data;

      if (type === 'typing') {
        setIsTyping(value);
      } else if (type === 'message' && role === 'assistant') {
        setMessages(prev => [...prev, { role: 'assistant', content }]);
        setIsTyping(false);
      }
    };

    return () => {
      mountedRef.current = false;
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  const sendMessage = (text) => {
    if (!wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) {
      alert('Not connected to backend. Please refresh the page.');
      return;
    }
    setMessages(prev => [...prev, { role: 'user', content: text }]);
    wsRef.current.send(JSON.stringify({ type: 'message', content: text }));
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