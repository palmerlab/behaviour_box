#include "SerialComs.h"
#include "Timing.h"

String version = "#behaviourbox160212";

/*
    Author: Naoya Takahashi
        modified by Andrew Micallef
    
    
    Setup connections:
    ------------------
      
    DIGITAL   output            variable       
    --------- ----------------- ---------------
    Current
    pin 2     recording trigger `recTrig`      
    pin 3     stimulus          `stimulusPin`  
    pin 8     speaker           `speakerPin`   
    pin 10    left water valve  `waterValve[0]`
    pin 11    right water valve `waterValve[1]`
    
    TODO
    pin 7     vacuum tube valve `vacValve`     
    pin 13    left  lick report `lickRep[0]`   
    pin 13    right lick report `lickRep[1]`   
    --------- ----------------- ---------------
              
    ANALOG    input                            
    --------- ----------------- ---------------
    A0        left  lick sensor `lickSens[0]`  
    A1        right lick sensor `lickSens[1]`  
    --------- ----------------- ---------------
 */

/*--------------------------------------------------------++
||                  IO port settings:                     ||
++--------------------------------------------------------*/

// digital pin 2 triggers ITC-18
// digital pin 4 control whisker stimulation

const char recTrig = 2;
const char stimulusPin = 3;
const char speakerPin = 8;
const char statusLED = 13;
      
// digital pin 8 control water valve 
// led connected to digital pin 13
// the piezos are connected to analog pins 0 and 1

const char waterPort[] = {10,11};
const char lickRep = 13;
const char lickSens[] = {A0,A1};


// timing parameters
// -----------------

unsigned long t_init;

unsigned int t_noLickPer = 0;
unsigned int trial_delay = 500; // ms
unsigned int t_stimONSET[] = {5000,6000};
unsigned int stimDUR = 500;
unsigned int t_rewardSTART = 4500; // ms
unsigned int t_rewardEND = 10000; // ms
unsigned int t_trialEND = 10000; // ms //maximum of 62 000

char mode = 'h'; //one of 'h'abituation, 'c'onditioning, 'o'perant
char rewardCond = 'R'; // a value that is 'L' 'R', 'B' or 'N' to represent lick port to be used
char minlickCount = 5;

// stimulus parameters
// -------------------
int ON = 20; //keep this constant for consistency sake

int left_OFF[][2] = {{100,  20},
                     { 20, 100}};

int right_OFF[][2] = {{100, 100},
                      { 20,  20}};

bool right_port = 1;
bool left_port = 0;

// audio
// -----

// int toneGoodLeft = 4000; //Hz
// int toneGoodRight = 8000; //Hz
int toneGood = 2000; //Hz
int toneBad = 500; //Hz
int toneDur = 100;


// Reward
// ------

// Global value to keep track of the total water consumed
// this really shouldn't get much higher than 100. 
char waterCount = 0;
char waterVol = 10; //uL per dispense

int lickThres = 450;
bool lickOn[] = {false, false};

bool verbose = true;
bool break_wrongChoice = false; // stop the trial if the animal makes a mistake during reward period
bool do_habituation = true;


                   
/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/
char get_response();

char Habituation();

bool senseLick(bool sensor, bool* PreviousState);

int UpdateGlobals(String input);

void flutter(int OFF);

char ActiveDelay(unsigned int wait, bool break_on_lick = false);
    
int TrialStimulus(int OFF);

void preTrial();

char TrialReward();

int runTrial();


/* -------------------------------------------------------++
||                  END PROTOTYPES                        ||
++--------------------------------------------------------*/

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
    Serial.println(version);
    
    randomSeed(analogRead(5));

    // declare the digital out pins as OUTPUTs
    pinMode(recTrig, OUTPUT);
    pinMode(waterPort[0], OUTPUT);
    pinMode(waterPort[1], OUTPUT);
    pinMode(stimulusPin, OUTPUT);
    pinMode(lickRep[0], OUTPUT);
    pinMode(speakerPin, OUTPUT);
    
    Serial.println("-- Status: Ready --");
}

