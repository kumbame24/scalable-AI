import pytest
import sys
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "ai-modules" / "vision"))
sys.path.insert(0, str(Path(__file__).parent.parent / "ai-modules" / "audio"))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))


class TestBackendIntegration:
    """Test backend API and database integration"""
    
    def test_backend_imports(self):
        """Test that all backend modules can be imported"""
        try:
            from backend.database import database, models
            from backend.schemas import EventCreate, Event, AlertResponse
            from backend.database.fusion import fuse, temporal_fusion, cross_modal_fusion
            from backend.utils import validate_event_data, validate_source_field
            assert True
        except ImportError as e:
            pytest.fail(f"Backend import failed: {e}")
    
    def test_event_schema_validation(self):
        """Test Pydantic event schema validation"""
        from backend.schemas import EventCreate
        
        # Valid event
        valid_event = {
            "source": "video",
            "session_id": 1,
            "sensor_id": 1,
            "event_type": "OBJECT_DETECTED",
            "confidence": 0.85,
            "timestamp": 1000.0
        }
        
        event = EventCreate(**valid_event)
        assert event.confidence == 0.85
        assert event.source == "video"
    
    def test_event_schema_invalid_confidence(self):
        """Test that invalid confidence values are rejected"""
        from backend.schemas import EventCreate
        from pydantic import ValidationError
        
        invalid_event = {
            "source": "video",
            "session_id": 1,
            "sensor_id": 1,
            "event_type": "OBJECT_DETECTED",
            "confidence": 1.5,  # Invalid: > 1.0
            "timestamp": 1000.0
        }
        
        with pytest.raises(ValidationError):
            EventCreate(**invalid_event)
    
    def test_fusion_video_audio(self):
        """Test video and audio confidence fusion"""
        from backend.database.fusion import fuse
        
        video_conf = 0.9
        audio_conf = 0.6
        fused = fuse(video_conf, audio_conf)
        
        # Should be weighted: 0.7 * 0.9 + 0.3 * 0.6
        expected = 0.7 * 0.9 + 0.3 * 0.6
        assert abs(fused - expected) < 0.01
    
    def test_fusion_single_modality(self):
        """Test fusion with only one modality"""
        from backend.database.fusion import fuse
        
        # Only video
        fused_video_only = fuse(0.8, 0)
        assert fused_video_only == 0.8 * 0.7
        
        # Only audio
        fused_audio_only = fuse(0, 0.7)
        assert fused_audio_only == 0.7 * 0.3
    
    def test_temporal_fusion(self):
        """Test temporal event fusion"""
        from backend.database.fusion import temporal_fusion
        
        events = [
            {"timestamp": 100.0, "confidence": 0.8, "event_type": "GAZE_DEVIATION", "source": "video"},
            {"timestamp": 100.5, "confidence": 0.6, "event_type": "OBJECT_DETECTED", "source": "video"},
            {"timestamp": 103.0, "confidence": 0.7, "event_type": "AUDIO_ANOMALY", "source": "audio"},
        ]
        
        # Default time window is 2.0 seconds
        fused = temporal_fusion(events, time_window=2.0)
        
        assert len(fused) == 2  # First two should fuse, third is separate
        assert fused[0]["event_count"] == 2
        assert fused[1]["event_count"] == 1
    
    def test_cross_modal_fusion(self):
        """Test cross-modal event fusion"""
        from backend.database.fusion import cross_modal_fusion
        
        video_event = {
            "confidence": 0.85,
            "event_type": "GAZE_DEVIATION",
            "source": "video",
            "timestamp": 100.0
        }
        
        audio_event = {
            "confidence": 0.65,
            "event_type": "AUDIO_ANOMALY",
            "source": "audio",
            "timestamp": 100.2  # Close in time
        }
        
        fused = cross_modal_fusion(video_event, audio_event, time_tolerance=1.0)
        
        assert fused is not None
        assert fused["modalities"] == 2
        assert fused["fused_confidence"] > 0
    
    def test_event_data_validation(self):
        """Test event data validation utility"""
        from backend.utils import validate_event_data
        
        # Valid event
        valid = {
            "source": "video",
            "session_id": 1,
            "sensor_id": 1,
            "event_type": "OBJECT_DETECTED",
            "confidence": 0.85
        }
        is_valid, msg = validate_event_data(valid)
        assert is_valid
        assert msg == ""
        
        # Missing field
        invalid = {
            "source": "video",
            "session_id": 1,
            "event_type": "OBJECT_DETECTED",
            "confidence": 0.85
        }
        is_valid, msg = validate_event_data(invalid)
        assert not is_valid
        assert "sensor_id" in msg


