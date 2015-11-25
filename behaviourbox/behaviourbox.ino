String version = "#behaviourbox151119";

//TODO: make a conditioning protocol
//TODO: rename singlestim operant
//TODO: find an obvious method for producing constant noise

/*
Authour: Naoya Takahashi
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


char lickport; //?? a value that is L R or 0 to represent lick port to be used


int lickThres = 450;

// timing parameters
int t_init;
int t_start;

int t_noLickPer = 0;   // ms
int t_stimSTART = 4000;   // ms
int t_stimEND = 4500;     // ms
int t_rewardSTART = 4500; // ms
int t_rewardEND = 10000;   // ms
int t_trialEND = 10000;   // ms
int minITI = 3000;        // ms
int maxITI = 6000;        // ms
int maxTimeOut = 0;    // ms
int minTimeOut = 0;    // ms

int t_stimONSET_0;
int t_stimONSET_1;
int stimDUR;






// stimulus parameters
unsigned long ON = 1000;

unsigned long OFF[] = {5000, 5000};


int toneBad = 500; //Hz
int toneDur = 100; 

// Global value to keep track of the total water consumed
int waterCount = 0; 
int waterVol = 5; //uL per dispense


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
    
    //was three lines before
    Serial.print("#Lick Threshold:\t"); Serial.print((float(lickThres)/1024)*5); Serial.println(" V");
    
    randomSeed(analogRead(5));

    pinMode(recTrig, OUTPUT); // declare the recTrig as as OUTPUT
    pinMode(waterPort[0], OUTPUT); // declare the waterValve as as OUTPUT
    pinMode(vacValve, OUTPUT); // declare the vacValve as as OUTPUT
    pinMode(stimulus, OUTPUT); // declare the whiskStim as as OUTPUT
    pinMode(lickRep[0], OUTPUT); // declare the licking as as OUTPUT
    pinMode(tonePin, OUTPUT);
}


void loop () {
    
    int mode = 0;
    
    String input = getSerialInput();
    
    if (input) {
        // single char flags are preceded by '-'
        // strip the '-' and proceed with parsing
        if (input[0] == '-') {
            
            input = input.substring(1);
            
            if ((input[0] == 'm') or (input[0] == 'M'))) {
            
                mode = getMode(input);
                
                if (mode >= 0){
                    // single trial returns an inter trial interval   
                    Serial.println(
                        "modeString\tistimeout\tstimTrial\tresponse\tlickCount");
                   
                    Serial.println(runTrial(mode));
                }
            }
            
            else if ((input[0] == 'f') or (input[0] == 'F')) {
                getFreq(input);
            }
            
            else if ((input[0] == 'p') or (input[0] == 'P')) {
                port = getValue(input);
            } 
        }
        
        else {
            
            int sep = getSepIndex(input);
            
            // input before seperator?
            if (input[0,sep] == "t_noLickPer") { t_noLickPer = getValue(input); }
            if (input[0,sep] == "t_stimSTART0") { t_stimSTART0 = getValue(input); }
            if (input[0,sep] == "t_stimEND0") { t_stimEND0 = getValue(input); }
            if (input[0,sep] == "t_stimSTART1") { t_stimSTART1 = getValue(input); }
            if (input[0,sep] == "t_stimEND1") { t_stimEND1 = getValue(input); }
            if (input[0,sep] == "t_rewardSTART") { t_rewardSTART = getValue(input); }
            if (input[0,sep] == "t_rewardEND") { t_rewardEND = getValue(input); }
            if (input[0,sep] == "t_trialEND") { t_trialEND = getValue(input); }
            if (input[0,sep] == "minITI") { minITI = getValue(input); } 
            if (input[0,sep] == "maxITI") { maxITI = getValue(input); }
            if (input[0,sep] == "maxTimeOut") { maxTimeOut = getValue(input); }
            if (input[0,sep] == "minTimeOut") { minTimeOut = getValue(input); }
            if (input[0,sep] == "stimTrial") { stimTrial = getValue(input); }
            if (input[0,sep] == "rewardCond") { rewardCond = getValue(input); }
        }
    }    
    
    if (senseLick(0) or senseLick(1)){
        tone(tonePin, toneBad, 10);
        delay(100);
    }
}

int runTrial (int modeSwitch,
    int t_noLickPer,   // ms
    int t_stimONSET_0, //time stim 0 turns on
    int t_stimONSET_1, // time stim 1 turns on
    int stimDUR, // duration of stimuli
    int stimGAP, // gap from end stim 0 to start stim 1
    int t_rewardSTART, // ms
    int t_rewardEND,   // ms
    int t_trialEND,   // ms
    int minITI,        // ms
    int maxITI,        // ms
    int maxTimeOut,    // ms
    int minTimeOut,    // ms
    bool stimTrial,
    char rewardCond,
) {
    // returns 0 if the stimulus was applied
    // returns 1 if a timeout is required
    // until next trial
    
    // local variables and initialisation of the trial
    String outString = "";
    int t; // local time
    int timeout = 0;
    
    String modeString;
  
    bool response = false;
    bool lickOn[] = {false, false};
    bool firstLick = true;
    
    
    /* t_init is initialised such that t_now
       returns 0 at the start of the trial, and 
       increases from there. */ 
    t_init = millis() + trial_delay;
    t = t_now(t_init);
    
    Serial.print(t); Serial.println(" ms");
    
    /*trial_phase0
    while the trial has not started 
       1. update the time
       2. check for licks
       3. trigger the recording by putting recTrig -> HIGH
    */
    
    preTrial(verbose);
    t = t_now(t_init);
    
    TrialStart(t_noLickPer, verbose);
    t = t_now(t_init);
    
    ActiveDelay(t_stimONSET_0 - t, false, verbose);
    
    TrialStimulus(stimulusPin, stimDUR, ON, OFF[0], verbose);
    t = t_now(t_init);
    
    ActiveDelay(t_stimONSET_1 - t, false, verbose);
    
    TrialStimulus(stimulusPin, stimDUR, ON, OFF[0], verbose);
    t = t_now(t_init);
    
    ActivDelay(t_rewardSTART - t, false, verbose);
    t = t_now(t_init);
    
    if (rewardCond != 'N') {
        TrialReward(, verbose);
    }
    else {
        ActivDelay(t_trialEND - t, false, verbose);
    }
    
    // reward period
    //trial_phase0
    
    
    Serial.print("#trial End:\t"); Serial.println(t - t_trialEND); Serial.print("#Licks? :\t"); Serial.println(response);
    
    waterCount += (int(response) * waterVol);
    
    Serial.print(modeString); Serial.print("\t"); 
    Serial.print(waterCount); Serial.print("\t"); 
    Serial.print(trial_delay); Serial.print("\t"); 
    Serial.print(timeout>0); Serial.print("\t"); 
    Serial.print(stimTrial); Serial.print("\t"); 
    Serial.print(response); Serial.print("\n"); 
                
    return random(minITI, maxITI);
}


