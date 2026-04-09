#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>

const char* ssid = "iotroam";
const char* password = "Deltion123";

#define SS_PIN 10
#define RST_PIN 9
#define LED_PIN 3
#define BUZZER_PIN 4

MFRC522 rfid(SS_PIN, RST_PIN);

void sendUID(String uid) {
  HTTPClient http;
  String url = "" + uid;
  http.begin(url);
  int code = http.GET();
  http.end();
}

void setup() {
  Serial.begin(115200);

  SPI.begin(6, 2, 7); // SCK, MISO, MOSI

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);

  rfid.PCD_Init();
  Serial.println("RFID ready");

  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(BUZZER_PIN, LOW);
}

void loop() {
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  // LED aan
  digitalWrite(LED_PIN, HIGH);

  // Buzzer
  digitalWrite(BUZZER_PIN, HIGH);
  delay(150);
  digitalWrite(BUZZER_PIN, LOW);

  Serial.print("UID: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i], HEX);
    uidString += String(rfid.uid.uidByte[i], HEX);
  }
  Serial.println();

  sendUID(uidString)

  delay(500);

  // LED uit
  digitalWrite(LED_PIN, LOW);

  rfid.PICC_HaltA();
}