String version = "#behaviourbox151119";

//TODO: make a conditioning protocol
//TODO: rename singlestim operant
//TODO: find an obvious method for producing constant noise

/*
    Author: Naoya Takahashi
        modified by Andrew Micallef
      
    This program delivers sensory stimulation and opens water 
    valve when the animal touches the licking sensor within a 
    certain time window.

    Setup connections:
    ------------------
      
    ---------   -----------------  ------------  
    DIGITAL     output             variable
    ---------   -----------------  ------------
    pin 2       recording trigger  `recTrig`  
    pin 4       stimulus TTL       `whiskStim`
    pin 6       speaker for cues   `tonePin`

    pin 8       syringe pump TTL   `waterValve`
    pin 9       vacuum tube valve  `vacValve`

    pin 13      lick report        `licking`

    ---------   -----------------  ------------
    ANALOG IN   input
    ---------   -----------------  ------------
    A0          piezo lick sensor  lickSens
    ---------   -----------------  ------------
    Table: connections to lick controller

      
    Start program:
    --------------

    Trial intervals will randomized between 'minITI' and 'maxITI'. 
    During a trial, the animal has to wait a stimulation without 
    licking (no-lick period, 'nolickPer').

    If it licks during no-lick period, the time of stimulation 
    will be postponed by giving a time out (randomized between 
    'minTimeOut' and 'maxTimeOut').

    When a stimulation is delivered (stimulus duration: 'stimDur'), 
    the animal need to respond (touch the sensor) within a certain 
    time window ('crPer') to get a water reward.

    Delayed licking after the time window will not be rewarded. 
    Opening duration of the water valve is defined by 'valveDur'.

    A TTL trigger for recording will be delivered 
    'baseLineTime' (1 s in default setting) before the stimulus.



//lines preceded by `#` are for debug purposes
 */


// IO port settings:
const int recTrig = 2;    // digital pin 2 triggers ITC-18
const int stimulusPin = 4;    // digital pin 4 control whisker stimulation
const int tonePin = 6;
const int vacValve = 7;     // digital pin 9 controls vacuum
const int statusLED = 2;

const int waterPort[] = {8,9};    // digital pin 8 control water valve 
const int lickRep[] = {12,13};      // led connected to digital pin 13
const int lickSens[] = {A0,A1}; // the piezo is connected to analog pin 0


int lickThres = 450;

// timing parameters
unsigned long t_init;

int trial_delay = 500;
int t_noLickPer = 0;   // ms

int t_stimONSET_0 = 5000;
int t_stimONSET_1 = 6000;
int stimDUR = 500;

int t_rewardSTART = 4500; // ms
int t_rewardEND = 10000;   // ms
int t_trialEND = 10000;   // ms


char mode = 'c';
char rewardCond = 'B'; // a value that is 'L' 'R', 'B' or 'N' to represent lick port to be used

// stimulus parameters
unsigned long ON = 1000;
unsigned long OFF[] = {5000, 5000};

// audio
int toneBad = 500; //Hz
int toneDur = 100; 

// Global value to keep track of the total water consumed
int waterCount = 0; 
int waterVol = 10; //uL per dispense

// Global lick on
bool lickOn[] = {false, false};
bool stimTrial = true; //sets if there is a stimulus this run
bool verbose = true;


void setup (){
    // Open serial communications and wait for port to open:
    Serial.begin(9600);
    // This requires RX and TX channels (pins 0 and 1)
    while (!Serial) {
        ; // wait for serial port to connect. Needed for native USB port only
    }
    //Confirm connection and telegraph the code version
    Serial.println("#Arduino online");
    Serial.println("#behaviourbox");
    Serial.println(version);
    
    // convert lickthreshold to V
    Serial.print("#Lick Threshold:\t"); Serial.print((float(lickThres)/1024)*5); Serial.println(" V");
    
    randomSeed(analogRead(5));

    pinMode(recTrig, OUTPUT); // declare the recTrig as as OUTPUT
    pinMode(waterPort[0], OUTPUT); // declare the waterValve as as OUTPUT
    pinMode(vacValve, OUTPUT); // declare the vacValve as as OUTPUT
    pinMode(stimulusPin, OUTPUT); // declare the whiskStim as as OUTPUT
    pinMode(lickRep[0], OUTPUT); // declare the licking as as OUTPUT
    pinMode(tonePin, OUTPUT);
}


