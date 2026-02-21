
#include <Arduino.h>
#include <SoftwareSerial.h>

SoftwareSerial XBee(10, 11);

const int BUFFER_SIZE = 5;
char buffer[BUFFER_SIZE]; // Buffer to store incoming characters
int bufferIndex = 0;      // Current index in the buffer
int i = 0; 
unsigned long lastSend = 0;

// define fill purge fire pins
const int FILL_PIN = 3;
const int PURGE_PIN = 2;
const int FIRE_PIN = 4;
const int ARM_PIN = 5;

//Functions for checking the commands
void check_purge(char* buf);
void check_fill(char* buf);
void check_fire(char* buf);
void check_ABORT(char* buf);
void check_ARM(char* buf);
void check_SAFE(char* buf);

void setup() {
  Serial.begin(9600);
  //initalizing the pins and the XBee
  pinMode(FILL_PIN, OUTPUT);
  pinMode(PURGE_PIN, OUTPUT);
  pinMode(FIRE_PIN, OUTPUT);
  pinMode(ARM_PIN, OUTPUT);

  XBee.begin(9600);

  Serial.println("Ready, Listening......");
}

void loop() {
  

// digitalWrite(SAFETY_PIN,HIGH);
// digitalWrite(FILL_PIN,HIGH);
// Serial.println("Saftey and FIll on");

// delay(1000);

// digitalWrite(FILL_PIN, LOW);
// delay(1000);
// digitalWrite(SAFETY_PIN,LOW);
// Serial.println("Saftey and FIll off");

// delay(1000);

// digitalWrite(SAFETY_PIN,HIGH);
// digitalWrite(FIRE_PIN,HIGH);
// Serial.println("Saftey and FIRE on");

// delay(1000);

// digitalWrite(FIRE_PIN, LOW);
// delay(1000);
// digitalWrite(SAFETY_PIN,LOW);
// Serial.println("Saftey and FIRE off");

// delay(1000);

// digitalWrite(PURGE_PIN, HIGH);

// Serial.println("PURGE on");
// delay(1000);

// digitalWrite(PURGE_PIN,LOW);
// Serial.println("PURGE off");
// delay(1000);

  
  //Forward data from Serial to XBee
if (Serial.available()) { 
XBee.write(Serial.read());
   }
  

//   // Read data from XBee and process it
   if (XBee.available()) {
     char receivedChar = XBee.read();
     Serial.println("Data received from XBee:");

//     // Echo received data to Serial
     Serial.write(receivedChar);

//     // If the char is a newline, reset the buffer
     if (receivedChar == '\n') {
       bufferIndex = 0;
       return;
     }

//     // Add character to buffer and check for commands
     buffer[bufferIndex++] = receivedChar;

     // If buffer is full, check for commands and reset buffer index
     if (bufferIndex >= BUFFER_SIZE) {
       check_purge(buffer);
       check_fire(buffer);
       check_fill(buffer);
       check_ABORT(buffer);
       check_ARM(buffer);
       check_SAFE(buffer);
       bufferIndex = 0;  // Reset the buffer for the next command
     }
   }
 }

// // Function to check if the buffer contains "purge"
 void check_purge(char* buf) {
   if (strncmp(buf, "PURGE", BUFFER_SIZE) == 0) {
     XBee.println("Purge command detected!");
    
     digitalWrite(FILL_PIN, LOW);
     XBee.println("FILLING OFF");

    digitalWrite(FIRE_PIN, LOW);
     XBee.println("FIREING OFF");

    digitalWrite(ARM_PIN, LOW);
     XBee.println("Safety off");

     digitalWrite(PURGE_PIN, HIGH);
     XBee.println("Purging...");
     // Add any additional action here for the "purge" command
   }
 }

 // Function to check if the buffer contains "fuel"
 void check_fill(char* buf) {
     if (strncmp(buf, "fill_", BUFFER_SIZE - 1) == 0) { // "fill" is 4 chars, no null needed
     XBee.println("Fill command detected!");


     digitalWrite(FILL_PIN, HIGH);
     XBee.println("FILLING...");

    
     // Add any additional action here for the "fuel" command
   }
 }

 void check_fire(char* buf) {
   if (strncmp(buf, "fire_", BUFFER_SIZE - 1) == 0) { // "fire" is 4 chars, no null needed
     XBee.println("Fire command detected!");

     digitalWrite(FIRE_PIN, HIGH);
     XBee.println("FIREING...");
    
    delay(3000);

    digitalWrite(FILL_PIN, LOW);
     XBee.println("FILLING OFF");



//     // Add any additional action here for the "fuel" command
   }
}

void check_ABORT(char* buf){
  if (strncmp(buf, "ABORT", BUFFER_SIZE - 1) == 0) { // "fire" is 4 chars, no null needed
     XBee.println("ABORT command detected!");
   
  digitalWrite(FILL_PIN, LOW);
     XBee.println("FILL OFF");

  digitalWrite(FIRE_PIN, LOW);
     XBee.println("FIREING OFF");
 
  digitalWrite(ARM_PIN, LOW);
     XBee.println("NOT ARMED");
   
   digitalWrite(PURGE_PIN, LOW);
     XBee.println("Purging OFF");


//     // Add any additional action here for the "fuel" command
   }

}

void check_ARM(char* buf){
  if (strncmp(buf, "ARM__", BUFFER_SIZE - 1) == 0) { // "fire" is 4 chars, no null needed
     XBee.println("ARM command detected!");

    digitalWrite(PURGE_PIN, LOW);
     XBee.println("Purge Closing");
    
    digitalWrite(ARM_PIN, HIGH);
     XBee.println("ARMED");

   }

}
void check_SAFE(char* buf){
  if (strncmp(buf, "safe_", BUFFER_SIZE - 1) == 0) { // "fill" is 4 chars, no null needed

    XBee.println("NOT ARMED");

     digitalWrite(FILL_PIN, LOW);
     XBee.println("FILLING OFF");

     digitalWrite(ARM_PIN, LOW);
     XBee.println("NOT ARMED");

    
     // Add any additional action here for the "fuel" command
   }

}