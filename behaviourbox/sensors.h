#include <Wire.h>          // Communications module for use with MPR121
#include "mpr121.h"        // Register definitions for the capacitive sensor

char get_response();

bool senseLick(bool sensor);

void readTouchInputs();

void set_register(int address, unsigned char r, unsigned char v);

void mpr121_setup(void);

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
    return touchStates[button_touch_pin];
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



void mpr121_setup(void){

  set_register(0x5A, ELE_CFG, 0x00); 
  
  // Section A - Controls filtering when data is > baseline.
  set_register(0x5A, MHD_R, 0x01);
  set_register(0x5A, NHD_R, 0x01);
  set_register(0x5A, NCL_R, 0x00);
  set_register(0x5A, FDL_R, 0x00);

  // Section B - Controls filtering when data is < baseline.
  set_register(0x5A, MHD_F, 0x01);
  set_register(0x5A, NHD_F, 0x01);
  set_register(0x5A, NCL_F, 0xFF);
  set_register(0x5A, FDL_F, 0x02);
  
  // Section C - Sets touch and release thresholds for each electrode
  set_register(0x5A, ELE0_T, TOU_THRESH);
  set_register(0x5A, ELE0_R, REL_THRESH);
 
  set_register(0x5A, ELE1_T, TOU_THRESH);
  set_register(0x5A, ELE1_R, REL_THRESH);
  
  set_register(0x5A, ELE2_T, TOU_THRESH);
  set_register(0x5A, ELE2_R, REL_THRESH);
  
  set_register(0x5A, ELE3_T, TOU_THRESH);
  set_register(0x5A, ELE3_R, REL_THRESH);
  
  set_register(0x5A, ELE4_T, TOU_THRESH);
  set_register(0x5A, ELE4_R, REL_THRESH);
  
  set_register(0x5A, ELE5_T, TOU_THRESH);
  set_register(0x5A, ELE5_R, REL_THRESH);
  
  set_register(0x5A, ELE6_T, TOU_THRESH);
  set_register(0x5A, ELE6_R, REL_THRESH);
  
  set_register(0x5A, ELE7_T, TOU_THRESH);
  set_register(0x5A, ELE7_R, REL_THRESH);
  
  set_register(0x5A, ELE8_T, TOU_THRESH);
  set_register(0x5A, ELE8_R, REL_THRESH);
  
  set_register(0x5A, ELE9_T, TOU_THRESH);
  set_register(0x5A, ELE9_R, REL_THRESH);
  
  set_register(0x5A, ELE10_T, TOU_THRESH);
  set_register(0x5A, ELE10_R, REL_THRESH);
  
  set_register(0x5A, ELE11_T, TOU_THRESH);
  set_register(0x5A, ELE11_R, REL_THRESH);
  
  // Section D
  // Set the Filter Configuration
  // Set ESI2
  set_register(0x5A, FIL_CFG, 0x04);
  
  // Section E
  // Electrode Configuration
  // Set ELE_CFG to 0x00 to return to standby mode
  set_register(0x5A, ELE_CFG, 0x0C);  // Enables all 12 Electrodes
  
  
  // Section F
  // Enable Auto Config and auto Reconfig
  /*set_register(0x5A, ATO_CFG0, 0x0B);
  set_register(0x5A, ATO_CFGU, 0xC9);  // USL = (Vdd-0.7)/vdd*256 = 0xC9 @3.3V   set_register(0x5A, ATO_CFGL, 0x82);  // LSL = 0.65*USL = 0x82 @3.3V
  set_register(0x5A, ATO_CFGT, 0xB5);*/  // Target = 0.9*USL = 0xB5 @3.3V
  
  set_register(0x5A, ELE_CFG, 0x0C);
  
}



void set_register(int address, unsigned char r, unsigned char v){
    Wire.beginTransmission(address);
    Wire.write(r);
    Wire.write(v);
    Wire.endTransmission();
}
