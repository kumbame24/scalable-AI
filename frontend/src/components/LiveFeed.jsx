import React, { useState, useEffect } from 'react';
import { Video, Mic, Maximize2 } from 'lucide-react';

export default function LiveFeed() {
    const [isCameraOn, setIsCameraOn] = useState(true);
    const [isCaptionsOn, setIsCaptionsOn] = useState(true);

    const toggleCamera = async (turnOn) => {
        const endpoint = turnOn ? 'start' : 'stop';
        try {
            await fetch(`http://localhost:5001/camera/${endpoint}`, { method: 'POST' });
            setIsCameraOn(turnOn);
        } catch (error) {
            console.error('Failed to toggle camera:', error);
        }
    };

    const toggleCaptions = async (turnOn) => {
        const endpoint = turnOn ? 'start' : 'stop';
        try {
            await fetch(`http://localhost:5001/captions/${endpoint}`, { method: 'POST' });
            setIsCaptionsOn(turnOn);
        } catch (error) {
            console.error('Failed to toggle captions:', error);
        }
    };

    // Fetch initial status
    useEffect(() => {
        const checkStatus = async () => {
            try {
                const res = await fetch('http://localhost:5001/status');
                if (res.ok) {
                    const data = await res.json();
                    setIsCameraOn(data.camera_active);
                    setIsCaptionsOn(data.captions_active !== false); // Default to true if missing
                }
            } catch (e) {
                console.error("Failed to check status", e);
            }
        };
        checkStatus();
    }, []);

    return (
        <div className="live-feed-container">
            <div className="feed-header-strip">
                <div className="feed-title-group">
                    <span className="live-dot"></span>
                    <span className="feed-title">Simulated Monitoring Feed</span>
                    <span className="session-id">SESSION ID: 482-10X</span>
                </div>
                <div className="feed-controls">
                    <button className="icon-btn-small" title="Toggle Camera" onClick={() => toggleCamera(!isCameraOn)}>
                        <Video size={16} color={isCameraOn ? "#10B981" : "#6B7280"} />
                    </button>
                    <button className="icon-btn-small" title="Toggle Captions" onClick={() => toggleCaptions(!isCaptionsOn)}>
                        <div style={{ fontWeight: 'bold', fontSize: '10px', color: isCaptionsOn ? "#2563EB" : "#6B7280" }}>TXT</div>
                    </button>
                    <button className="icon-btn-small">
                        <Mic size={16} />
                    </button>
                    <button className="icon-btn-small">
                        <Maximize2 size={16} />
                    </button>
                </div>
            </div>

            <div className="video-wrapper">
                {isCameraOn ? (
                    <img
                        src="http://localhost:5001/video_feed"
                        alt="Live Stream"
                        className="video-player"
                        onError={(e) => {
                            e.target.onerror = null;
                            e.target.src = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='640' height='480'%3E%3Crect fill='%23333' width='640' height='480'/%3E%3Ctext x='50%' y='50%' font-size='24' fill='white' text-anchor='middle' dominant-baseline='middle'%3ECamera Feed Unavailable%3C/text%3E%3C/svg%3E";
                        }}
                    />
                ) : (
                    <div className="camera-off-placeholder">
                        <span>Camera Offline</span>
                        <p style={{ fontSize: '1.2rem', marginBottom: '5px' }}>Webcam is OFF</p>
                        <small>Click Video Icon above to resume</small>
                    </div>
                )}
                <div className="demo-live-badge">
                    <span className="blink-dot"></span> DEMO LIVE
                </div>
            </div>
        </div>
    );
}
