String version = "#behaviourbox160323";

/*
    Author: Naoya Takahashi
        modified by Andrew Micallef
                    Mohamed Salih 

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

unsigned int t_noLickPer = 1000;
unsigned int trial_delay = 1000; // ms
unsigned int t_stimONSET[] = {2000,2550};
unsigned int stimDUR = 500;
unsigned int t_rewardSTART = 3400; // ms
unsigned int t_rewardEND = 5000; // ms
unsigned int t_trialEND = 5000; // ms //maximum of 62 000

char mode = '-'; //one of 'h'abituation, 'o'perant
char rewardCond = 'R'; // a value that is 'L' 'R', 'B' or 'N' to represent lick port to be used
byte minlickCount = 5;

// stimulus parameters
// -------------------

bool single_stim;
bool right_same;

int off_short = 0;
int off_long = 40;

int ON = 30;
int diff_OFF[][2] =  {{off_short, off_long},
                      { off_long, off_short}};

int same_OFF[][2] = {{off_long, off_long},
                      { off_short, off_short}};

bool right = 1;
bool left = 0;
int right_OFF[2][2];
int left_OFF[2][2];

// audio
// -----
bool auditory = 0;

int toneGoodLeft = 6000; //Hz
int toneGoodRight = 7000; //Hz
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
bool break_wrongChoice = false; // stop if the animal makes a mistake
bool do_habituation = true;

/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/

char get_response();

char Habituation();

bool senseLick(bool sensor, bool* PreviousState);

int UpdateGlobals(String input);

void flutter(int OFF);

void init_ports();

char ActiveDelay(unsigned long wait, bool break_on_lick = false);
    
int TrialStimulus(int value);

void preTrial();

char TrialReward();

int runTrial();

long t_now(unsigned long t_init);

String getSerialInput();

int getSepIndex(String input, char seperator);

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
    pinMode(lickRep, OUTPUT);
    pinMode(speakerPin, OUTPUT);
    
    Serial.println("-- Status: Ready --");
}

void loop () {
    
    t_init = millis();
    
    if (Serial.available()){
        
        String input = getSerialInput();
        
        init_stim();
        
        if (input == "GO"){
            runTrial();
            Serial.println("-- Status: Ready --");
            digitalWrite(recTrig, LOW);
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

char get_response(){
    char response = 0;
    
    // Change the values of lickOn and lickOn 
    senseLick(left);
    senseLick(right);

    if (lickOn[left]){
        response = 'L';
    }
    else if (lickOn[right]){
        response = 'R';
    }
    
    // set the response to nothing if there was none
    if (!response){
        response = '-';
    }
    return response;
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

void flutter(int OFF){
  
  digitalWrite(stimulusPin, HIGH);
  delay(ON);
  
  digitalWrite(stimulusPin, LOW);
  delay(OFF);
}

void init_stim(){
    // This function sets the right and left
    // stimulus intensities to the same or different
    // depending on the value of `right_same`
        
    same_OFF[0][0] = off_short;
    same_OFF[0][1] = off_short;
    same_OFF[1][0] = off_long;
    same_OFF[1][1] = off_long;    
    
    diff_OFF[0][0] = off_short;
    diff_OFF[0][1] = off_long;
    diff_OFF[1][0] = off_long;
    diff_OFF[1][1] = off_short;
    
    if (single_stim) {
        diff_OFF[0][0] = -1;
        diff_OFF[1][0] = -1;
        
        same_OFF[0][0] = -1;
        same_OFF[1][0] = -1;
    }

    if (right_same){
        memcpy(right_OFF, same_OFF, sizeof(right_OFF));
        memcpy(left_OFF, diff_OFF, sizeof(left_OFF));
    }
    else {
        memcpy(right_OFF, diff_OFF, sizeof(right_OFF));
        memcpy(left_OFF, same_OFF, sizeof(left_OFF));
    }
}

char ActiveDelay(unsigned long wait, bool break_on_lick) {

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
        
        senseLick(left);
        senseLick(right);

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
    
    //digitalWrite(recTrig, LOW);
    
    if (verbose) {
        Serial.print("#Exit `preTrial`:\t");
        Serial.println(t);
    }
    
} 

int TrialStimulus(int value) {
    
    int t_local = millis();
    int t = t_now(t_local);
    
    // TODO this should be abstracted
    /*if (auditory) {
        if (value == off_short){
            value = 20000;
        } 
        else if (value == off_long){
            value = 5000;
        } 
    }*/
    
    if (verbose) {
        // TODO make verbosity a scale instead of Boolean
        Serial.print("#Enter `TrialStimulus`:\t");

        Serial.println(t_now(t_init));
        
        Serial.print("#\tauditory:\t");
        Serial.println(auditory);
        
        Serial.print("#\tstimDUR:\t");
        Serial.println(stimDUR);
        
        Serial.print("#\tvalue:\t");
        Serial.println(value);
    }
   
    if (auditory and (value > 0)) {
        tone(speakerPin, value, stimDUR - 10);
    }
        
    while (t < stimDUR){
        /* Run the buzzer while:
           1. update the time
           2. check for licks
        */
        senseLick(left);
        senseLick(right);
        
        if ((value >= 0) and (not auditory)){
            flutter(value);
        }
        
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
        
        count[left] = count[left] + senseLick(left);
        count[right] = count[right] + senseLick(right);
        
        // response reports if there was a lick in the reward period
        
        if (rewardCond == 'L') {
                RewardTest = (count[left] >= minlickCount);
                RewardPort = left;
        }
                
        else if (rewardCond ==  'R') {
                RewardTest = (count[right] >= minlickCount); 
                RewardPort = right;
        }
        
        if (RewardTest) {
            
            digitalWrite(waterPort[RewardPort], HIGH);

            if (verbose) { 
                Serial.print("WaterPort[");

                Serial.print(RewardPort);
                Serial.print("]:\t");
                Serial.println("1");               
            }
                        
            delay(waterVol);

            digitalWrite(waterPort[RewardPort], LOW);
             
            if (lickOn[left] and !response){ // hit left
                response = 'L';
                tone(speakerPin, toneGoodLeft, 50);
            } 
            if (lickOn[right] and !response){ // hit right
                response = 'R';
                tone(speakerPin, toneGoodRight, 50);
            } 
        
            if (verbose) { 
                Serial.print("count[0]:\t");
                Serial.println(count[left]);
                
                Serial.print("count[1]:\t");
                Serial.println(count[right]);
                
                Serial.print("#Exit `TrialReward`:\t");
                Serial.println(t);
            }
            return response;
        }
        else if (count[!RewardPort] >= minlickCount){
                        
            // declare the fail condition??
            
            if (!response) {
                tone(speakerPin, toneBad, 150);
                // TODO add random amount of time till trial end
                if (lickOn[left]) {
                    response = 'l';
                } //bad left 
                if (lickOn[right]) {
                    response = 'r';
                }  //bad right
            }
            if (break_wrongChoice){
                tone(speakerPin, toneBad, 150);
                if (verbose) { 
                    Serial.print("count[0]:\t");
                    Serial.println(count[left]);
                    
                    Serial.print("count[1]:\t");
                    Serial.println(count[right]);
                    
                    Serial.print("#Exit `TrialReward`:\t");
                    Serial.println(t);
                }
                return response;
            }
        }

        digitalWrite(waterPort[left], LOW);
        digitalWrite(waterPort[right], LOW);
       //safety catch
    }

    // miss 
    if (verbose) { 
        Serial.print("count[0]:\t");
        Serial.println(count[left]);
        
        Serial.print("count[1]:\t");
        Serial.println(count[right]);
        
        Serial.print("#Exit `TrialReward`:\t");
        Serial.println(t);
    }
    return response;
}

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
        OFF[0] = left_OFF[rbit][0];
        OFF[1] = left_OFF[rbit][1];
    }
    else if (rewardCond == 'R') {
        OFF[0] = right_OFF[rbit][0];
        OFF[1] = right_OFF[rbit][1];
    }
    
    /*trial_phase0
    while the trial has not started 
       1. update the time
       2. check for licks
       3. trigger the recording by putting recTrig -> HIGH
    */
    
    preTrial();
    t = t_now(t_init);
      
    ActiveDelay(t_noLickPer, false);
    t = t_now(t_init);
    
    response = ActiveDelay(t_stimONSET[0], t_noLickPer);
    
    if ((response != '-') and t_noLickPer){
        
        if (response == 'L'){
            response = 'l';
        }
        if (response == 'R'){
            response = 'r';
        }
        
        tone(speakerPin, toneBad, 150);
        
        Serial.print("response:\t");
        Serial.println(response);
        Serial.print("response_time:\t");
        Serial.println(t_now(t_init));
        
        Serial.println("count[0]:\tnan");
        Serial.println("count[1]:\tnan");
        Serial.println("OFF[0]:\tnan");
        Serial.println("OFF[1]:\tnan");
        
        ActiveDelay(t_trialEND, false);
        
        return 0;
    }
    
    t = t_now(t_init);
    
    TrialStimulus(OFF[0]);
    t = t_now(t_init);
    
    ActiveDelay(t_stimONSET[1], false);
    t = t_now(t_init);
    
    TrialStimulus(OFF[1]);
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
    
    if (response != rewardCond) {

        if (response == 'L'){
            response = 'l';
            //tone(speakerPin, toneBad, 150);
        }
        else if (response == 'R'){
            response = 'r';
            //tone(speakerPin, toneBad, 150);
        }
        else if (!response){
            response = '-';
        }
    }
    
    ActiveDelay(t_trialEND, false);
    
    Serial.print("response:\t");
    Serial.println(response);
    Serial.print("response_time:\t");
    Serial.println(response_time);
    
    Serial.print("OFF[0]:\t");
    Serial.println(OFF[0]);
    
    Serial.print("OFF[1]:\t");
    Serial.println(OFF[1]);
    
   
    return 0;
}