void loop () {
    
    if (Serial.available()){
        String input = getSerialInput();
        Serial.println(input);
    }
    
    Serial.println("modeString\tistimeout\tstimTrial\tresponse\tlickCount");
                       
    runTrial (mode, trial_delay, t_noLickPer, t_stimONSET_0,
            t_stimONSET_1, stimDUR, t_rewardSTART, t_rewardEND, 
            t_trialEND, stimTrial, rewardCond, waterVol, verbose);
    
    if (senseLick(0) or senseLick(1)){
        tone(tonePin, toneBad, 10);
        delay(100);
    }
}

int t_now(unsigned long t_init){
    // is less than 0 before the trial starts
    // is greater than 0 after the start of trial
    return (int) millis() - t_init;
}

bool senseLick(bool sensor){
    // check to see if the lick sensor has moved
    // set lickDetected
    boolean lickDetected = false;
    int sensVal = analogRead(lickSens[sensor]);

    if (sensVal <= lickThres){
        digitalWrite(lickRep[sensor], HIGH);
        lickDetected = true;
    } 
    else {
        digitalWrite(lickRep[sensor], LOW);
        lickDetected = false;
    }

    digitalWrite(tonePin, !random(0, random(50)));
    return lickDetected;
}

String getSerialInput(){

    String readString;
    
    while (Serial.available()) { 
        delay(3);  //delay to allow buffer to fill
        char c = Serial.read();  //gets one byte from serial buffer
        readString += c; //makes the string readString
    }
    
    return readString;
}

int getChar(String input){
    //return the value of the string after the seperator
    int val = input[getSepIndex(input)+1];
    return val;
}

int getInt(String input){
    //return the value of the string after the seperator
    int val = input.substring(getSepIndex(input)).toInt();
    return val;
}

int getSepIndex(String input) {
    char c = 1;
    int i = 0;
   
    while (c != 0) {
        c = input[i];
        
        if (c == ':'){
            return i;
        }
        i ++;
    }
    return 0;
}

void flutter(int stim_pin, unsigned long on, unsigned long off){
  
  digitalWrite(stim_pin, HIGH);
  digitalWrite(statusLED, LOW);
  
  delayMicroseconds(on);
    
  digitalWrite(stim_pin, LOW);
  digitalWrite(statusLED, LOW);
  
  delayMicroseconds(off);
}


/*
-----------------
THE TRIAL STATES
----------------
*/

int ActiveDelay(int wait, 
    bool break_on_lick = false, 
    bool verbose = true) {
    
    unsigned long t_init = millis();
    int t = t_now(t_init);
    
    bool response = false;
    
    if (verbose) {Serial.print("#Exit `ActiveDelay`:\t"); Serial.println(t);}
    
    while (t < wait) {
        t = t_now(t_init);
        lickOn[0] = senseLick(0);
        lickOn[1] = senseLick(1);
        
        if (lickOn[0] or lickOn[1]){
            response = true;
            
            Serial.print("#response `ActiveDelay`:\t"); Serial.println(t);
            Serial.print("#port[0]:\t"); Serial.println(lickOn[0]);
            Serial.print("#port[1]:\t"); Serial.println(lickOn[1]);
            if (break_on_lick){
                if (verbose) {
                    Serial.print("#Exit `ActiveDelay`:\t"); Serial.println(t);
                    Serial.print("#port[0]:\t"); Serial.println(lickOn[0]);
                    Serial.print("#port[1]:\t"); Serial.println(lickOn[1]);
                }
                return response;
            }
        }
    }
    
    if (verbose) {Serial.print("#Exit `ActiveDelay`:\t"); Serial.println(t);}
    return response;
}

//0 PRETRIAL

