# Softphone Application

A modern web-based softphone application built with Python, Flask, and Twilio. This application allows you to make and receive voice calls, as well as send and receive SMS/WhatsApp messages through a clean web interface.

## Features

- **Voice Calls**: Make and receive voice calls directly from your browser
- **Messaging**: Send and receive SMS and WhatsApp messages
- **Real-time Updates**: Instant display of incoming messages and call status
- **Audio Device Management**: Select and manage your audio input/output devices
- **Event Logging**: Comprehensive logging of all communication events
- **Endpoint Security**: Utilizes JWT Token for authorization.

## Project Structure

- `backend/`: Flask server and Twilio integration
- `backend/static/`: Frontend assets and JavaScript
- `backend/templates/`: HTML templates
- `backend/event_logger.py`: Event logging system

## Getting Started

1. Clone the repository
2. Set up your environment variables in `.env`:
   ```
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_CALLER_ID=your_twilio_number
   TWILIO_TWIML_APP_SID=your_twiml_app_sid
   API_KEY=your_api_key
   API_SECRET=your_api_secret
   ```
3. Follow the setup instructions in `backend/README.md`

## Development

- Backend: Python 3.x with Flask
- Frontend: HTML5, CSS3, JavaScript with jQuery
- Real-time: Server-Sent Events (SSE)
- Communication: Twilio Voice and Messaging APIs

## License

MIT License
