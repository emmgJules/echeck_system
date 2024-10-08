/*
Serial Commands
.................................

1 = red
2 = green
3 = yellow
# = read again

*/




#include <Wire.h>
#include <SPI.h>
#include <Adafruit_PN532.h>

// If using the breakout with SPI, define the pins for SPI communication.
#define PN532_SCK  (2)
#define PN532_MOSI (3)
#define PN532_SS   (4)
#define PN532_MISO (5)

#define PN532_IRQ   (2)
#define PN532_RESET (3)  // Not connected by default on the NFC Shield

Adafruit_PN532 nfc(PN532_SCK, PN532_MISO, PN532_MOSI, PN532_SS);

int read = LOW;
String data = "";
int green = 12;
int yellow = 11;
int red = 10;


void setup(void) {
  Serial.begin(115200);

  pinMode(red,OUTPUT);
  pinMode(green,OUTPUT);
  pinMode(yellow,OUTPUT);

  nfc.begin();
  uint32_t versiondata = nfc.getFirmwareVersion();
  if (!versiondata) {
    Serial.println("Didn't find PN53x board");
    while (1); // halt
  }
  // Serial.print("Found chip PN5"); Serial.println((versiondata >> 24) & 0xFF, HEX);
  // Serial.print("Firmware ver. "); Serial.print((versiondata >> 16) & 0xFF, DEC);
  // Serial.print('.'); Serial.println((versiondata >> 8) & 0xFF, DEC);
  // Serial.println("Waiting for an ISO14443A Card ...");
  
}

void loop(void) {
  while(!read){
    checkCard();
  }
  while(Serial.available() > 0){
    data += Serial.readString();
    Serial.println(data);
    if(data=="#"){
      read = LOW;
      digitalWrite(red,LOW);
      digitalWrite(green,LOW);
      digitalWrite(yellow,LOW);
    }else if(data=="1"){
      digitalWrite(red,HIGH);
      digitalWrite(green,LOW);
      digitalWrite(yellow,LOW);
    }else if(data=="2"){
      digitalWrite(red,LOW);
      digitalWrite(green,HIGH);
      digitalWrite(yellow,LOW);
    }else if(data=="3"){
      digitalWrite(red,LOW);
      digitalWrite(green,LOW);
      digitalWrite(yellow,HIGH);
    }
    data = "";
  }
  
}

void checkCard(void){
  uint8_t success;
  uint8_t uid[] = { 0, 0, 0, 0, 0, 0, 0 };  
  uint8_t uidLength;                       

  success = nfc.readPassiveTargetID(PN532_MIFARE_ISO14443A, uid, &uidLength);

  if (success&&!read) {
    String uidi = "";
    for (uint8_t i = 0; i < uidLength; i++) {
      uidi += String(uid[i], HEX);
    }
    Serial.println(uidi);
    read = HIGH; 
    }
}