void loop () {
    
    t_init = millis();
    
    if (Serial.available()){
        
        String input = getSerialInput();
        
        if (input == "GO"){

            runTrial();
                    
            Serial.println("-- Status: Ready --");
        }
        
        else { UpdateGlobals(input);
}

    }
    
    while (!Serial.available()
            and (mode == 'h')){
        
        Habituation();
    }
    
    if (lickOn[0] or lickOn[1]){
        delay(100);
    }
}



//definitions

char get_response(){
    char response = 0;
    
    // Change the values of lickOn and lickOn 
    senseLick(0, &lickOn[0]);
    senseLick(1, &lickOn[1]);

    if (lickOn[0]){
        response = 'L';
    }
    else if (lickOn[1]){
        response = 'R';
    }
    
    // set the response to nothing if there was none
    if (!response){
        response = '-';
    }
    
    return response;
}

bool senseLick(bool sensor, bool* PreviousState) {
    // Update: PreviousState points to the variable that
    //         holds the LickOn state. Dereferencing this
    //         pointer in the function sets the state to
    //         true or false based on the following logic:
    // 1. check to see if the lick sensor has moved
    // 2. check if the sensor is above threshold
    // 3. report if the state of lickOn has change
    
    bool CallSpike; // Who You Gonna Call?
    
    if (analogRead(lickSens[sensor]) >= lickThres){
        
        if (*PreviousState == false) { 
            CallSpike = true;
            // counted = true
        }
        else { 
            CallSpike = false;
        }
        *PreviousState = true;
    }
    else {
        *PreviousSate = false;
        CallSpike = false;
    }
    
    return CallSpike
}

void flutter(int OFF){
  
  digitalWrite(stim_pin, HIGH);
  delay(ON);
  
  digitalWrite(stim_pin, LOW);
  delay(OFF);
}

/*
-----------------
THE TRIAL STATES
----------------
*/

char ActiveDelay(unsigned long wait, 
                    bool break_on_lick) {

    unsigned long t = t_now(t_init);
    
    char response = 0;
    
    if (verbose) {
        Serial.print("#Enter `ActiveDelay`:\t");
        Serial.println(t);
    }
    
    while (t < wait) {
        t = t_now(t_init);
        
        response = get_response();
            
        if (break_on_lick and (response != '-')){
            if (verbose) { 
                Serial.print("#Exit `ActiveDelay`:\t");
                Serial.println(t);
            }
            return response;
        }    
    }
    
    if (verbose) {
        Serial.print("#Exit `ActiveDelay`:\t");
        Serial.println(t);
    }
    
    return response;
}

//0 PRETRIAL

void preTrial() {   
    /* while the trial has not started 
       1. update the time
       2. check for licks
       4. trigger the recording by putting recTrig -> HIGH
    */
    long t = t_now(t_init);
    
    if (verbose) {
        Serial.print("#Enter `preTrial`:\t");

        Serial.println(t);
    }
    
    while (t < 0){
        // 1. update time
        // 2. check for licks
        t = t_now(t_init);
        
        senseLick(0, &lickOn[0]);
        senseLick(1, &lickOn[1]);
        
        //TODO: define statusLED and plug in an LED to hardware: Almost Done
        // LED to flash each second before the trial: Might not be possible, can be done with different coloured number of LEDs
        if (t%1000 < 20){
            digitalWrite(statusLED, HIGH);
        } 
        else {digitalWrite(statusLED, LOW);}
        
        // 3. trigger the recording
        if (t > -10){
            digitalWrite(recTrig, HIGH);
        }
        
        // note, recTrig is switched off immediately after the
        // loop to avoid artefacts in the recording
    }
    
    digitalWrite(recTrig, LOW);
    
    if (verbose) {
        Serial.print("#Exit `preTrial`:\t");
        Serial.println(t);
    }
    
} 

