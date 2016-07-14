#include <Arduino.h>

#include "global_variables.h"

#include "timing.h"
#include "sensors.h" 
#include "functions.h"
#include "SerialComms.h"
#include "single_port_setup.h"

String version = "#BB_V3.0.20160629";


void setup (){
    // Open serial communications and wait for port to open:
    // This requires RX and TX channels (pins 0 and 1)
    // wait for serial port to connect. Needed for native USB port only
    Serial.begin(115200);
    while (!Serial) {
        ;
    }
    //Confirm connection and telegraph the code version

    Serial.println("#Arduino online");
    Serial.println  (version);
    
    randomSeed(analogRead(5));

    // declare the digital out pins as OUTPUTs
    pinMode(recTrig, OUTPUT);
    pinMode(bulbTrig, OUTPUT);
    pinMode(waterPort[0], OUTPUT);
    pinMode(waterPort[1], OUTPUT);
    pinMode(stimulusPin, OUTPUT);
    pinMode(speakerPin, OUTPUT);

    Serial.println("-- Status: Ready --");
}

void loop () {

    t_init = millis();

    if (Serial.available()){

        String input = getSerialInput();

        init_trial(trialType);

        if ((mode == 'o') and (input == "GO")){

            runTrial();

            digitalWrite(bulbTrig, LOW);
            digitalWrite(recTrig, LOW);
            Serial.println("-- Status: Ready --");
        }
        else if (mode == 'h'){
            Habituation_single();
        }
        else { 
            UpdateGlobals(input);
        }
    }
}