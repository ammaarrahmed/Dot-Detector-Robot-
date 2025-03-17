#include <WiFi.h>
#include <ESP32Servo.h>
#include <WebServer.h>

// WiFi credentials
const char* ssid = "PTCL-BB21";
const char* password = "1234567890123";

// Servo pins and objects
const int baseServoPin = 15;  // GPIO pin for base servo
const int jointServoPin = 13; // GPIO pin for joint servo

Servo baseServo;
Servo jointServo;

// Default angles
int baseAngle = 90;
int jointAngle = 90;

// Web server instance
WebServer server(80);

// HTML page for user interface
const char* htmlPage = R"rawliteral(
<!DOCTYPE html>
<html>
  <head>
    <title>2 DOF Robot Control</title>
    <style>
      body { font-family: Arial, sans-serif; text-align: center; }
      input { width: 60px; margin: 10px; text-align: center; }
      button { padding: 10px 20px; margin: 10px; }
    </style>
  </head>
  <body>
    <h2>Control 2 DOF Robot</h2>
    <div>
      <h3>Base Joint</h3>
      <input id="baseAngle" type="number" value="90" min="0" max="180" />
      <button onclick="sendAngle('base')">Set Base</button>
    </div>
    <div>
      <h3>Second Joint</h3>
      <input id="jointAngle" type="number" value="90" min="0" max="180" />
      <button onclick="sendAngle('joint')">Set Joint</button>
    </div>
    <script>
      function sendAngle(joint) {
        const angle = document.getElementById(joint + 'Angle').value;
        fetch(`/set?joint=${joint}&angle=${angle}`)
          .then(response => response.text())
          .then(data => alert(data))
          .catch(error => console.error('Error:', error));
      }
    </script>
  </body>
</html>
)rawliteral";

// Function to handle root page
void handleRoot() {
  server.send(200, "text/html", htmlPage);
}

// Function to handle angle updates
void handleSetAngle() {
  // Debugging: print the full request URL
  Serial.print("Request URL: ");
  Serial.println(server.uri());

  if (server.hasArg("base") && server.hasArg("joint")) {
    int base = server.arg("base").toInt();
    int joint = server.arg("joint").toInt();

    // Print received arguments for debugging
    Serial.print("Received request: base = ");
    Serial.print(base);
    Serial.print(", joint = ");
    Serial.println(joint);

    // Validate angles
    if (base < 0 || base > 180 || joint < 0 || joint > 180) {
      server.send(400, "text/plain", "Invalid angle. Must be between 0 and 180.");
      return;
    }

    // Set servo angles based on the received parameters
    baseAngle = base;
    jointAngle = joint;
    
    baseServo.write(baseAngle);
    jointServo.write(jointAngle);

    server.send(200, "text/plain", "Base and joint angles set to " + String(baseAngle) + " and " + String(jointAngle));
    Serial.print("Base angle set to: ");
    Serial.println(baseAngle);
    Serial.print("Joint angle set to: ");
    Serial.println(jointAngle);
  } else {
    server.send(400, "text/plain", "Missing 'base' or 'joint' parameters.");
    Serial.println("Error: Missing 'base' or 'joint' parameters.");
  }
}



void setup() {
  Serial.begin(115200);

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected.");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Attach servos
  baseServo.attach(baseServoPin);
  jointServo.attach(jointServoPin);

  // Set initial servo positions
  baseServo.write(baseAngle);
  jointServo.write(jointAngle);

  // Configure web server routes
  server.on("/", handleRoot);
  server.on("/set", handleSetAngle);

  // Start the server
  server.begin();
  Serial.println("Web server started.");
}

void loop() {
  server.handleClient();
}
