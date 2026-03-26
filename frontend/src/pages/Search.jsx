import { useState } from 'react';
import { companiesAPI, interestsAPI } from '../api/companies';

function Search() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError('');
    try {
      const response = await companiesAPI.search(query);
      setResults(response.data);
    } catch (err) {
      setError('검색에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddInterest = async (company) => {
    try {
      await interestsAPI.add({
        companyRefId: company.id,
        companyCode: company.code,
        companyName: company.name
      });
      setSuccessMessage(`${company.name}을(를) 관심종목에 추가했습니다.`);
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setError(err.response?.data?.message || '추가에 실패했습니다.');
    }
  };

  return (
    <div className="container">
      <h1>기업 검색</h1>

      <form onSubmit={handleSearch} style={{ marginTop: '24px', marginBottom: '24px' }}>
        <div className="input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="기업명 또는 종목코드로 검색 (예: 삼성전자, 005930)"
          />
          <button type="submit" disabled={loading}>
            {loading ? '검색 중...' : '검색'}
          </button>
        </div>
      </form>

      {successMessage && <div className="success" style={{ marginBottom: '16px' }}>{successMessage}</div>}
      {error && <div className="error" style={{ marginBottom: '16px' }}>{error}</div>}

      {results.length > 0 && (
        <div>
          <h2>검색 결과 ({results.length})</h2>
          <div style={{ display: 'grid', gap: '12px', marginTop: '16px' }}>
            {results.map((company) => (
              <div key={company.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <h3 style={{ fontSize: '18px', marginBottom: '4px' }}>{company.name}</h3>
                  <p style={{ color: '#6b7280', fontSize: '14px' }}>
                    {company.code} | {company.market} | {company.sector}
                  </p>
                </div>
                <button onClick={() => handleAddInterest(company)}>
                  관심종목 추가
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {query && results.length === 0 && !loading && (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          검색 결과가 없습니다.
        </div>
      )}

      {!query && (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p>기업명 또는 종목코드로 검색해보세요.</p>
          <p style={{ marginTop: '12px', color: '#6b7280', fontSize: '14px' }}>
            검색어 예시: 삼성전자, LG에너지솔루션, 005930
          </p>
        </div>
      )}
    </div>
  );
}

export default Search;
