import { useState, useEffect } from 'react';
import { interestsAPI, disclosuresAPI } from '../api/companies';

function Dashboard() {
  const [interests, setInterests] = useState([]);
  const [disclosures, setDisclosures] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchInterests();
  }, []);

  const fetchInterests = async () => {
    try {
      const response = await interestsAPI.list();
      setInterests(response.data);
      if (response.data.length > 0) {
        // Use companyRefId if available, otherwise skip (old data)
        const companyIds = response.data
          .map(i => i.companyRefId)
          .filter(id => id != null);
        if (companyIds.length > 0) {
          fetchDisclosures(companyIds);
        }
      }
    } catch (err) {
      setError('관심종목을 불러오는데 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchDisclosures = async (companyIds) => {
    try {
      const response = await disclosuresAPI.getLatest(companyIds);
      setDisclosures(response.data);
    } catch (err) {
      console.error('공시정보를 불러오는데 실패했습니다.', err);
    }
  };

  const handleDelete = async (id) => {
    try {
      await interestsAPI.delete(id);
      setInterests(interests.filter(i => i.id !== id));
    } catch (err) {
      setError('삭제에 실패했습니다.');
    }
  };

  if (loading) return <div className="container">로딩 중...</div>;

  return (
    <div className="container">
      <h1>관심종목 공시정보</h1>

      {error && <div className="error" style={{ marginBottom: '16px' }}>{error}</div>}

      {interests.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p>등록된 관심종목이 없습니다.</p>
          <a href="/search" style={{ color: '#2563eb', textDecoration: 'none' }}>기업 검색으로 이동</a>
        </div>
      ) : (
        <>
          <div style={{ marginBottom: '24px' }}>
            <h2>관심종목 ({interests.length})</h2>
            <div style={{ display: 'grid', gap: '12px', marginTop: '16px' }}>
              {interests.map((interest) => (
                <div key={interest.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <strong>{interest.companyName}</strong>
                    <span style={{ marginLeft: '12px', color: '#6b7280' }}>{interest.companyCode}</span>
                  </div>
                  <button onClick={() => handleDelete(interest.id)} style={{ background: '#dc2626', padding: '8px 16px' }}>
                    삭제
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h2>최신 공시정보</h2>
            {disclosures.length === 0 ? (
              <div className="card" style={{ textAlign: 'center', padding: '20px' }}>
                공시정보가 없습니다.
              </div>
            ) : (
              <div style={{ display: 'grid', gap: '12px', marginTop: '16px' }}>
                {disclosures.map((disclosure) => (
                  <div key={disclosure.id} className="card">
                    <h3 style={{ fontSize: '16px', marginBottom: '8px' }}>{disclosure.title}</h3>
                    <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '8px' }}>{disclosure.content}</p>
                    <p style={{ color: '#9ca3af', fontSize: '12px' }}>
                      {new Date(disclosure.report_date).toLocaleDateString('ko-KR')}
                    </p>
                    {disclosure.url && (
                      <a href={disclosure.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'none', fontSize: '14px' }}>
                        상세보기
                      </a>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}

export default Dashboard;
