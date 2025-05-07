# Softphone Application

A web-based softphone application built with Python, Flask, and Twilio. This application allows you to make and receive voice calls, as well as send and receive SMS/WhatsApp messages through a web interface.

## Features

- **Voice Calls**: Make and receive voice calls directly from your browser
- **Messaging**: Send and receive SMS and WhatsApp messages
- **Real-time Updates**: Instant display of incoming messages and call status
- **Audio Device Management**: Select and manage your audio input/output devices
- **Event Logging**: Comprehensive logging of all communication events
- **Endpoint Security**: Utilizes JWT Token for authorization.

## Project Structure

- `backend/`: in construction

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

- Backend: Python, Flask, WebHooks
- Frontend: HTML5, CSS3, JavaScript
- Communication: Twilio Voice and Messaging APIs

## Credit

- This project has used and modified code examples provided by Twilio as part of their SDK.
