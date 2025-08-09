#include <WiFi.h>
#include <PubSubClient.h>

// === CONFIGURE THESE ===
const char* ssid = "YourWiFi";        // <- placeholder
const char* password = "YourPass";    // <- placeholder
const char* mqtt_server = "192.168.1.100"; // MQTT broker IP (Raspberry Pi)
// =======================

WiFiClient espClient;
PubSubClient client(espClient);

#define TRIG_PIN 5
#define ECHO_PIN 18

long durationVal;
int distanceCm;

void setup() {
  Serial.begin(115200);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // connect WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected");

  client.setServer(mqtt_server, 1883);
}

void loop() {
  if (!client.connected()) reconnectMQTT();
  measureDistance();
  char buf[16];
  sprintf(buf, "%d", distanceCm);
  client.publish("sensor/distance", buf);
  delay(500);
}

void measureDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  durationVal = pulseIn(ECHO_PIN, HIGH);
  distanceCm = durationVal * 0.034 / 2;
  // clamp
  if (distanceCm < 0) distanceCm = 0;
  if (distanceCm > 500) distanceCm = 500;
  Serial.print("Distance (cm): ");
  Serial.println(distanceCm);
}

void reconnectMQTT() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 2 seconds");
      delay(2000);
    }
  }
}
