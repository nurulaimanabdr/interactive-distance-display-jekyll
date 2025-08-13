#include <WiFi.h>
#include <PubSubClient.h>

// ==== WiFi Config ====
const char* ssid = "Billwong-TIME";
const char* password = "Billwong1234";

// ==== MQTT Config ====
const char* mqtt_server = "192.168.100.191"; // <-- Pi IP here
const int mqtt_port = 1883;
const char* mqtt_topic = "sensor/distance";

WiFiClient espClient;
PubSubClient client(espClient);

// Dummy sensor variable (replace with real sensor later)
int distanceCM = 34;

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to WiFi: ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  int retries = 0;
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
    retries++;
    if (retries > 30) {  // 15 seconds timeout
      Serial.println("\nWiFi connection FAILED!");
      return;
    }
  }

  Serial.println("");
  Serial.println("WiFi connected ✅");
  Serial.print("ESP32 IP Address: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  // Loop until connected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection to ");
    Serial.print(mqtt_server);
    Serial.print(":");
    Serial.println(mqtt_port);

    if (client.connect("ESP32Client")) {
      Serial.println("MQTT connected ✅");
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" -> retry in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  setup_wifi();

  client.setServer(mqtt_server, mqtt_port);
}

void loop() {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("⚠️ WiFi disconnected! Reconnecting...");
    setup_wifi();
  }

  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Simulate distance publishing
  Serial.print("Publishing distance: ");
  Serial.print(distanceCM);
  Serial.println(" cm");

  if (!client.publish(mqtt_topic, String(distanceCM).c_str())) {
    Serial.println("❌ Publish failed! (Check MQTT broker)");
  } else {
    Serial.println("✅ Publish success");
  }

  delay(2000);
}