int TrialStimulus(int OFF) {
    
    int t_local = millis();
    int t = t_now(t_local);
    
    if (verbose) {
        // TODO make verbosity a scale instead of Boolean
        Serial.print("#Enter `TrialStimulus`:\t");

        Serial.println(t_now(t_init));
        
        Serial.print("#\tstimDUR:\t");
        Serial.println(stimDUR);
        
        Serial.print("#\tOFF:\t");
        Serial.println(OFF);
    }
   
    while (t < stimDUR){
        /* Run the buzzer while:
           1. update the time
           2. check for licks
        */
        senseLick(0, &lickOn[0]);
        senseLick(1, &lickOn[1]);

        flutter(OFF);

        t = t_now(t_local);

    } 
    digitalWrite(stimulusPin, LOW); //this is a safety catch

    if (verbose) {
        
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
    }
    return 1;
}

char TrialReward() {
    /* 
    returns a character:
            ---- --------------------------------------
             'L' correct hit on left port
             'R' correct hit on right port
             'l' incorrect lick on left port
             'r' incorrect lick on right port
             '-' unknown
             'M' No lick detected during reward period
            ---- --------------------------------------  
    */
                
    int t = t_now(t_init);
    bool RewardTest = 0;
    bool RewardPort = 0;
    char response = 0;
    byte count[] = {0,0};
    
    if (verbose) {
        Serial.print("#Enter `TrialReward`:\t");
        Serial.println(t);
    }
    
    while (t < t_rewardEND) {
        
        t = t_now(t_init);
        
        count[0] = count[0] + senseLick(0, &lickOn[0]);
        count[1] = count[1] + senseLick(1, &lickOn[1]);
        
        // response reports if there was a lick in the reward period
        
        switch (rewardCond){
            
            case 'L':
                RewardTest = (count[0] >= minlickCount) 
                                or (mode == 'c');
                RewardPort = 0;
            break;
                
            case 'R':
                RewardTest = (count[1] >= minlickCount) 
                                or (mode == 'c');
                RewardPort = 1;
            break;
            
            case 'B':
                RewardTest = (count[0] >= minlickCount) 
                                or (count[1] >= minlickCount) 
                                or (mode == 'c');
            break;
            
            case 'N':
                if (verbose) { 
                    Serial.print("count[0]:\t");
                    Serial.println(count[0]);
                    
                    Serial.print("count[1]:\t");
                    Serial.println(count[1]);
                    
                    Serial.print("#Exit `TrialReward`:\t");
                    Serial.println(t);
                }
                return 0;
            break;
            
            default:
                Serial.print("ERROR: rewardCond not specified");
                Serial.println(" requires 'L'eft, 'R'ight, 'B'oth, 'N'either");
                return '!';
            break;
        }
        
        if (RewardTest) {
            
            if (rewardCond == 'B') { 
                digitalWrite(waterPort[0], HIGH);

                digitalWrite(waterPort[1], HIGH);
                if (verbose) {
                    Serial.println("WaterPort[0]:\t1\nWaterPort[1]:\t1");
                }
            }
            else { 
                digitalWrite(waterPort[RewardPort], HIGH);

                    if (verbose) { 
                        Serial.print("WaterPort[");

                        Serial.print(RewardPort);
                        Serial.print("]:\t");
                        Serial.println("1");               
                    }
                }
            
            delay(waterVol);

            digitalWrite(waterPort[0], LOW);
            digitalWrite(waterPort[1], LOW);
           
            if (mode != 'c'){ 
                if (lickOn[0]){ // hit left
                    response = 'L';
                } 
                if (lickOn[1]){ // hit right
                    response = 'R';
                } 
                if (rewardCond == 'B'){
                    if (count[0] > count[1]) {
                        response = 'L';
                    }
                    else if (count[0] < count[1]) { 
                        response = 'R';
                    }
                    else { 
                        response = 'B';
                    }
                }
            }
            
            if (verbose) { 
                Serial.print("count[0]:\t");
                Serial.println(count[0]);
                
                Serial.print("count[1]:\t");
                Serial.println(count[1]);
                
                Serial.print("#Exit `TrialReward`:\t");
                Serial.println(t);
            }
            return response;
        }
        else if ((count[!RewardPort] >= minlickCount) 
                    and (rewardCond != 'B')){
                        
            // declare the fail condition??
            if (!response) {
                if (lickOn[0]) {
                    response = 'l';
                } //bad left 
                if (lickOn[1]) {
                    response = 'r';
                }  //bad right
            }
            if (break_wrongChoice){
                tone(speakerPin, toneBad, 50);
                if (verbose) { 
                    Serial.print("count[0]:\t");
                    Serial.println(count[0]);
                    
                    Serial.print("count[1]:\t");
                    Serial.println(count[1]);
                    
                    Serial.print("#Exit `TrialReward`:\t");
                    Serial.println(t);
                }
                return response;
            }
        }

        digitalWrite(waterPort[0], LOW);
        digitalWrite(waterPort[1], LOW);
       //safety catch
    }

    // miss 
    if (verbose) { 
        Serial.print("count[0]:\t");
        Serial.println(count[0]);
        
        Serial.print("count[1]:\t");
        Serial.println(count[1]);
        
        Serial.print("#Exit `TrialReward`:\t");
        Serial.println(t);
    }
    return response;
}

