import { Link, useNavigate } from 'react-router-dom';

function Navbar({ onLogout }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    onLogout();
    navigate('/login');
  };

  return (
    <nav style={{ background: '#1e293b', padding: '16px 0' }}>
      <div className="container" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none', fontSize: '20px', fontWeight: 'bold' }}>
          chat-base-starter
        </Link>
        <div style={{ display: 'flex', gap: '24px' }}>
          <Link to="/dashboard" style={{ color: 'white', textDecoration: 'none' }}>홈</Link>
          <Link to="/search" style={{ color: 'white', textDecoration: 'none' }}>기업 검색</Link>
          <Link to="/chat" style={{ color: 'white', textDecoration: 'none' }}>채팅</Link>
          <button onClick={handleLogout} style={{ background: '#dc2626' }}>로그아웃</button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;
