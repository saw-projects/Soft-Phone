$(function () {
  let device;
  let token;

  // Tab Switching
  $('.tab-button').on('click', function() {
    const tabId = $(this).data('tab');
    $('.tab-button').removeClass('active');
    $('.tab-panel').removeClass('active');
    $(this).addClass('active');
    $(`#${tabId}`).addClass('active');
  });

  // Log a message to the event log
  function log(message) {
    const logDiv = $("#log");
    const timestamp = new Date().toLocaleTimeString();
    logDiv.removeClass("hide");
    logDiv.append(`<div class="log-entry">[${timestamp}] ${message}</div>`);
    logDiv.scrollTop(logDiv[0].scrollHeight);
  }

  // Add a message to the message history
  function addMessageToHistory(message, direction) {
    const messageDiv = $("#message-history");
    const messageClass = direction === 'incoming' ? 'incoming' : 'outgoing';
    const timestamp = new Date().toLocaleString();
    messageDiv.append(`
      <div class="message ${messageClass}">
        <div class="message-time">${timestamp}</div>
        <div class="message-content">${message}</div>
      </div>
    `);
    messageDiv.scrollTop(messageDiv[0].scrollHeight);
  }

  // Initialize Twilio Device
  $("#startup-button").on("click", function () {
    $(this).attr("disabled", "disabled");
    log("Requesting access token...");
    
    $.getJSON("/token")
      .then(function (data) {
        log("Got a token.");
        token = data.token;
        
        // Initialize the device
        device = new Twilio.Device(token, {
          logLevel: 1,
          codecPreferences: ["opus", "pcmu"],
        });

        setupDeviceEventHandlers();
        setupDeviceControls();
        
        $("#connection-status").removeClass("hide");
        $("#outgoing-call-controls").removeClass("hide");
        $("#device-settings").removeClass("hide");
        setClientNameUI(data.identity);
      })
      .catch(function (err) {
        console.error("Could not get a token from server!", err);
        log("Error: Could not get a token from server!");
        $("#startup-button").removeAttr("disabled");
      });
  });

  // Set up the Device's controls
  function setupDeviceControls() {
    // Handle outgoing call form submission
    $("#call-form").on("submit", function (e) {
      e.preventDefault();
      const params = {
        To: $("#phone-number").val()
      };
      
      if (device) {
        log("Attempting to call " + params.To + "...");
        const call = device.connect({ params });

        call.on("accept", function() {
          log("Call in progress...");
          $("#button-call").addClass("hide");
          $("#button-hangup-outgoing").removeClass("hide");
          
          $("#button-hangup-outgoing").off("click").on("click", function() {
            log("Hanging up...");
            call.disconnect();
          });
        });

        call.on("disconnect", function() {
          log("Call ended.");
          $("#button-hangup-outgoing").addClass("hide");
          $("#button-call").removeClass("hide");
        });
      } else {
        log("Unable to make call. Device not initialized.");
      }
    });

    // Handle audio device selection
    $("#get-devices").on("click", async function() {
      try {
        await navigator.mediaDevices.getUserMedia({ audio: true })
          .then(function(stream) {
            // Stop the tracks immediately after getting permission
            stream.getTracks().forEach(track => track.stop());
            return navigator.mediaDevices.enumerateDevices();
          })
          .then(function(devices) {
            const audioDevices = devices.filter(device => 
              device.kind === "audiooutput" || device.kind === "audioinput"
            );
            
            // Clear existing options
            $("#speaker-devices, #microphone-devices").empty();
            
            audioDevices.forEach(function(device) {
              const option = $("<option>", {
                value: device.deviceId,
                text: device.label || `${device.kind} (${device.deviceId})`
              });
              
              if (device.kind === "audiooutput") {
                $("#speaker-devices").append(option);
              } else if (device.kind === "audioinput") {
                $("#microphone-devices").append(option);
              }
            });
            
            log("Audio devices refreshed.");
          });
      } catch (err) {
        console.error("Error getting audio devices:", err);
        log("Error getting audio devices.");
      }
    });
  }

  // Set up the Device's event handlers
  function setupDeviceEventHandlers() {
    device.on("registered", function () {
      log("Twilio.Device Ready to make and receive calls!");
    });

    device.on("error", function (error) {
      log("Twilio.Device Error: " + error.message);
    });

    device.on("incoming", function (connection) {
      log("Incoming connection from " + connection.parameters.From);
      $("#incoming-call-controls").removeClass("hide");
      $("#incoming-number").text(connection.parameters.From);

      // Handle incoming call buttons
      $("#button-accept-incoming").off("click").on("click", function() {
        connection.accept();

        connection.on("accept", function() {
          $("#incoming-call-controls .button-group").addClass("hide");
          $("#button-hangup-incoming").removeClass("hide");
          log("Call in progress...");
          
          $("#button-hangup-incoming").off("click").on("click", function() {
            log("Hanging up...");
            connection.disconnect();
          });
        });

        connection.on("disconnect", function() {
          $("#incoming-call-controls").addClass("hide");
          $("#button-hangup-incoming").addClass("hide");
          $("#incoming-call-controls .button-group").removeClass("hide");
          log("Call ended.");
        });
      });
      
      $("#button-reject-incoming").off("click").on("click", function() {
        connection.reject();
        $("#incoming-call-controls").addClass("hide");
        log("Call rejected.");
      });
    });
  }

  // Set up server-sent events for real-time updates
  const eventSource = new EventSource('/events');
  
  eventSource.onmessage = function(event) {
    const eventData = JSON.parse(event.data);
    
    // Handle incoming messages
    if (eventData.event_type === 'message' && eventData.direction === 'incoming') {
      // Add to message history
      addMessageToHistory(eventData.message_body, 'incoming');
      
      // Add to event log
      log(`Incoming ${eventData.channel.toUpperCase()}: From ${eventData.from_number}: ${eventData.message_body}`);
    }
  };

  eventSource.onerror = function(error) {
    console.error("EventSource failed:", error);
    log("Lost connection to server. Messages may be delayed.");
  };

  // Handle sending messages
  $("#sms-form").on("submit", function (e) {
    e.preventDefault();
    const messageData = {
      to: $("#sms-number").val().trim(),
      message: $("#sms-message").val().trim(),
      type: $('input[name="message-type"]:checked').val()
    };

    if (!messageData.to || !messageData.message) {
      log("Please fill in all message fields.");
      return;
    }

    $.ajax({
      url: '/send-message',
      method: 'POST',
      contentType: 'application/json',
      data: JSON.stringify(messageData),
      success: function(response) {
        log(`Message sent successfully! SID: ${response.message_sid}`);
        addMessageToHistory(messageData.message, 'outgoing');
        $("#sms-message").val(''); // Clear message input
      },
      error: function(xhr, status, error) {
        log(`Error sending message: ${error}`);
        console.error('Error:', xhr.responseJSON);
      }
    });
  });

  // Helper functions
  function setClientNameUI(clientName) {
    $("#client-name").html(`Connected as: <strong>${clientName}</strong>`);
  }
});
