#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "Mohamad's S20 FE";
const char* password = "rfjv6743";

#define SS_PIN 10
#define RST_PIN 9
#define LED_PIN 3
#define BUZZER_PIN 4

String pendingUID = "";

MFRC522 rfid(SS_PIN, RST_PIN);

void sendUID(String uid) {
  HTTPClient http;
  String url = "http://10.160.89.237:5000/scan?uid=" + uid; 
  Serial.println("Sending: " + url);

  http.begin(url);
  int code = http.GET();
  Serial.println("HTTP code: " + String(code));
  http.end();
}

void setup() {
  Serial.begin(115200);

  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(300);
    Serial.print(".");
  }
  Serial.println("\nConnected!");
  Serial.println(WiFi.localIP());

  SPI.begin(6, 2, 7);
  rfid.PCD_Init();
  Serial.println("RFID ready");

  pinMode(LED_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
}

void loop() {

  // Verstuur pending UID
  if (pendingUID != "") {
    sendUID(pendingUID);
    pendingUID = "";
  }

  // RFID lezen
  if (rfid.PICC_IsNewCardPresent() && rfid.PICC_ReadCardSerial()) {

    String uidString = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
      if (rfid.uid.uidByte[i] < 0x10) uidString += "0";
      uidString += String(rfid.uid.uidByte[i], HEX);
    }
    uidString.toUpperCase();

    Serial.println("UID: " + uidString);

    pendingUID = uidString;

    // LED + buzzer
    digitalWrite(LED_PIN, HIGH);
    digitalWrite(BUZZER_PIN, HIGH);
    delay(150);
    digitalWrite(BUZZER_PIN, LOW);
    digitalWrite(LED_PIN, LOW);

    rfid.PICC_HaltA();
    delay(300);
  }
}
