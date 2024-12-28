from flask import Flask, request, jsonify, render_template, Response
from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VoiceGrant
from twilio.twiml.voice_response import VoiceResponse, Dial
from twilio.twiml.messaging_response import MessagingResponse
from twilio.rest import Client
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Literal
from event_logger import log_event
import logging
import re
import json
import queue
import threading

app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

alphanumeric_only = re.compile("[\W_]+")
phone_pattern = re.compile(r"^[\d\+\-\(\) ]+$")

# Load environment variables from .env
load_dotenv()

# Get credentials from environment variables
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
twilio_number = os.environ["TWILIO_CALLER_ID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]

# Store the most recently created identity in memory for routing calls
IDENTITY = {"identity": ""}

# Message queue for server-sent events
message_queue = queue.Queue()

# Frontend routes
@app.route('/')
def index():
    return app.send_static_file("index.html")

# Voice Token Generation
@app.route("/token", methods=["GET"])
def token():
    # Generate a random user name and store it
    account_sid = os.environ["TWILIO_ACCOUNT_SID"]
    application_sid = os.environ["TWILIO_TWIML_APP_SID"]
    api_key = os.environ["API_KEY"]
    api_secret = os.environ["API_SECRET"]

    # Generate a user name and store it
    identity = 'SawyersSoftphone'
    IDENTITY["identity"] = identity

    # Create access token with credentials
    token = AccessToken(account_sid, api_key, api_secret, identity=identity)

    # Create a Voice grant and add to token
    voice_grant = VoiceGrant(
        outgoing_application_sid=application_sid,
        incoming_allow=True,
    )
    token.add_grant(voice_grant)

    # Return token info as JSON
    token = token.to_jwt()
    return jsonify(identity=identity, token=token)

# Voice Routes
@app.route("/voice", methods=["POST"])
def voice():
    resp = VoiceResponse()
    if request.form.get("To") == twilio_number:
        # Receiving an incoming call to our Twilio number
        dial = Dial()
        # Route to the most recently created client based on the identity stored in the session
        dial.client(IDENTITY["identity"])
        resp.append(dial)
        
        # Log incoming call
        log_event(
            event_type='call',
            direction='incoming',
            status='received',
            from_number=request.form.get("From"),
            to_number=request.form.get("To"),
            channel='voice',
            event_id=request.form.get("CallSid")
        )
    elif request.form.get("To"):
        # Placing an outbound call from the Twilio client
        dial = Dial(caller_id=twilio_number)
        # wrap the phone number or client name in the appropriate TwiML verb
        # by checking if the number given has only digits and format symbols
        if phone_pattern.match(request.form["To"]):
            dial.number(request.form["To"])
        else:
            dial.client(request.form["To"])
        resp.append(dial)
        
        # Log outgoing call
        log_event(
            event_type='call',
            direction='outgoing',
            status='sent',
            from_number=twilio_number,
            to_number=request.form.get("To"),
            channel='voice',
            event_id=request.form.get("CallSid")
        )
    else:
        resp.say("Thanks for calling!")

    return Response(str(resp), mimetype="text/xml")

# Server-Sent Events Route
@app.route('/events')
def events():
    def generate():
        while True:
            try:
                # Get message from queue, blocking until one is available
                message = message_queue.get()
                yield f"data: {json.dumps(message)}\n\n"
            except Exception as e:
                logger.error(f"Error in event stream: {str(e)}")
                break
    
    return Response(generate(), mimetype='text/event-stream')

# SMS Routes
@app.route('/send-message', methods=['POST'])
def send_sms():
    try:
        data = request.get_json()
        to_number = data.get('to')
        message_text = data.get('message')
        channel = data.get('type', 'sms')  # 'sms' or 'whatsapp'
        
        if not to_number or not message_text:
            return jsonify({'error': 'Phone number and message are required'}), 400

        result = send_message(
            to_number=to_number,
            message=message_text,
            twilio_number=twilio_number,
            account_sid=account_sid,
            auth_token=auth_token,
            channel=channel
        )
        
        return jsonify({
            'status': 'success',
            'message_sid': result.get('message_sid'),
            'message_type': channel
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/incoming-message', methods=['POST'])
def incoming_message():
    """
    Webhook endpoint for receiving SMS messages from Twilio
    """
    try:
        # Get incoming message data
        message_data = request.form.to_dict()
        
        # Process the message
        processed_message = process_incoming_message(message_data)
        
        # Determine if it's SMS or WhatsApp
        channel = 'whatsapp' if 'whatsapp' in message_data.get('From', '').lower() else 'sms'
        
        # Create event data for logging
        log_event(
            event_type='message',
            direction='incoming',
            status='received',
            from_number=processed_message['from_number'],
            to_number=processed_message['to_number'],
            channel=channel,
            message_body=processed_message['body'],
            event_id=processed_message['message_sid']
        )
        
        # Create event data for real-time updates (includes timestamp)
        event_data = {
            'event_type': 'message',
            'direction': 'incoming',
            'status': 'received',
            'from_number': processed_message['from_number'],
            'to_number': processed_message['to_number'],
            'channel': channel,
            'message_body': processed_message['body'],
            'event_id': processed_message['message_sid'],
            'timestamp': processed_message['timestamp']
        }
        
        # Add to message queue for real-time updates
        message_queue.put(event_data)
        
        # Log the incoming message
        logger.info(f"Received SMS: {processed_message}")

        # Create response
        resp = MessagingResponse()
        resp.message(f"Thank you - message received at: {processed_message['timestamp']}")
        
        return str(resp), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")

        # Log the error event
        log_event(
            event_type='message',
            direction='incoming',
            status='failure',
            from_number=request.form.get('From', 'Unknown'),
            to_number=request.form.get('To', 'Unknown'),
            channel='unknown',
            message_body=request.form.get('Body', ''),
            error=str(e)
        )
        
        # Create error event data for real-time updates
        error_event = {
            'event_type': 'message',
            'direction': 'incoming',
            'status': 'failure',
            'from_number': request.form.get('From', 'Unknown'),
            'to_number': request.form.get('To', 'Unknown'),
            'channel': 'unknown',
            'message_body': request.form.get('Body', ''),
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }
        
        # Add error to message queue
        message_queue.put(error_event)
        
        return str(MessagingResponse()), 400

## Helper Functions ------------------------------

def process_incoming_message(message_data: dict) -> dict:
    """
    Process incoming SMS message data
    
    Args:
        message_data (dict): The message data from Twilio webhook
        
    Returns:
        dict: Processed message information
    """
    return {
        'from_number': message_data.get('From', 'Unknown'),
        'to_number': message_data.get('To', 'Unknown'),
        'body': message_data.get('Body', ''),
        'message_sid': message_data.get('MessageSid', ''),
        'timestamp': datetime.now().isoformat()
    }

def send_message(
    to_number: str, 
    message: str, 
    twilio_number: str, 
    account_sid: str, 
    auth_token: str,
    channel: Literal['sms', 'whatsapp'] = 'sms'
) -> dict:
    """
    Send a message using Twilio via SMS or WhatsApp.
    
    Args:
        to_number (str): The recipient's phone number in E.164 format
        message (str): The message content to send
        twilio_number (str): Your Twilio phone number
        account_sid (str): Twilio account SID
        auth_token (str): Twilio auth token
        channel (str): The messaging channel to use ('sms' or 'whatsapp')
    
    Returns:
        dict: Response from Twilio API containing message details
    """
    try:
        client = Client(account_sid, auth_token)
        
        # Format numbers based on channel
        if channel == 'whatsapp':
            from_number = f"whatsapp:{twilio_number}"
            to_number = f"whatsapp:{to_number}"
        else:
            from_number = twilio_number
        
        # Send message
        message_response = client.messages.create(
            body=message,
            from_=from_number,
            to=to_number
        )
        
        # Log successful message
        log_event(
            event_type='message',
            direction='outgoing',
            status='sent',
            from_number=from_number,
            to_number=to_number,
            channel=channel,
            message_body=message,
            event_id=message_response.sid
        )
        
        return {
            'status': 'success',
            'channel': channel,
            'message_sid': message_response.sid,
            'to': to_number,
            'body': message
        }
        
    except Exception as e:
        # Log failed message
        log_event(
            event_type='message',
            direction='outgoing',
            status='failure',
            from_number=twilio_number,
            to_number=to_number,
            channel=channel,
            message_body=message,
            error=str(e)
        )
        
        return {
            'status': 'error',
            'channel': channel,
            'error': str(e)
        }



if __name__ == '__main__':
    print(f"Starting server with Twilio number: {twilio_number}")
    app.run(debug=True, port=5000)