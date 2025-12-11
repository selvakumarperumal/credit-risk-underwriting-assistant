// Use VITE_API_URL from environment (set during build), fallback to localhost for dev
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8001';

// Debug: Log API URL (check browser console to verify correct URL is being used)
console.log('API_BASE_URL:', API_BASE_URL);

/**
 * Check backend health status
 */
export async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return await response.json();
    } catch (error) {
        console.error('Health check failed:', error);
        return {
            status: 'error',
            service: 'Credit Risk Underwriting Assistant',
            model: 'unknown',
            api_key_configured: false,
            error: error.message
        };
    }
}

/**
 * Analyze applicant with full response
 */
export async function analyzeApplicant(applicantText) {
    const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ applicant_text: applicantText }),
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
}

/**
 * Analyze applicant with streaming response
 * @param {string} applicantText - The applicant information
 * @param {function} onChunk - Callback for each chunk of text
 * @param {function} onComplete - Callback when streaming completes
 * @param {function} onError - Callback for errors
 */
export async function analyzeApplicantStream(applicantText, onChunk, onComplete, onError) {
    try {
        const response = await fetch(`${API_BASE_URL}/analyze/stream`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ applicant_text: applicantText }),
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                if (onComplete) onComplete();
                break;
            }

            buffer += decoder.decode(value, { stream: true });

            // Process Server-Sent Events
            const lines = buffer.split('\n\n');
            buffer = lines.pop() || '';

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    const data = line.slice(6);
                    if (data === '[DONE]') {
                        if (onComplete) onComplete();
                        return;
                    }
                    if (onChunk) onChunk(data);
                }
            }
        }
    } catch (error) {
        console.error('Streaming error:', error);
        if (onError) onError(error);
    }
}

/**
 * Sample applicant data for quick testing
 */
export const sampleApplicantData = `Applicant: Rajesh Kumar
Age: 35 years
Monthly Income: ₹85,000
Employment Type: Salaried (IT Professional)
Current Employer: TCS
Years at Current Company: 6 years
Total Work Experience: 12 years

Loan Details:
- Loan Amount Requested: ₹45,00,000
- Loan Type: Home Loan
- Property Value: ₹60,00,000
- Property Location: Bangalore

Existing Liabilities:
- Car Loan EMI: ₹12,000 (18 months remaining)
- Credit Card Outstanding: ₹35,000
- Credit Card Limit: ₹2,50,000

Credit History:
- Credit Score: 745
- Credit History Length: 8 years
- Number of Active Loans: 1
- Payment History: No defaults

Bank Relationship:
- Savings Account Balance: ₹2,50,000
- Fixed Deposits: ₹5,00,000
- Existing Customer: Yes (5 years)`;
