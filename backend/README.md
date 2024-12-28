# Softphone Backend API

A Flask-based backend API for a softphone application that supports voice calls, SMS, and WhatsApp messaging using Twilio.

## Features

- Voice calls (outbound and inbound)
- SMS messaging (outbound and inbound)
- WhatsApp messaging and calls
- Webhook handling for incoming communications
- Basic authentication for API endpoints
- Media handling support

## Prerequisites

- Python 3.8+
- Twilio account with:
  - Account SID
  - Auth Token
  - Twilio phone number
  - WhatsApp-enabled number (for WhatsApp features)
- ngrok (for local development)

## Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
    TWILIO_ACCOUNT_SID=your_account_sid
    TWILIO_AUTH_TOKEN=your_auth_token
    TWILIO_PHONE_NUMBER=your_twilio_phone_number
    API_USERNAME=your_api_username
    API_PASSWORD=your_api_password
  ```
  ```bash
   pip install -r requirements.txt
  ```

5. Create a `.env` file with your credentials:
   ```bash
   TWILIO_ACCOUNT_SID=your_account_sid
   TWILIO_AUTH_TOKEN=your_auth_token
   TWILIO_PHONE_NUMBER=your_twilio_phone_number
   API_USERNAME=your_api_username
   API_PASSWORD=your_api_password
   ```

## Running the Server

1. Start the Flask server:
   ```bash
   python main.py
   ```

2. Expose your local server using ngrok:
   ```bash
   ngrok http 5000
   ```

3. Update your Twilio webhook URLs with the ngrok URL:
   - Voice calls: `https://your-ngrok-url/webhook/incoming-call`
   - Messages: `https://your-ngrok-url/webhook/incoming-message`

## API Endpoints

### Make a Call
```bash
curl -X POST http://localhost:5000/api/call \
-u "username:password" \
-H "Content-Type: application/json" \
-d '{
    "to": "+1234567890",
    "whatsapp": false
}'
```

### Send a Message (SMS or WhatsApp)
```bash
curl -X POST http://localhost:5000/api/message \
-u "username:password" \
-H "Content-Type: application/json" \
-d '{
    "to": "+1234567890",
    "message": "Hello!",
    "type": "sms",
    "media_url": "https://example.com/image.jpg"
}'
```

## Security Considerations

1. **Environment Variables**
   - Never commit `.env` file to version control
   - Rotate your Twilio auth token periodically
   - Use strong passwords for API authentication

2. **ngrok Usage**
   - ngrok URLs are public and can be accessed by anyone
   - Use basic authentication (already implemented)
   - Consider IP whitelisting in production
   - Monitor your ngrok dashboard for suspicious activity

3. **Production Deployment**
   - Use HTTPS only
   - Implement rate limiting
   - Set up proper monitoring and logging
   - Use a production-grade server (e.g., Gunicorn)
   - Consider using a CDN
   - Implement proper input validation and sanitization

4. **Twilio Best Practices**
   - Validate incoming webhook requests using Twilio's signature verification
   - Use webhook authentication
   - Monitor your Twilio console for unusual activity
   - Set up spending limits and alerts

## Webhook Endpoints

The API provides webhook endpoints for handling incoming communications:

- `/webhook/incoming-call`: Handles incoming voice calls
- `/webhook/incoming-message`: Handles incoming SMS and WhatsApp messages

## Error Handling

The API includes comprehensive error handling for:
- Invalid requests
- Authentication failures
- Twilio API errors
- General server errors

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