void preTrial(bool verbose = true) {   
    /* while the trial has not started 
       1. update the time
       2. check for licks
       4. trigger the recording by putting recTrig -> HIGH
    */
    int t = t_now(t_init);
    if (verbose) {Serial.print("#Enter `preTrial`:\t"); Serial.println(t);}
    
    while (t < 0){
        // 1. update time
        // 2. check for licks
        t = t_now(t_init);
        lickOn[0] = senseLick(0); 
        lickOn[1] = senseLick(1);
        
        digitalWrite(vacValve, HIGH);
        
        //TODO: define statusLED and plug in an LED to hardware
        // LED to flash each second before the trial
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
    digitalWrite(vacValve, LOW);
    
    if (verbose) {Serial.print("#Exit `preTrial`:\t"); Serial.println(t);}
    
} 

int TrialStimulus(int stimulusPin,
    int stimDUR,
    unsigned long ON = 5000, // us time of ON pulse    ie FREQUENCY of flutter
    unsigned long OFF = 5000, // us time of off pulse  ie FREQUENCY of flutter
    bool verbose = true) {
    
    int t = t_now(t_init);
    
    if (verbose) {
        // TODO make verbosity a scale instead of Boolean
        Serial.print("#Enter `TrialStimulus`:\t"); Serial.println(t);
        Serial.print("#stimDUR:\t"); Serial.println(stimDUR);
        Serial.print("#ON:\t"); Serial.println(ON);
        Serial.print("#OFF:\t"); Serial.println(OFF);
    }
    
    while (t < stimDUR){
        /* Run the buzzer while:
           1. update the time
           2. check for licks
        */
        t = t_now(t_init);
        lickOn[0] = senseLick(0); 
        lickOn[1] = senseLick(1);
        
        
        flutter(stimulusPin, ON, OFF);
       
        
    } digitalWrite(stimulusPin, LOW); //this is a safety catch
    
    if (verbose) {Serial.print("#Exit `TrialStimulus`:\t"); Serial.println(t);}
    return 1;
}

int TrialReward(char mode, // -'c'onditioning (guaranteed reward) -'o'perant (reward on lick)
                char rewardCond, // 'L'eft, 'R'ight, 'B'oth, 'N'either
                int waterVol = 10, // 10 ms gives ~ 5-8 uL
                bool verbose = true) {

    int t = t_now(t_init);
    bool RewardTest;
    int RewardPort;
    
    while (t < t_rewardEND) {
        
        t = t_now(t_init);
        
        lickOn[0] = senseLick(0); 
        lickOn[1] = senseLick(1);
        
        // response reports if there was a lick in the reward period
        
        switch (rewardCond){
            
            case 'L':
                RewardTest = (lickOn[0]) or (mode == 'c');
                RewardPort = 0;
            break;
                
            case 'R':
                RewardTest = (lickOn[1]) or (mode == 'c');
                RewardPort = 1;
            break;
            
            case 'B':
                RewardTest = (lickOn[0] or lickOn[1]) or (mode == 'c');
                if (lickOn[0]){RewardPort = 0;}
                if (lickOn[1]){RewardPort = 1;}
            break;
            
            case 'N':
                if (verbose) { Serial.print("#Exit `TrialReward`:\t"); Serial.println(t);}
                return 0;
            break;
            
            default:
                Serial.print("ERROR: rewardCond not specified");
                Serial.println(" requires 'L'eft, 'R'ight, 'B'oth, 'N'either");
                return -1;
            break;
        }
        
        if (RewardTest){
            digitalWrite(waterPort[RewardPort], HIGH);
            
            delay(waterVol);
            
            digitalWrite(waterPort[RewardPort], LOW);
            
            if (verbose) { Serial.print("#Exit `TrialReward`:\t"); Serial.println(t);}
            return 1;
        } 
        digitalWrite(waterPort[0], LOW);
        digitalWrite(waterPort[1], LOW);        //safety catch
    }
    
    if (verbose) {Serial.print("#Exit `TrialReward`:\t"); Serial.println(t);}
    return 1;
}

int runTrial (int mode,
    int trial_delay,
    int t_noLickPer,   // ms
    int t_stimONSET_0, //time stim 0 turns on
    int t_stimONSET_1, // time stim 1 turns on
    int stimDUR, // duration of stimuli
    int t_rewardSTART, // ms
    int t_rewardEND,   // ms
    int t_trialEND,   // ms
    bool stimTrial,
    char rewardCond,
    int waterVol,
    bool verbose) {
    // returns 0 if the stimulus was applied
    // returns 1 if a timeout is required
    // until next trial
    
    // local variables and initialisation of the trial
    int t; // local time
    
    
    
    /* t_init is initialised such that t_now
       returns 0 at the start of the trial, and 
       increases from there. */ 
    t_init = millis() + trial_delay;
    t = t_now(t_init);
    
    /*trial_phase0
    while the trial has not started 
       1. update the time
       2. check for licks
       3. trigger the recording by putting recTrig -> HIGH
    */
    
    preTrial(verbose);
    t = t_now(t_init);
       
    ActiveDelay(t_noLickPer - t, false, verbose);
    t = t_now(t_init);
    
    ActiveDelay(t_stimONSET_0 - t, true, verbose);
    t = t_now(t_init);
    
    TrialStimulus(stimulusPin, stimDUR, ON, OFF[0], verbose);
    t = t_now(t_init);
    
    ActiveDelay(t_stimONSET_1 - t, false, verbose);
    
    TrialStimulus(stimulusPin, stimDUR, ON, OFF[0], verbose);
    t = t_now(t_init);
    
    ActiveDelay(t_rewardSTART - t, false, verbose);
    t = t_now(t_init);
    
    if (rewardCond != 'N') {
        TrialReward(mode, rewardCond, waterVol, verbose);
    }
    else {
        ActiveDelay(t_trialEND - t, false, verbose);
    }   
}


