#include <Arduino.h>

// define fill purge fire pins
const int FILL_PIN = 2;
const int PURGE_PIN = 3;
const int FIRE_PIN = 4;


void setup() {
  pinMode(FILL_PIN, OUTPUT);
  pinMode(PURGE_PIN, OUTPUT);
  pinMode(FIRE_PIN, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  digitalWrite(FILL_PIN, HIGH);
  // write to serial
  Serial.println("Filling...");
  delay(1000); // wait for a second
  digitalWrite(FILL_PIN, LOW);
  delay(1000); 
  digitalWrite(PURGE_PIN, HIGH);
  Serial.println("Purging...");
  delay(1000);
  digitalWrite(PURGE_PIN, LOW);
  delay(1000);
  digitalWrite(FIRE_PIN, HIGH);
  delay(1000);
  digitalWrite(FIRE_PIN, LOW);
  delay(1000);
}
