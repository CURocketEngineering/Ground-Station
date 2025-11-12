#ifndef HEADER_H
#define HEADER_H

#include <Arduino.h>
#include <HX711.h>



void readcommands();
void process_command();
void openpurge();
void closepurge();
void quit_program();
void dump_nitrous();
void fire_cycle();
void close_fire_relay();
void open_fire_relay();

void enterSafeMode();
void enterArmedMode();
void emergencyAbort();


#endif


