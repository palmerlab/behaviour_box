#include "global_variables.h"

#include "timing.h"
#include "sensors.h" 
#include "functions.h"
#include "SerialComms.h"

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
    
    // MPR121 communications
    pinMode(irqpin, INPUT);
    digitalWrite(irqpin, HIGH); //enable pullup resistor

    Wire.begin();
    mpr121_setup();

    randomSeed(analogRead(5));

    // declare the digital out pins as OUTPUTs
    pinMode(recTrig, OUTPUT);
    pinMode(waterPort[0], OUTPUT);
    pinMode(waterPort[1], OUTPUT);
    pinMode(stimulusPin, OUTPUT);
    pinMode(lickRep, OUTPUT);
    pinMode(speakerPin, OUTPUT);

    Serial.println("-- Status: Ready --");
}

void loop () {

    t_init = millis();

    if (Serial.available()){

        String input = getSerialInput();

        init_stim(trialType);

        if (input == "GO"){
            runTrial();

            digitalWrite(recTrig, LOW);
            Serial.println("-- Status: Ready --");
        }
        else { 
            UpdateGlobals(input);
        }
    }

    while (!Serial.available() and (mode == 'h')){
        Habituation();
    }

    while (!Serial.available() and (mode == 's')){
        Serial.print(senseLick(0));
        Serial.print(" ... ");
        Serial.println(senseLick(1));
        delay(100);

    }
}
