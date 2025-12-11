import { useState } from 'react';
import Header from './components/Header';
import ApplicantForm from './components/ApplicantForm';
import AnalysisResult from './components/AnalysisResult';
import { analyzeApplicant, analyzeApplicantStream } from './services/api';
import './App.css';

function App() {
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamContent, setStreamContent] = useState('');
  const [useStreaming, setUseStreaming] = useState(true);
  const [error, setError] = useState(null);

  const handleSubmit = async (applicantText) => {
    setIsLoading(true);
    setError(null);
    setResult(null);
    setStreamContent('');

    try {
      if (useStreaming) {
        // Streaming mode
        setIsStreaming(true);

        await analyzeApplicantStream(
          applicantText,
          // onChunk
          (chunk) => {
            setStreamContent(prev => prev + chunk);
          },
          // onComplete
          () => {
            setIsStreaming(false);
            setIsLoading(false);
          },
          // onError
          (err) => {
            setError(err.message);
            setIsStreaming(false);
            setIsLoading(false);
          }
        );
      } else {
        // Full response mode
        const response = await analyzeApplicant(applicantText);
        setResult(response);
        setIsLoading(false);
      }
    } catch (err) {
      setError(err.message);
      setIsLoading(false);
      setIsStreaming(false);
    }
  };

  const dismissError = () => {
    setError(null);
  };

  return (
    <div className="app">
      <Header />

      <main className="main-content">
        <div className="container">
          <div className="page-intro fade-in">
            <h1 className="page-title">
              <span className="gradient-text">Analyze Credit Risk</span>
            </h1>
            <p className="page-subtitle">
              Get comprehensive risk assessments powered by AI. Enter loan applicant
              details and receive instant underwriting recommendations.
            </p>
          </div>

          {error && (
            <div className="error-toast glass-card fade-in">
              <div className="error-content">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                  <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5" />
                  <path d="M10 6V10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                  <circle cx="10" cy="13" r="1" fill="currentColor" />
                </svg>
                <span>{error}</span>
              </div>
              <button className="error-dismiss" onClick={dismissError}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                  <path d="M4 4L12 12M4 12L12 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                </svg>
              </button>
            </div>
          )}

          <div className="content-grid">
            <div className="form-section">
              <ApplicantForm
                onSubmit={handleSubmit}
                isLoading={isLoading}
                useStreaming={useStreaming}
                onUseStreaming={setUseStreaming}
              />
            </div>

            <div className="result-section">
              {(result || streamContent || isStreaming) && (
                <AnalysisResult
                  result={result}
                  isStreaming={isStreaming}
                  streamContent={streamContent}
                />
              )}

              {!result && !streamContent && !isStreaming && !isLoading && (
                <div className="empty-state glass-card fade-in">
                  <div className="empty-icon">
                    <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                      <circle cx="24" cy="24" r="20" stroke="currentColor" strokeWidth="2" strokeDasharray="4 4" />
                      <path d="M18 24L22 28L30 20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                  <h3>Ready to Analyze</h3>
                  <p>
                    Enter loan applicant information in the form to generate
                    a comprehensive credit risk assessment report.
                  </p>
                  <div className="features-list">
                    <div className="feature-item">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 8L6 12L14 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      <span>DTI & LTV ratio calculations</span>
                    </div>
                    <div className="feature-item">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 8L6 12L14 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      <span>Credit score analysis</span>
                    </div>
                    <div className="feature-item">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 8L6 12L14 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      <span>Risk classification</span>
                    </div>
                    <div className="feature-item">
                      <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                        <path d="M2 8L6 12L14 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                      </svg>
                      <span>Underwriting recommendations</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>

      <footer className="footer">
        <div className="container">
          <p>Credit Risk Underwriting Assistant • Powered by Google Gemini AI</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
