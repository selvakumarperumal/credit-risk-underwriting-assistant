import { useState } from 'react';
import { sampleApplicantData } from '../services/api';
import './ApplicantForm.css';

export default function ApplicantForm({ onSubmit, isLoading, onUseStreaming, useStreaming }) {
    const [applicantText, setApplicantText] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (applicantText.trim() && !isLoading) {
            onSubmit(applicantText);
        }
    };

    const handleLoadSample = () => {
        setApplicantText(sampleApplicantData);
    };

    const handleClear = () => {
        setApplicantText('');
    };

    return (
        <form onSubmit={handleSubmit} className="applicant-form glass-card fade-in">
            <div className="form-header">
                <h2>Loan Applicant Profile</h2>
                <p className="form-description">
                    Enter the applicant's details below. Include information about income,
                    employment, credit history, and loan requirements.
                </p>
            </div>

            <div className="form-body">
                <div className="form-group">
                    <div className="label-row">
                        <label htmlFor="applicant-text" className="label">
                            Applicant Information
                        </label>
                        <div className="quick-actions">
                            <button
                                type="button"
                                className="btn btn-ghost btn-sm"
                                onClick={handleLoadSample}
                                disabled={isLoading}
                            >
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                    <path d="M4 2V14M4 2L8 6M4 2L0 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" transform="translate(4, 0) rotate(90 4 8)" />
                                </svg>
                                Load Sample
                            </button>
                            {applicantText && (
                                <button
                                    type="button"
                                    className="btn btn-ghost btn-sm"
                                    onClick={handleClear}
                                    disabled={isLoading}
                                >
                                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                        <path d="M4 4L12 12M4 12L12 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
                                    </svg>
                                    Clear
                                </button>
                            )}
                        </div>
                    </div>
                    <textarea
                        id="applicant-text"
                        className="textarea"
                        value={applicantText}
                        onChange={(e) => setApplicantText(e.target.value)}
                        placeholder={`Enter applicant details, for example:

Applicant: John Doe
Monthly Income: ₹75,000
Existing EMIs: ₹15,000
Loan Amount Requested: ₹20,00,000
Property Value: ₹30,00,000
Credit Score: 720
Employment: Salaried, 5 years at current company
Total Work Experience: 10 years`}
                        disabled={isLoading}
                    />
                    <div className="textarea-footer">
                        <span className="char-count">
                            {applicantText.length} characters
                        </span>
                    </div>
                </div>

                <div className="form-options">
                    <label className="toggle-label">
                        <input
                            type="checkbox"
                            checked={useStreaming}
                            onChange={(e) => onUseStreaming(e.target.checked)}
                            disabled={isLoading}
                        />
                        <span className="toggle-switch"></span>
                        <span className="toggle-text">
                            Stream response in real-time
                        </span>
                    </label>
                </div>
            </div>

            <div className="form-footer">
                <button
                    type="submit"
                    className="btn btn-primary btn-lg submit-btn"
                    disabled={!applicantText.trim() || isLoading}
                >
                    {isLoading ? (
                        <>
                            <span className="spinner"></span>
                            Analyzing...
                        </>
                    ) : (
                        <>
                            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                                <path d="M10 3V17M10 3L4 9M10 3L16 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" transform="rotate(90 10 10)" />
                            </svg>
                            Analyze Risk
                        </>
                    )}
                </button>
            </div>
        </form>
    );
}