char Habituation(){
    
    bool rbit = random(0,2); // a random bit
    bool port = 0;
    int t_interStimdelay = t_stimONSET[1] 
                            - (t_stimONSET[0] + stimDUR);
    int intensity[2] = {0,0};
    t_init = millis();

    char response = get_response();
    
    if (response != '-') {
        
        if (response == 'L') {
            intensity[0] = left_OFF[rbit][0];
            intensity[1] = left_OFF[rbit][1];
            port = left;
        }
        
        else if (response == 'R'){
            intensity[0] = right_OFF[rbit][0];
            intensity[1] = right_OFF[rbit][1];
            port = right;
        }
        
        digitalWrite(waterPort[port], HIGH);
        delay(waterVol);
        digitalWrite(waterPort[port], LOW);
        
        tone(speakerPin, toneGood, 50);

        TrialStimulus(intensity[0]);
        
        delay(t_interStimdelay);
        
        TrialStimulus(intensity[1]);
                    
        if (ActiveDelay(500u, true) == response){
            digitalWrite(waterPort[port], HIGH);
            delay(waterVol);
            digitalWrite(waterPort[port], LOW);
        }
        
        ActiveDelay(3500u, false);
      }

  return response;    
}

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
    int sep = getSepIndex(input, ':');

    if (sep) {
        
        String variable_name = input.substring(0,sep);
        String variable_value = input.substring(sep+1);
        
        Serial.print("#");
        Serial.print(variable_name);
        Serial.print("\t");
        Serial.println(variable_value);
        
        // input before seperator?
        
        if (variable_name == "lickThres") {
                lickThres = variable_value.toInt();
                Serial.print("lickThres:\t");
                Serial.println(lickThres);
                return 1;
        }
            
        else if (variable_name == "mode") {
                mode = variable_value[0];
                Serial.print("mode:\t");
                Serial.println(mode);
                return 1;
        }
            
        else if (variable_name == "rewardCond") {
                rewardCond = variable_value[0];
                Serial.print("rewardCond:\t");
                Serial.println(rewardCond);
                return 1;
        }
          
        else if (variable_name == "break_wrongChoice") {
                break_wrongChoice = bool(variable_value.toInt());
                Serial.print("break_wrongChoice:\t");
                Serial.println(break_wrongChoice);
                return 1;
        }
            
        else if (variable_name == "minlickCount") {
                minlickCount = variable_value.toInt();
                Serial.print("minlickCount:\t");
                Serial.println(minlickCount);
                return 1;
        }
        else if (variable_name == "t_noLickPer") {
                t_noLickPer = variable_value.toInt();
                Serial.print("t_noLickPer:\t");
                Serial.println(t_noLickPer);
                return 1;
        }
        else if (variable_name == "right_same") {
                right_same = bool(variable_value.toInt());
                Serial.print("right_same:\t");
                Serial.println(right_same);
                return 1;
        }
        else if (variable_name == "off_short") {
                off_short = variable_value.toInt();
                Serial.print("off_short:\t");
                Serial.println(off_short);
                return 1;
        }
        else if (variable_name == "off_long") {
                off_long = variable_value.toInt();
                Serial.print("off_long:\t");
                Serial.println(off_long);
                return 1;
        }
        else if (variable_name == "auditory") {
                auditory = bool(variable_value.toInt());
                Serial.print("auditory:\t");
                Serial.println(auditory);
                return 1;
        }
        else if (variable_name == "single_stim") {
                single_stim = bool(variable_value.toInt());
                Serial.print("single_stim:\t");
                Serial.println(single_stim);
                return 1;
        }
        
   }
   return 0;
}


/*----------------------------------------------++
||                  Serial Coms                 ||
++----------------------------------------------*/

String getSerialInput(){

    /*
      This function reads the data from the serial 
      connection and returns it as a string. 
      
      This is used later to update the values
    */
    String readString;
    
    while (Serial.available()) { 
        /* 1. delay to allow buffer to fill
           2. get one byte from serial buffer
           3. make the string readString 
       */
        
        delay(3);  
        char c = Serial.read();  
        readString += c; 
    }
    
    return readString;
}

int getSepIndex(String input, char seperator) {
    /*
      Returns the index of the seperator character
      in a string.
    */
    
    char c = 1;
    int i = 0;
   
    while (c != 0) {
        c = input[i];
        if (c == seperator){ 
            return i; 
        }
        i ++;
    }
    return 0;
}

/*----------------------------------------------++
||                  Timing                      ||
++----------------------------------------------*/

long t_now(unsigned long t_init){
    // The time since t_init:
    //   + is less than 0 before the trial starts
    //   + is greater than 0 after the start of trial

    return (long) millis() - t_init;
}



