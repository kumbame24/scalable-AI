from typing import Optional, List, Tuple
from datetime import datetime, timedelta


def fuse(video_conf: float, audio_conf: float, weights: Tuple[float, float] = (0.7, 0.3)) -> float:
    """
    Fuse video and audio confidence scores using weighted fusion.
    
    Args:
        video_conf: Video detection confidence (0-1)
        audio_conf: Audio detection confidence (0-1)
        weights: Tuple of (video_weight, audio_weight), must sum to 1.0
    
    Returns:
        Fused confidence score (0-1)
    """
    if not video_conf and not audio_conf:
        return 0.0
    
    if video_conf and not audio_conf:
        return video_conf * weights[0]
    
    if audio_conf and not video_conf:
        return audio_conf * weights[1]
    
    # Both present: weighted sum
    return (video_conf * weights[0] + audio_conf * weights[1])


def temporal_fusion(
    events: List[dict],
    time_window: float = 2.0
) -> List[dict]:
    """
    Fuse events occurring within a temporal window.
    
    Args:
        events: List of event dicts with 'timestamp', 'confidence', 'event_type'
        time_window: Time window in seconds for fusion
    
    Returns:
        List of fused events
    """
    if not events:
        return []
    
    # Sort by timestamp
    sorted_events = sorted(events, key=lambda x: x.get('timestamp', 0))
    fused = []
    current_group = [sorted_events[0]]
    
    for event in sorted_events[1:]:
        current_time = event.get('timestamp', 0)
        group_time = current_group[0].get('timestamp', 0)
        
        if current_time - group_time <= time_window:
            current_group.append(event)
        else:
            # Fuse and save current group
            if current_group:
                fused.append(_fuse_group(current_group))
            current_group = [event]
    
    # Don't forget the last group
    if current_group:
        fused.append(_fuse_group(current_group))
    
    return fused


def _fuse_group(event_group: List[dict]) -> dict:
    """
    Fuse a group of events into a single event.
    """
    if not event_group:
        return {}
    
    # Calculate average confidence
    avg_conf = sum(e.get('confidence', 0) for e in event_group) / len(event_group)
    
    # Collect event types
    event_types = list(set(e.get('event_type', 'UNKNOWN') for e in event_group))
    
    # Use earliest timestamp
    timestamp = min(e.get('timestamp', 0) for e in event_group)
    
    # Use first source or combine
    sources = list(set(e.get('source', 'unknown') for e in event_group))
    
    return {
        'event_types': event_types,
        'fused_confidence': avg_conf,
        'timestamp': timestamp,
        'sources': sources,
        'event_count': len(event_group)
    }


def cross_modal_fusion(
    video_event: Optional[dict],
    audio_event: Optional[dict],
    time_tolerance: float = 1.0
) -> Optional[dict]:
    """
    Fuse video and audio events if they occur close in time.
    
    Args:
        video_event: Video detection event
        audio_event: Audio detection event
        time_tolerance: Maximum time difference in seconds for fusion
    
    Returns:
        Fused event or None if events are too far apart
    """
    if not video_event and not audio_event:
        return None
    
    if not video_event or not audio_event:
        # Only one modality detected - return with lower confidence
        event = video_event or audio_event
        return {**event, 'fused_confidence': event.get('confidence', 0) * 0.8, 'modalities': 1}
    
    # Check temporal proximity
    video_time = video_event.get('timestamp', 0)
    audio_time = audio_event.get('timestamp', 0)
    
    if abs(video_time - audio_time) > time_tolerance:
        return None
    
    # Fuse the events
    video_conf = video_event.get('confidence', 0)
    audio_conf = audio_event.get('confidence', 0)
    
    fused_conf = fuse(video_conf, audio_conf)
    
    return {
        'video_confidence': video_conf,
        'audio_confidence': audio_conf,
        'fused_confidence': fused_conf,
        'event_types': [
            video_event.get('event_type', 'UNKNOWN'),
            audio_event.get('event_type', 'UNKNOWN')
        ],
        'timestamp': min(video_time, audio_time),
        'modalities': 2
    }


def fuse_and_store(event_data: dict, db_session) -> dict:
    """
    Process and store event data with optional fusion logic.
    
    Args:
        event_data: Event data dictionary
        db_session: Database session for storing events
    
    Returns:
        Dictionary with storage status
    """
    # For now, this is a placeholder that just returns the event data
    # In a full implementation, this would apply fusion logic and store to DB
    return {
        'status': 'processed',
        'event': event_data
    }
    