int t_now(int t_init){
    // is less than 0 before the trial starts
    // is greater than 0 after the start of trial
    return millis() - t_init;
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

char* getSerialInput(){

    char* readString;
    
    while (Serial.available()) { 
        delay(3);  //delay to allow buffer to fill
        char c = Serial.read();  //gets one byte from serial buffer
        readString += c; //makes the string readString
    }
    
    return readString;
}

int getValue(String input){
    
    int val = 0;   // value to return for port
    
    //return the value of the string after the seperator
    int val = input.substring(getSepIndex(input)).toInt();
    return val;
}

int getMode(String input){
    
    int m = -1;    //value to return for mode

    if ((input[0] != 'm') and (input[0] != 'M')){
        Serial.println("Invalid input to getMode");
        return -1;
    }
    
    return input.substring(1).toInt();
}

int getFreq(String input){
    // returns -ve on failure
    if ((input[0] != 'f') and (input[0] != 'F')){
        Serial.println("Invalid input to getFreq");
        return -1;
    }
    
    int index = input[1] - '0';

    char c = 1;
    int i = 0;
   
    while (c != 0) {
        c = input[i];
        
        if (c == ':'){
            break;
        }
        i ++;
    }
    if (c == 0) {
        Serial.println("No frequency found");
        return -2;
    }
    else {
        OFF[index] = (unsigned long)input.substring(i+1).toInt();
        return index;
    }
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

int serialComs(){
    
  if (readString.length() > 0) {
    Serial.print("#input:\t");
    Serial.println(readString);
    
    
  if (input.length() > 0) {
  

  input = "";
  }
      
      
      
             
            char flag = readString[0];
            
            switch(flag){
                case 't': {
                    char* value = strtok(readString, ":");
                    ++value; //move pointer by one
                    lickThres = value.atoi();
                    
                    Serial.print("#lickThres set:\t");
                        Serial.print(lickThres);
                        Serial.print(" (");
                        Serial.print((float(lickThres)/1024)*5);
                        Serial.println(" V)");
                } break;
                 case 'm': {
                    return getMode(input);
                } break;            
                case 'p': {
                    char* value = strtok(readString, ":");
                    ++value; //move pointer by one
                   
                    if value[0] == 'L'{ //switch to reward left if left lick
                        return;
                    }
                    if value[0] == 'R'{ //switch to reward right if right lick
                        ;
                    }
                     if value[0] == '1'{ 
                     // switch to reward from the port licked at
                     // if either port is detected.
                        ;
                    }
                    else { // no reward on this trial
                        ;
                    } 
                }
                default:
                    Serial.println("#could not parse input");
                break;
                
            }
            readString = "";
        }             
    }
    return mode;
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
    
    unsigned long t_init = millis() // 
    int t = t_now(t_init);
    
    if (verbose) {Serial.print("#Exit `ActiveDelay`:\t"); Serial.println(t);}
    
    while (t < wait) {
        t = t_now(t_init);
        lickOn[0] = senseLick(0);
        lickOn[1] = senseLick(1);
        
        if (break_on lick and (lickOn[0] or lickOn[1])){
            if (verbose) {
                Serial.print("#Exit `ActiveDelay`:\t"); Serial.println(t);
                Serial.print("#port[0]:\t"); Serial.println(lickOn[0]);
                Serial.print("#port[1]:\t"); Serial.println(lickOn[1]);
            }
            return 0;
        }
    }
    
    if (verbose) {Serial.print("#Exit `ActiveDelay`:\t"); Serial.println(t);}
    return 1;
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

// 1 START PHASE
int TrialStart(bool verbose = true) {
    /* This function returns a 1 if the trial can continue,
       
       
       returns 0 if a time out has been invoked

     The trial has started but the stimulus
       is yet to be delivered, so long as timeout
       is not in place
       1. update the time
       2. check for licks
       3. punish licks with additional timeout\
          this breaks the function and ultimatley results
          in a line being printed with the lick time `t`.
    */
    
    int t = t_now(t_init);
    
    if (verbose) {Serial.print("#Enter `TrialStart`:\t"); Serial.println(t);}
    
    while (t < t_stimSTART){

        // 1. update the time
        // 2. check for licks  
        t = t_now(t_init);
        
        lickOn[0] = senseLick(0); 
        lickOn[1] = senseLick(1);
        
        // 3. punish licks with additional timeout
        if ((lickOn[0] or lickOn[1]) 
            and (t_noLickPer) 
            and (t > t_noLickPer)) {
            /* conditions
                : 
                1. if the animal has licked
                2. if there is a no lick period 
                    (is false during conditioning)
                3. if the no lick period has started
                    (the timenow is greater than no lick time)
            */ 
            
            // 3.2. report that a timeout has occurred
            Serial.println("#timeout added:\t");
            
            // 3.3. report to the animal that timeout has occurred
            tone(tonePin, toneBad, toneDur);
            
            // 3.4. make a standard output line
           
            Serial.print(modeString); Serial.print("\t"); 
            Serial.print(waterCount); Serial.print("\t"); 
            Serial.print(trial_delay); Serial.print("\t"); 
            Serial.print(timeout>0); Serial.print("\t"); 
            Serial.print(stimTrial); Serial.print("\t"); 
            Serial.print(response);  Serial.print("\n");
             
            // exits, starting a new trial in the higher loop
            // 3.1. set a timout value
            if (verbose) {
                Serial.print("#Exit `TrialStart`:\t"); 
                Serial.print(t);
                Serial.println(" with timeout")}
            return 0;
        }
    }
    
    if (verbose) {Serial.print("#Exit `TrialStart`:\t"); Serial.println(t);}
    return 1;
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
    return 1
}

int TrialReward(char mode, // -'c'onditioning (guaranteed reward) -'o'perant (reward on lick)
                char rewardCond, // 'L'eft, 'R'ight, 'B'oth, 'N'either
                int waterVol = 10, // 10 ms gives ~ 5-8 uL
                bool verbose = true) {

    int t = t_now(t_init);
    bool RewardTest;
    bool RewardPort[] = {false, false};
    
    while (t < t_rewardEND) {
        
        t = t_now(t_init);
        
        lickOn[0] = senseLick(0); 
        lickOn[1] = senseLick(1);
        
        // response reports if there was a lick in the reward period
        
        switch (rewardCond){
            
            case 'L':
                RewardTest = (lickOn[0]) or (mode == 'c')
                RewardPort = 0;
            break;
                
            case 'R':
                RewardTest = (lickOn[1]) or (mode == 'c')
                RewardPort = 1;
            break;
            
            case 'B':
                RewardTest = (lickOn[0] or lickOn[1]) or (mode == 'c')
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
            break;
        }
        
        if (RewardTest){
            digitalWrite(waterPort[RewardPort], HIGH);
            
            delay(waterVol);
            
            digitalWrite(waterPort[RewardPort], LOW);
            
            if (verbose) { Serial.print("#Exit `TrialReward`:\t"); Serial.println(t);}
            return 1
        } 
        
        digitalWrite(waterPort[0], LOW);
        digitalWrite(waterPort[1], LOW);        //safety catch
    }
    
    if (verbose) {Serial.print("#Exit `TrialReward`:\t"); Serial.println(t);}
    return 1;
}