/* ------------------------------
     THE MAIN MAIN FUNCTION
--------------------------------- */ 

int runTrial() { 
    
    // returns 0 if the stimulus was applied
    // returns 1 if a timeout is required
    // until next trial
    
    // local variables and initialisation of the trial
    /* t_init is initialised such that t_now
       returns 0 at the start of the trial, and 
       increases from there. */ 
    unsigned long t;
    int response_time = 0;
    char response = 0;
    bool rbit = random(0,2);
    int OFF[2] = {-1, -1};
    
    
    // local time
    t_init = millis() + trial_delay;
    t = t_now(t_init);
    
    // select the frequency pair to use
    if (rewardCond == 'L') {
        OFF[0] = left_off[rbit][0];
        OFF[1] = left_off[rbit][1];
    }
    else if (rewardCond == 'R') {
        OFF[0] = right_off[rbit][0];
        OFF[1] = right_off[rbit][1];
    }
    
    /*trial_phase0
    while the trial has not started 
       1. update the time
       2. check for licks
       3. trigger the recording by putting recTrig -> HIGH
    */
    
    preTrial(verbose);
    t = t_now(t_init);
      
    ActiveDelay(t_noLickPer, false);
    t = t_now(t_init);
    
    ActiveDelay(t_stimONSET[0], false);
    t = t_now(t_init);
    
    if (OFF[0] > 0) {
        TrialStimulus(OFF[0]);
    }
    else if (verbose) {
        Serial.println("#skipping stim0");
    }
    
    t = t_now(t_init);
    
    ActiveDelay(t_stimONSET[1], false);
    t = t_now(t_init);
    
    if (OFF[1] > 0){ 
        TrialStimulus(OFF[1]);
    }
    else {
        if (verbose){
            Serial.println("#skipping stim1");
        }
    }
    
    t = t_now(t_init);
    
    
    // TODO include contingency to report on lick early without breaking?
    ActiveDelay(t_rewardSTART, false);
    t = t_now(t_init);
    
    /* this is a little complicated:
       1. check that there is a reward due, ie the condition
          is not `N`
       2. TrialReward returns 0 if break_wrongChoice is set.
          therefore if TrialReward is false, the incorrect
          sensor was tripped during the reward period. A 
          bad tone is played; and the function returns, 
          resetting the program
       3. Otherwise we wait until the trial period has ended
    */
    
    response = TrialReward();

    
    if (response) {
        response_time = t_now(t_init);
    }
    else {
        response = ActiveDelay(t_trialEND, true);
    }
    
    if ((response != '-')    
            and (
                (response == rewardCond) 
                or (rewardCond == 'B')
            )
        ) {
            tone(speakerPin, toneGood, 50);
    }
    else {
        
        if (response == 'L'){
            response = 'l';
            //tone(speakerPin, toneBad, 50);
        }
        else if (response == 'R'){
            response = 'r';
            //tone(speakerPin, toneBad, 50);
        }
    }
    
    ActiveDelay(t_trialEND, false);
    
    Serial.print("response:\t");
    Serial.println(response);
    Serial.print("response_time:\t");
    Serial.println(response_time);
   
    return 0;
}