class TestVisionModuleIntegration:
    """Test vision module components"""
    
    def test_camera_import(self):
        """Test camera module import"""
        try:
            from camera import Camera
            assert Camera is not None
        except ImportError as e:
            pytest.fail(f"Camera import failed: {e}")
    
    def test_object_detector_import(self):
        """Test object detector import"""
        try:
            from objects import ObjectDetector
            assert ObjectDetector is not None
        except ImportError as e:
            pytest.fail(f"ObjectDetector import failed: {e}")
    
    def test_gaze_detector_import(self):
        """Test gaze detector import with fallback"""
        try:
            from gaze import GazeDetector
            assert GazeDetector is not None
        except ImportError as e:
            pytest.fail(f"GazeDetector import failed: {e}")
    
    def test_gaze_detector_initialization(self):
        """Test gaze detector can be initialized"""
        try:
            from gaze import GazeDetector
            gaze = GazeDetector()
            assert gaze is not None
            # Should have face_landmarker or be None (fallback)
            assert hasattr(gaze, 'face_landmarker')
        except Exception as e:
            pytest.fail(f"GazeDetector initialization failed: {e}")
    
    def test_object_detector_initialization(self):
        """Test object detector can be initialized"""
        try:
            from objects import ObjectDetector
            detector = ObjectDetector()
            assert detector is not None
            assert hasattr(detector, 'model')
            assert hasattr(detector, 'suspicious')
        except Exception as e:
            pytest.fail(f"ObjectDetector initialization failed: {e}")


class TestAudioModuleIntegration:
    """Test audio module components"""
    
    def test_audio_module_imports(self):
        """Test audio module imports"""
        try:
            from capture import record
            from features import extract
            from anomaly import detect
            assert record is not None
            assert extract is not None
            assert detect is not None
        except ImportError as e:
            pytest.fail(f"Audio module import failed: {e}")
    
    def test_anomaly_detection(self):
        """Test anomaly detection logic"""
        from anomaly import detect
        
        # Low energy - no event
        result_low = detect(energy=0.001)
        assert result_low is None
        
        # High energy - event detected
        result_high = detect(energy=0.02)
        assert result_high is not None
        assert result_high["type"] == "AUDIO_ANOMALY"
        assert result_high["confidence"] == 0.6


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limiter_creation(self):
        """Test rate limiter can be created"""
        try:
            from backend.rate_limiter import RateLimiter
            limiter = RateLimiter(requests_per_second=100)
            assert limiter is not None
        except ImportError as e:
            pytest.fail(f"RateLimiter import failed: {e}")
    
    def test_rate_limiter_allow_requests(self):
        """Test rate limiter allows requests within limit"""
        from backend.rate_limiter import RateLimiter
        
        limiter = RateLimiter(requests_per_second=10)
        
        # First few requests should be allowed
        for i in range(5):
            is_allowed, info = limiter.is_allowed("test_client")
            assert is_allowed
            assert info["requests_used"] == i + 1
    
    def test_rate_limiter_blocks_excess_requests(self):
        """Test rate limiter blocks requests exceeding limit"""
        from backend.rate_limiter import RateLimiter
        
        limiter = RateLimiter(requests_per_second=5)
        
        # Use up the limit
        for i in range(5):
            is_allowed, _ = limiter.is_allowed("test_client")
            assert is_allowed
        
        # Next request should be blocked
        is_allowed, info = limiter.is_allowed("test_client")
        assert not is_allowed
        assert info["requests_used"] == 5


class TestErrorHandling:
    """Test error handling utilities"""
    
    def test_safe_detector_decorator(self):
        """Test safe detector decorator"""
        try:
            from ai_modules.error_handler import safe_detector
            
            @safe_detector("TestDetector")
            def test_detect(value):
                return {"type": "TEST", "confidence": 0.8}
            
            result = test_detect(None)
            assert result is not None
            assert result["type"] == "TEST"
        except ImportError:
            # If error_handler not available, skip
            pytest.skip("Error handler module not available")
    
    def test_validation_error_handling(self):
        """Test validation error handling"""
        try:
            from backend.utils import ValidationError
            
            with pytest.raises(ValidationError):
                raise ValidationError("Test error")
        except ImportError:
            pytest.skip("ValidationError not available")


# Run tests if executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
