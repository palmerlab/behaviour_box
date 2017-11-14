#include <Arduino.h>

#include "prototypes.h"
#include "global_variables.h"

#include "SerialComms.h"
#include "timing.h"
#include "sensors.h"
#include "states.h"
#include "opto_simple.h"

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
    pinMode(lightPin, OUTPUT);

    Send_params();

}

void loop () {

    if (Serial.available()){

        byte input = Serial.read();

        //if (input < 8) {

          Serial.write(int(input));
          delay(100);

          run_opto_trial(input);
          Serial.write(long(0));


          //Send_status();
        //}
    }
}
