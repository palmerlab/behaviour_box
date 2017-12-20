#include <Arduino.h>

#include "prototypes.h"
#include "hidden_variables.h"
#include "USER_variables.h"

#include "SerialComms.h"
#include "timing.h"
#include "sensors.h"
#include "states.h"
#include "opto_simple.h"

String version = "BB_V:4.0";

void setup (){
    // Open serial communications and wait for port to open:
    // This requires RX and TX channels (pins 0 and 1)
    // wait for serial port to connect. Needed for native USB port only
    Serial.begin(115200);
    while (!Serial) {;}
    //Confirm connection and telegraph the code version
    Serial.println();
    Serial.println(version);

    // declare the digital out pins as OUTPUTs
    pinMode(bulbTrig, OUTPUT);
    pinMode(waterPort, OUTPUT);
    pinMode(buzzerPin, OUTPUT);
    pinMode(stimulusPin, OUTPUT);
    pinMode(speakerPin, OUTPUT);
    pinMode(lightPin, OUTPUT);
    pinMode(lickSens, INPUT);

    Send_params();

}

void loop () {

    if (Serial.available()){

        byte input = Serial.read();
        Serial.write(input);

        if (input < 8) {
          init_trial (input);
          t_init = millis();
          run_opto_trial();
          Send_status();
        }
        // run habituation until told to stop
        else if (input == 'h') {
          while (!Serial.available()){
            t_init = millis();
            run_habituation();
          }
        }
        else if (input == 'M') {
          Recieve_params();
        }
    }
}
