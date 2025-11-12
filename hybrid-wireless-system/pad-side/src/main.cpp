#include "Arduino.h"
#include "header.h"

using namespace std;


#define FILL_RELAY_PIN 1
#define PURGE_RELAY_PIN 2
#define FIRE_RELAY_PIN 4

#define LOADCELL_DOUT_PIN 5
#define LOADCELL_SCK_PIN

HX&11 read;
// use millis() when possible

// put function declarations here:
enum systemState{
  STATE_SAFE,
  STATE_ARMED
};

systemState currentState = STATE_SAFE;

struct relayStates{
  bool fill;
  bool purge;
  bool fire;
} relays = {false,false,false};

unsigned long lastRead = 0;
const unsigned long READ_INTERVAL = 100;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(115200);

  pinMode(FILL_RELAY_PIN, OUTPUT);
  pinMode(PURGE_RELAY_PIN, OUTPUT);
  pinMode(FIRE_RELAY_PIN, OUTPUT);

  digitalWrite(FILL_RELAY_PIN, LOW);
  digitalWrite(PURGE_RELAY_PIN, LOW);
  digitalWrite(FIRE_RELAY_PIN, LOW);


  read.begin(LOADCELL_DOUT_PIN,LOADCELL_SCK_PIN);
}

void loop() {
  // put your main code here, to run repeatedly:
}

// put function definitions here:
int myFunction(int x, int y) {
  return x + y;
}