#include <Arduino.h>

#include "global_variables.h"
#include "prototypes.h"

#include "timing.h"
#include "sensors.h"
#include "states.h"
#include "SerialComms.h"
#include "single_port_setup.h"

String version = "#BB_V4.0";


void setup (){
    // Open serial communications and wait for port to open:
    // This requires RX and TX channels (pins 0 and 1)
    // wait for serial port to connect. Needed for native USB port only
    Serial.begin(115200);
    while (!Serial) {;}
    //Confirm connection and telegraph the code version
    Serial.println(version);

    // declare the digital out pins as OUTPUTs
    pinMode(recTrig, OUTPUT);
    pinMode(bulbTrig, OUTPUT);
    pinMode(waterPort, OUTPUT);
    pinMode(buzzerPin, OUTPUT);
    pinMode(stimulusPin, OUTPUT);
    pinMode(speakerPin, OUTPUT);
}

void loop () {

    t_init = millis();

    if (Serial.available()){

        byte input = Serial.read();
        if (input < 8) {
          Serial.write(input);
        }

        //String input = getSerialInput();

        if ((mode == 'o') and (input == "GO")){

            runTrial();

            digitalWrite(bulbTrig, LOW);
            digitalWrite(recTrig, LOW);
            Serial.println("- Status: Ready");
        }
        else {
            UpdateGlobals(String(input));
        }
    }
    else if (mode == 'h'){
            Habituation();
    }
}
