import { useState, useEffect, useRef } from 'react';
import { chatAPI } from '../api/chat';

function Chat() {
  const [conversations, setConversations] = useState([]);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [error, setError] = useState('');
  const [showSidebar, setShowSidebar] = useState(true);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadConversations();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async () => {
    try {
      const response = await chatAPI.getConversations();
      setConversations(response.data.conversations || []);
    } catch (err) {
      setError('대화 목록을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const createConversation = async () => {
    try {
      setError('');
      const response = await chatAPI.createConversation();
      const newConv = response.data;
      setConversations([newConv, ...conversations]);
      selectConversation(newConv);
      setShowSidebar(false);
    } catch (err) {
      setError('새 대화 생성에 실패했습니다.');
    }
  };

  const selectConversation = async (conv) => {
    try {
      setError('');
      setCurrentConversation(conv);
      const response = await chatAPI.getConversation(conv.id);
      setMessages(response.data.messages || []);
      setShowSidebar(false);
    } catch (err) {
      setError('대화 내용을 불러오는데 실패했습니다.');
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || sending) return;

    setSending(true);
    setError('');
    const userMessage = newMessage;
    const optimisticMessage = {
      id: `pending-${Date.now()}`,
      type: 'human',
      content: userMessage,
      created_at: new Date().toISOString(),
      pending: true,
    };

    setMessages((prev) => [...prev, optimisticMessage]);
    setNewMessage('');

    try {
      const response = await chatAPI.sendMessage(currentConversation.id, userMessage);
      setMessages(response.data.messages || []);
    } catch (err) {
      setMessages((prev) => prev.filter((msg) => msg.id !== optimisticMessage.id));
      setError('메시지 전송에 실패했습니다.');
      setNewMessage(userMessage);
    } finally {
      setSending(false);
    }
  };

  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDate = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleDateString('ko-KR', { month: 'short', day: 'numeric' });
  };

  if (loading) {
    return <div className="container">로딩 중...</div>;
  }

  return (
    <div style={styles.container}>
      {/* Mobile header */}
      <div style={styles.mobileHeader}>
        <button 
          onClick={() => setShowSidebar(!showSidebar)} 
          style={styles.menuButton}
        >
          {showSidebar ? '✕' : '☰'}
        </button>
        <span style={styles.headerTitle}>
          {currentConversation ? '대화' : '채팅'}
        </span>
        <div style={{ width: '40px' }} />
      </div>

      <div style={styles.layout}>
        {/* Sidebar - Conversation List */}
        <div style={{
          ...styles.sidebar,
          ...(showSidebar ? {} : styles.sidebarHidden)
        }}>
          <div style={styles.sidebarHeader}>
            <h2 style={styles.sidebarTitle}>대화 목록</h2>
            <button onClick={createConversation} style={styles.newChatButton}>
              + 새 대화
            </button>
          </div>

          <div style={styles.conversationList}>
            {conversations.length === 0 ? (
              <div style={styles.emptyState}>
                <p>대화가 없습니다.</p>
                <p style={{ color: '#6b7280', fontSize: '13px', marginTop: '8px' }}>
                  새 대화를 시작해보세요.
                </p>
              </div>
            ) : (
              conversations.map((conv) => (
                <div
                  key={conv.id}
                  onClick={() => selectConversation(conv)}
                  style={{
                    ...styles.conversationItem,
                    ...(currentConversation?.id === conv.id ? styles.conversationItemActive : {})
                  }}
                >
                  <div style={styles.conversationTitle}>
                    {conv.title || '새 대화'}
                  </div>
                  <div style={styles.conversationMeta}>
                    {formatDate(conv.updated_at || conv.created_at)}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Main Chat Area */}
        <div style={{
          ...styles.chatArea,
          ...(showSidebar ? {} : styles.chatAreaFull)
        }}>
          {currentConversation ? (
            <>
              {/* Messages */}
              <div style={styles.messagesContainer}>
                {messages.length === 0 ? (
                  <div style={styles.emptyMessages}>
                    <p>메시지를 보내 대화를 시작하세요.</p>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <div
                      key={msg.id || idx}
                      style={{
                        ...styles.messageRow,
                        ...(msg.type === 'human' ? styles.messageRowUser : styles.messageRowAssistant)
                      }}
                    >
                      <div style={{
                        ...styles.messageBubble,
                        ...(msg.type === 'human' ? styles.messageBubbleUser : styles.messageBubbleAssistant),
                        ...(msg.pending ? styles.messageBubblePending : {})
                      }}>
                        <div style={styles.messageContent}>{formatContent(msg.content)}</div>
                        <div style={styles.messageMetaRow}>
                          <div style={styles.messageTime}>{formatTime(msg.created_at)}</div>
                          {msg.pending && <div style={styles.pendingLabel}>전송 중...</div>}
                        </div>
                      </div>
                    </div>
                  ))
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Form */}
              <form onSubmit={sendMessage} style={styles.inputForm}>
                {error && <div style={styles.inlineError}>{error}</div>}
                <div style={styles.inputRow}>
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="메시지를 입력하세요..."
                    style={styles.messageInput}
                    disabled={sending}
                  />
                  <button 
                    type="submit" 
                    disabled={!newMessage.trim() || sending}
                    style={styles.sendButton}
                  >
                    {sending ? '...' : '전송'}
                  </button>
                </div>
              </form>
            </>
          ) : (
            <div style={styles.noConversation}>
              <div style={styles.noConversationCard}>
                <h3 style={{ marginBottom: '12px' }}>대화를 선택하거나 새 대화를 시작하세요</h3>
                <p style={{ color: '#6b7280', fontSize: '14px' }}>
                  왼쪽 목록에서 대화를 선택하거나<br />
                  '새 대화' 버튼을 클릭하세요.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

const formatContent = (content) => {
  if (typeof content === 'string') {
    return content;
  }

  if (Array.isArray(content)) {
    return content
      .map((part) => (part.type === 'text' ? part.text : '[image]'))
      .join('\n');
  }

  return '';
};

const styles = {
  container: {
    height: 'calc(100vh - 68px)',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#f5f5f5',
  },
  mobileHeader: {
    display: 'none',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '12px 16px',
    backgroundColor: '#1e293b',
    color: 'white',
  },
  menuButton: {
    background: 'transparent',
    border: 'none',
    color: 'white',
    fontSize: '20px',
    cursor: 'pointer',
    padding: '8px',
    width: '40px',
    height: '40px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: '18px',
    fontWeight: '600',
  },
  layout: {
    display: 'flex',
    flex: 1,
    overflow: 'hidden',
  },
  sidebar: {
    width: '280px',
    backgroundColor: '#1e293b',
    display: 'flex',
    flexDirection: 'column',
    flexShrink: 0,
  },
  sidebarHidden: {
    display: 'none',
  },
  sidebarHeader: {
    padding: '20px 16px',
    borderBottom: '1px solid rgba(255,255,255,0.1)',
  },
  sidebarTitle: {
    color: 'white',
    fontSize: '18px',
    marginBottom: '12px',
  },
  newChatButton: {
    width: '100%',
    padding: '10px 16px',
    backgroundColor: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
  },
  conversationList: {
    flex: 1,
    overflowY: 'auto',
    padding: '8px 0',
  },
  conversationItem: {
    padding: '12px 16px',
    cursor: 'pointer',
    borderBottom: '1px solid rgba(255,255,255,0.05)',
    transition: 'background-color 0.2s',
  },
  conversationItemActive: {
    backgroundColor: 'rgba(37, 99, 235, 0.3)',
  },
  conversationTitle: {
    color: 'white',
    fontSize: '14px',
    fontWeight: '500',
    marginBottom: '4px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  },
  conversationMeta: {
    color: '#9ca3af',
    fontSize: '12px',
  },
  emptyState: {
    padding: '40px 16px',
    textAlign: 'center',
    color: '#9ca3af',
  },
  chatArea: {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: 'white',
    minWidth: 0,
  },
  chatAreaFull: {
    flex: 1,
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto',
    padding: '20px',
    display: 'flex',
    flexDirection: 'column',
    gap: '16px',
  },
  emptyMessages: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    color: '#9ca3af',
  },
  messageRow: {
    display: 'flex',
    marginBottom: '8px',
  },
  messageRowUser: {
    justifyContent: 'flex-end',
  },
  messageRowAssistant: {
    justifyContent: 'flex-start',
  },
  messageBubble: {
    maxWidth: '70%',
    padding: '12px 16px',
    borderRadius: '12px',
    position: 'relative',
  },
  messageBubbleUser: {
    backgroundColor: '#2563eb',
    color: 'white',
    borderBottomRightRadius: '4px',
  },
  messageBubbleAssistant: {
    backgroundColor: '#f3f4f6',
    color: '#1f2937',
    borderBottomLeftRadius: '4px',
  },
  messageContent: {
    fontSize: '14px',
    lineHeight: '1.5',
    wordBreak: 'break-word',
  },
  messageTime: {
    fontSize: '11px',
    marginTop: '4px',
    opacity: '0.7',
  },
  messageMetaRow: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginTop: '4px',
  },
  messageBubblePending: {
    opacity: '0.72',
  },
  pendingLabel: {
    fontSize: '11px',
    opacity: '0.78',
  },
  inputForm: {
    padding: '16px 20px',
    borderTop: '1px solid #e5e7eb',
    backgroundColor: 'white',
  },
  inlineError: {
    color: '#dc2626',
    fontSize: '13px',
    marginBottom: '8px',
  },
  inputRow: {
    display: 'flex',
    gap: '12px',
  },
  messageInput: {
    flex: 1,
    padding: '12px 16px',
    border: '1px solid #e5e7eb',
    borderRadius: '8px',
    fontSize: '14px',
    outline: 'none',
    transition: 'border-color 0.2s',
  },
  sendButton: {
    padding: '12px 24px',
    backgroundColor: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '14px',
    cursor: 'pointer',
    transition: 'background-color 0.2s',
    flexShrink: 0,
  },
  noConversation: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    padding: '20px',
  },
  noConversationCard: {
    textAlign: 'center',
    padding: '40px',
    backgroundColor: '#f9fafb',
    borderRadius: '8px',
    maxWidth: '320px',
  },
};

// Add responsive styles via media query injection
const mediaQueryStyles = `
  @media (max-width: 768px) {
    .chat-container [style*="mobileHeader"] {
      display: flex !important;
    }
  }
`;

export default Chat;