/* ------------------------------
     END MAIN MAIN FUNCTION
--------------------------------- */ 


char Habituation(){
    
    bool rbit = random(0,2); // a random bit
    bool port = 0;
    int t_interStimdelay = (t_stimONSET[1] + stimuDur) 
                                    - t_stimONSET[0];
    int OFF[2] = {0,0};
    

    char response = get_response();
    
    if (response != '-') {
        
        if (response == 'L') {
            OFF[0] = left_OFF[rbit][0];
            OFF[1] = left_OFF[rbit][1];
            port = left_port;
        }
        
        else if (response == 'R'){
            OFF[0] = right_OFF[rbit][0];
            OFF[1] = right_OFF[rbit][1];
            port = right_port;
        }
        
        digitalWrite(waterPort[port], HIGH);
        delay(waterVol);
        digitalWrite(waterPort[port], LOW);
        
        tone(speakerPin, toneGood, 50);

        TrialStimulus(stimulusPin,
                        stimDUR,
                        30,
                        OFF[0]);
        
        delay(500);
        
        TrialStimulus(stimulusPin,
                        stimDUR,
                        30,
                        OFF[1]);
                    
        if (ActiveDelay(500, true) == response){
            digitalWrite(waterPort[port], HIGH);
            delay(waterVol);
            digitalWrite(waterPort[port], LOW);
        }
        
        ActiveDelay(1000, false);
      }

  return response;    
}

/* ------------------------------
     END OF THE MAP... here be monsters
--------------------------------- */ 


int UpdateGlobals(String input) {
    /*
    This is a big ugly function which compares the
    input string to the names of variables that I have
    stored in memory; This is very much not the `C` 
    way to do things...
    
    I think this could be a hash table. I haven't
    learned enough about hash table implementation
    yet and I know this works, so for the moment:
    *If it ain't broke*...
    */

    // sep is the index of the ':' character
    int sep = getSepIndex(input);

    if (sep) {
        
        String variable_name = input.substring(0,sep);
        String variable_value = input.substring(sep+1);
        
        Serial.print("#");
        Serial.print(variable_name);
        Serial.print("\t");
        Serial.println(variable_value);
        
        // input before seperator?
        
        switch (variable_name) :
        
            case "lickThres" :
                lickThres = variable_value.toInt();
                Serial.print("lickThres:\t");
                Serial.println(lickThres);
                return 1;
            break;
            
            case "mode" :
                mode = variable_value[0];
                Serial.print("mode:\t");
                Serial.println(mode);
                return 1;
            break;
            
            case "rewardCond" :
                rewardCond = variable_value[0];
                Serial.print("rewardCond:\t");
                Serial.println(rewardCond);
                return 1;
            break;
          
            case "break_wrongChoice" :
                break_wrongChoice = variable_value.toInt();
                Serial.print("break_wrongChoice:\t");
                Serial.println(break_wrongChoice);
                return 1;
            break;
            
            case "minlickCount" :
                minlickCount = variable_value.toInt();
                Serial.print("minlickCount:\t");
                Serial.println(minlickCount);
                return 1;
            break;
            
            default
                return 0;
            break;
   }
   return 0;
}
