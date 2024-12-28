# Softphone Backend

Flask-based backend server for the Softphone application, handling Twilio integration, real-time events, and communication logging.

There is modified user-interface based off of the backend provide by Twilio at https://github.com/TwilioDevEd/voice-javascript-sdk-quickstart-python?tab=readme-ov-file. The modified user interface is very basic and only for testing. A more complete and robust user interface is in progress, and can be found in the frontend folder.

## Setup

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the backend directory with your Twilio credentials:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_CALLER_ID=your_twilio_number
   TWILIO_TWIML_APP_SID=your_twiml_app_sid
   API_KEY=your_api_key
   API_SECRET=your_api_secret
   ```

4. Run the development server:
   ```bash
   python main.py
   ```

## Project Structure

- `main.py`: Main Flask application with routes and Twilio integration
- `event_logger.py`: Event logging system for calls and messages
- `static/`: Frontend assets
  - `softphone.js`: Main JavaScript file for UI and Twilio Device
  - `styles.css`: Application styles
- `templates/`: HTML templates
- `requirements.txt`: Python dependencies
- `softphone_events.log`: Event log file

## API Endpoints

- `/`: Main application interface
- `/token`: Generate Twilio access token
- `/voice`: Handle voice calls
- `/events`: Server-sent events endpoint
- `/send-message`: Send SMS/WhatsApp messages
- `/incoming-message`: Webhook for incoming messages

## Event Logging

The application logs all communication events (calls and messages) to `softphone_events.log` with the following information:
- Event type (call/message)
- Direction (incoming/outgoing)
- Status (received/sent/failure/missed/completed)
- Channel (voice/sms/whatsapp)
- Timestamps
- Error information (if applicable)

## Development

To run the server in development mode with debug logging:
```bash
export FLASK_ENV=development
export FLASK_DEBUG=1
python main.py
```

