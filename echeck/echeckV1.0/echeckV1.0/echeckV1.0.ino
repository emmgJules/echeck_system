#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

// Define the pins for SPI communication.
#define PN532_SCK   2
#define PN532_MOSI  3
#define PN532_SS    4
#define PN532_MISO  5
#define PN532_RESET 3 // Reset pin connected to Arduino D3

Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

bool readCard = false;
String data = "";
int greenLED = 12;
int blueLED = 11;  // Blue LED pin
int redLED = 10;   // Red LED pin
int buzzer = 8;    // Buzzer pin

void setup(void) {
  Serial.begin(115200);

  pinMode(redLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  pinMode(blueLED, OUTPUT); // Blue LED pin
  pinMode(buzzer, OUTPUT);  // Buzzer pin

  // Initial state: blue LED on to indicate device is on
  digitalWrite(blueLED, HIGH);
  digitalWrite(redLED, LOW);
  digitalWrite(greenLED, LOW);

  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("Didn't find PN53x board");
    while (1); // halt
  }

  nfc.SAMConfig();
}

void loop(void) {
  while (!readCard) {
    checkCard();
  }

  // Handle serial commands
  while (Serial.available() > 0) {
    data = Serial.readString();
    Serial.println(data);
    if (data == "#") {
      readCard = false;
      digitalWrite(blueLED, LOW);
      delay(500);
      digitalWrite(blueLED, HIGH);
      digitalWrite(greenLED, LOW);
      buzzDifferent();
    } else if (data == "1") {
      digitalWrite(redLED, LOW);
      digitalWrite(greenLED, HIGH);
      buzzOnce();
    } else if (data == "2") {
      digitalWrite(redLED, HIGH);
      digitalWrite(greenLED, LOW);
      buzzDifferent();
    }
    data = "";
  }
}

void checkCard(void) {
  uint8_t success;
  uint8_t uid[] = {0, 0, 0, 0, 0, 0, 0};
  uint8_t uidLength;

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success && !readCard) {
    String uidi = "";
    for (uint8_t i = 0; i < uidLength; i++) {
      uidi += String(uid[i], HEX);
    }
    Serial.println(uidi);
    readCard = true;
  }
}

void buzzOnce() {
  digitalWrite(buzzer, HIGH);
  delay(500);
  digitalWrite(buzzer, LOW);
  
}

void buzzDifferent() {
  digitalWrite(buzzer, HIGH);
  delay(200);
  digitalWrite(buzzer, LOW);
  delay(200);
  digitalWrite(buzzer, HIGH);
  delay(200);
  digitalWrite(buzzer, LOW);
  delay(200);
  digitalWrite(buzzer, HIGH);
  delay(200);
  digitalWrite(buzzer, LOW);
  
}
