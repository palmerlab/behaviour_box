#include <Wire.h>          // Communications module for use with MPR121
#include "mpr121.h"        // Register definitions for the capacitive sensor

char get_response();

bool senseLick(bool sensor);

void readTouchInputs(){};

char get_response(){

    char response = 0;

    readTouchInputs();

    if (touchOn[lick_port_L] 
        and touchOn[lick_port_R]) {
        response = 'B'; // could happen?
    }
    else if (touchOn[lick_port_L]){
        response = 'L';
    }
    else if (touchOn[lick_port_R]){
        response = 'R';
    }
    else {
        // set the response to nothing if there was none
        response = '-';
    }
    return response;
}


bool checkforepaw() {
    readTouchInputs();
    return touchState[button_touch_pin];
}

bool senseLick(bool sensor) {
    // 1. check to see if the lick sensor has moved
    // 2. check if the sensor is above threshold
    // 3. report if the state of lickOn has change

    bool CallSpike = false; // Who You Gonna Call?

    if (lickOn[sensor] == false) { 
        CallSpike = true;
        // counted = true
    }

    if (analogRead(lickSens[sensor]) >= lickThres){
        lickOn[sensor] = true;
    }
    else {
        lickOn[sensor] = false;
    }

    // if the sensor was off, and now it is on, return 1
    return (CallSpike and lickOn[sensor]);
}

void readTouchInputs(){

    /* code from:
         https://github.com/sparkfun/MPR121_Capacitive_Touch_Breakout/
                  tree/master/Firmware/MPR121Q/Arduino Sketch/mpr121.ino
       
       For safety I have cloned that repository into 
       Behaviour_box/libraries
    */
    /*
        1. Check the irq interupt from the MPR121
        2. Send a read request
            2.1. Read the Least significant bits
            2.2. Read the Most significant bits
            2.3. The touched status
        3. Scroll through the electrodes and 
           evaluate if the status of the electrode has
           changed. `touchStates` records if an electrode
           is currently active, `touchOn` records if an
           electrode has just been turned ON on this cycle.
    */

    /*  Electrode Byte Table
        ====================
        
        electrode0-7
        ------ ---- ---- ---- ---- ---- ---- ---- ----
        bit    D7   D6   D5   D4   D3   D2   D1   D0
        read   ELE7 ELE6 ELE5 ELE4 ELE3 ELE2 ELE1 ELE0
        write  --   --   --   --  --  --  --  --
        ------ ---- ---- ---- ---- ---- ---- ---- ----
        
        electrode8-11, eleprox
        ------ ---- ---- ---- ---- ----- ----- ---- ----
        bit    D7   D6   D5   D4   D3    D2    D1   D0
        read   OVCF --   --   ELPR ELE11 ELE10 ELE9 ELE8
        write  --   --   --   --   --    --    --   --
        ------ ---- ---- ---- ---- ----- ----- ---- ----
    */

    if(!digitalRead(irqpin)){ // MPR121 sends an interupt signal to the irqpin

        //read the touch state from the MPR121
        Wire.requestFrom(0x5A,2); 

        byte LSB = Wire.read();
        byte MSB = Wire.read();

        //16bits that make up the touch states
        uint16_t touched = ((MSB << 8) | LSB);

        for (int i=0; i < 12; i++){  // Check what electrodes were pressed
            if(touched & (1<<i)){
                if(touchStates[i] == false){
                    //pin i was just touched
                    touchOn[i] = true;
                }else if(touchStates[i] == true){
                    //pin i is still being touched
                    touchOn[i] = false;
                }
                touchStates[i] = true;
            }else{
                //pin i is no longer being touched
                touchStates[i] = false;
            }
        }
    }
}