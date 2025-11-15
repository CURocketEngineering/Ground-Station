
#include <Arduino.h>
#include <SoftwareSerial.h>

SoftwareSerial XBee(10, 11);

const int BUFFER_SIZE = 5;
char buffer[BUFFER_SIZE]; // Buffer to store incoming characters
int bufferIndex = 0;      // Current index in the buffer
int i = 0; 

// define fill purge fire pins
const int FILL_PIN = 3;
const int PURGE_PIN = 1;
const int FIRE_PIN = 2;
const int SAFETY_PIN = 4;

//Functions for checking the commands
void check_purge(char* buf);
void check_fill(char* buf);
void check_fire(char* buf);

void setup() {
  Serial.begin(115200);
  //initalizing the pins and the XBee
  pinMode(FILL_PIN, OUTPUT);
  pinMode(PURGE_PIN, OUTPUT);
  pinMode(FIRE_PIN, OUTPUT);
  pinMode(SAFETY_PIN, OUTPUT);

  XBee.begin(115200);

  Serial.println("Ready, Listening......");
}

void loop() {
  i++;
  
  // Forward data from Serial to XBee
  if (Serial.available()) { 
    XBee.write(Serial.read());
  }
  

  // Read data from XBee and process it
  if (XBee.available()) {
    // Serial.println("Data received from XBee:");
    char receivedChar = XBee.read();

    // Echo received data to Serial
    Serial.write(receivedChar);

    // If the char is a newline, reset the buffer
    if (receivedChar == '\n') {
      bufferIndex = 0;
      return;
    }

    // Add character to buffer and check for commands
    buffer[bufferIndex++] = receivedChar;

    // If buffer is full, check for commands and reset buffer index
    if (bufferIndex >= BUFFER_SIZE) {
      check_purge(buffer);
      check_fire(buffer);
      check_fill(buffer);
      bufferIndex = 0;  // Reset the buffer for the next command
    }
  }
}

// Function to check if the buffer contains "purge"
void check_purge(char* buf) {
  if (strncmp(buf, "purge", BUFFER_SIZE) == 0) {
    Serial.println("Purge command detected!");
    
    digitalWrite(SAFETY_PIN, LOW);
    Serial.println("Safety Off");

    digitalWrite(PURGE_PIN, HIGH);
    Serial.println("Purging...");
    // Add any additional action here for the "purge" command
  }
}

// Function to check if the buffer contains "fuel"
void check_fill(char* buf) {
  if (strncmp(buf, "fill_", BUFFER_SIZE - 1) == 0) { // "fill" is 4 chars, no null needed
    Serial.println("Fill command detected!");

    digitalWrite(SAFETY_PIN, HIGH);
    Serial.println("Safety On");

    digitalWrite(FILL_PIN, HIGH);
    Serial.println("FILLING...");

    
    // Add any additional action here for the "fuel" command
  }
}

void check_fire(char* buf) {
  if (strncmp(buf, "fire_", BUFFER_SIZE - 1) == 0) { // "fire" is 4 chars, no null needed
    Serial.println("Fire command detected!");

  digitalWrite(SAFETY_PIN, HIGH);
    Serial.println("Safety On");

    digitalWrite(FIRE_PIN, HIGH);
    Serial.println("FIREING...");
    // Add any additional action here for the "fuel" command
  }
}