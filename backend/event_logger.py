import logging
from datetime import datetime
from typing import Literal, Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('softphone_events.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_event(
    event_type: Literal['call', 'message'],
    direction: Literal['incoming', 'outgoing'],
    status: Literal['received', 'sent', 'failure', 'missed', 'completed'],
    from_number: str,
    to_number: str,
    channel: Literal['voice', 'sms', 'whatsapp'],
    duration: Optional[int] = None,
    message_body: Optional[str] = None,
    error: Optional[str] = None,
    event_id: Optional[str] = None  # call_sid or message_sid
) -> None:
    """
    Log communication events (calls or messages) with consistent formatting
    
    Args:
        event_type: Type of event ('call' or 'message')
        direction: Direction of communication ('incoming' or 'outgoing')
        status: Status of the event ('received', 'sent', 'failure', 'missed', 'completed')
        from_number: Source phone number
        to_number: Destination phone number
        channel: Communication channel ('voice', 'sms', 'whatsapp')
        duration: Call duration in seconds (for calls only)
        message_body: Content of the message (for messages only)
        error: Error message if status is 'failure'
        event_id: Unique identifier for the event (call_sid or message_sid)
    """
    event_data = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'direction': direction,
        'status': status,
        'from_number': from_number,
        'to_number': to_number,
        'channel': channel,
        'event_id': event_id
    }

    if duration is not None:
        event_data['duration'] = duration
    
    if message_body is not None:
        event_data['message_body'] = message_body
    
    if error is not None:
        event_data['error'] = error

    if status == 'failure':
        logger.error(f"Communication {event_type} {status}: {event_data}")
    else:
        logger.info(f"Communication {event_type} {status}: {event_data}")
