import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './AnalysisResult.css';

export default function AnalysisResult({ result, isStreaming, streamContent }) {
    const [copied, setCopied] = useState(false);

    // Use streamContent if available (streaming mode), otherwise use result.response
    const content = streamContent || result?.response;
    const toolsUsed = result?.tools_used || [];
    const messageCount = result?.message_count || 0;

    const handleCopy = async () => {
        try {
            await navigator.clipboard.writeText(content);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    if (!content && !isStreaming) return null;

    return (
        <div className="analysis-result glass-card fade-in">
            <div className="result-header">
                <div className="result-title">
                    <h2>
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                            <path d="M9 12L11 14L15 10M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                        </svg>
                        Risk Assessment Report
                    </h2>
                    {isStreaming && (
                        <span className="streaming-badge">
                            <span className="loading-dots">
                                <span></span>
                                <span></span>
                                <span></span>
                            </span>
                            Streaming
                        </span>
                    )}
                </div>

                <div className="result-actions">
                    <button className="btn btn-ghost" onClick={handleCopy} title="Copy to clipboard">
                        {copied ? (
                            <>
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                    <path d="M3 8L6 11L13 4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                                </svg>
                                Copied!
                            </>
                        ) : (
                            <>
                                <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                    <rect x="5" y="5" width="9" height="9" rx="1" stroke="currentColor" strokeWidth="1.5" />
                                    <path d="M11 5V3C11 2.44772 10.5523 2 10 2H3C2.44772 2 2 2.44772 2 3V10C2 10.5523 2.44772 11 3 11H5" stroke="currentColor" strokeWidth="1.5" />
                                </svg>
                                Copy
                            </>
                        )}
                    </button>
                </div>
            </div>

            {(toolsUsed.length > 0 || messageCount > 0) && !isStreaming && (
                <div className="result-meta">
                    {toolsUsed.length > 0 && (
                        <div className="tools-used">
                            <span className="meta-label">Tools Used:</span>
                            <div className="tool-badges">
                                {toolsUsed.map((tool, index) => (
                                    <span key={index} className="badge badge-primary">
                                        {tool.replace(/_/g, ' ')}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                    {messageCount > 0 && (
                        <div className="message-count">
                            <span className="badge">{messageCount} messages</span>
                        </div>
                    )}
                </div>
            )}

            <div className="result-content markdown-content">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {content}
                </ReactMarkdown>
                {isStreaming && <span className="typing-cursor"></span>}
            </div>
        </div>
    );
}
