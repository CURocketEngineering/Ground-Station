#ifndef HEADER_H
#define HEADER_H

#include <Arduino.h>
#include <HX&11.h>

void readcommands();
void processCommand(string cmd);

void enterSafeMode();
void enterArmedMode();

void quit_program();
void dump_nitrous();
void fire_cycle();

void readAndSendLoadCell();

#endif


