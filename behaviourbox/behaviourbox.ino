String version = "#behaviourbox_v2.0_160612_durdesc";

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
unsigned int trial_delay = 500; // ms
unsigned int t_stimONSET = 2000;
unsigned int t_stimDELAY = 100; //ms
unsigned int t_stimDUR = 500;
unsigned int t_rDELAY = 2100; // ms
unsigned int t_rDUR = 2000; // ms
unsigned int timeout = 0;

char mode = '-'; //one of 'h'abituation, 'o'perant
char rewardCond = 'R'; // a value that is 'L' 'R', 'B' or 'N' to represent lick port to be used
byte minlickCount = 5;

// Globals to count number of continuous left and rights
byte reward_count[] = {0, 0};

// stimulus parameters
// -------------------

bool single_stim;
bool right_same;

int DUR_short = 100;
int DUR_long = 500;

int diff_DUR[][2] =  {{DUR_short, DUR_long},
                      { DUR_long, DUR_short}};

int same_DUR[][2] = {{ DUR_long, DUR_long},
                     {DUR_short, DUR_short}};

bool right = 1;
bool left = 0;

int right_DUR[2][2];
int left_DUR[2][2];

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


// Global value to count the licks
byte count[] = {0,0};

char waterVol = 10; //uL per dispense

int lickThres = 450;
bool lickOn[] = {false, false};

bool verbose = true;
bool break_wrongChoice = false; // stop if the animal makes a mistake

/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/

char get_response();

char Habituation();

bool senseLick(bool sensor, bool* PreviousState);

int UpdateGlobals(String input);

void init_ports();

char ActiveDelay(unsigned long wait, bool break_on_lick = false);

void deliver_reward(bool port, char waterVol);

int Timeout(unsigned long wait, int depth = 0);
    
int TrialStimulus(int duration);

void preTrial();

char TrialReward();

char runTrial();

long t_now(unsigned long t_init);

void printCounts(byte count[2]);

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

void init_stim(){
    // This function sets the right and left
    // stimulus intensities to the same or different
    // depending on the value of `right_same`
        
    same_DUR[0][0] = DUR_short;
    same_DUR[0][1] = DUR_short;
    same_DUR[1][0] = DUR_long;
    same_DUR[1][1] = DUR_long;    
    
    diff_DUR[0][0] = DUR_short;
    diff_DUR[0][1] = DUR_long;
    diff_DUR[1][0] = DUR_long;
    diff_DUR[1][1] = DUR_short;
    
    if (single_stim) {
        diff_DUR[0][0] = -1;
        diff_DUR[1][0] = -1;
        diff_DUR[0][1] = right_same? DUR_long : DUR_short;
        diff_DUR[1][1] = right_same? DUR_long : DUR_short;
        
        same_DUR[0][0] = -1;
        same_DUR[1][0] = -1;
        same_DUR[0][1] = right_same? DUR_short : DUR_long;
        same_DUR[1][1] = right_same? DUR_short : DUR_long;
    }

    if (right_same){
        memcpy(right_DUR, same_DUR, sizeof(right_DUR));
        memcpy(left_DUR, diff_DUR, sizeof(left_DUR));
    }
    else {
        memcpy(right_DUR, diff_DUR, sizeof(right_DUR));
        memcpy(left_DUR, same_DUR, sizeof(left_DUR));
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

void deliver_reward(bool port, char waterVol) {
    /* Open the water port on `port` for a 
        duration defined by waterVol */
    
    digitalWrite(waterPort[port], HIGH);
    delay(waterVol);
    digitalWrite(waterPort[port], LOW);
}

int Timeout(unsigned long wait, int depth) {
    
    unsigned long t_init = millis();
    unsigned long t = t_now(t_init);
    
   //delay(500); // Delay prevents punishing continued licking
    tone(speakerPin, toneBad, 150);
    
    while (t < wait) {
        t = t_now(t_init);
        
        if (get_response() != '-') {
            if (depth < 10) {
                depth ++;
                depth = Timeout(wait, depth);
                break;
            }
        }
    }
    
    return depth;
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
        else {
            digitalWrite(statusLED, LOW);
        }
        
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

int TrialStimulus(int duration) {
    
    int t_local = millis();
    int t = t_now(t_local);
    // reset the lick counter
    count[0] = 0;
    count[1] = 0; 
    
    // TODO this still feels inelegant

    if (verbose) {
        // TODO make verbosity a scale instead of Boolean
        Serial.print("#Enter `TrialStimulus`:\t");

        Serial.println(t_now(t_init));
        
        Serial.print("#\tauditory:\t");
        Serial.println(auditory);
        
        Serial.print("#\tduration:\t");
        Serial.println(duration);
    }
   
    if (auditory and (intensity > 0)) {
        tone(speakerPin, intensity, duration - 10);
    }
    
    // Run the buzzer if this is not an auditory trial
    // update the time after each square pulse
    if ((intensity >= 0) and (not auditory)){
        digitalWrite(stimulusPin, HIGH);
    }
    while (t < duration){
        t = t_now(t_local);
        
        count[left] = count[left] + senseLick(left);
        count[right] = count[right] + senseLick(right);
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
    int t_END = t + t_rDUR;
    bool RewardTest = 0;
    bool RewardPort = 0;
    char response = 0;
    byte count[] = {0,0};
    int N_to; //number of timeouts
    
    if (verbose) {
        Serial.print("#Enter `TrialReward`:\t");
        Serial.println(t);
    }
    
    while (t < t_END) {
        
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
            /* This next block opens the water port on the 
            correct side and returns the response */
            digitalWrite(waterPort[RewardPort], HIGH);

            if (verbose) { 
                Serial.print("WaterPort[");
                Serial.print(RewardPort);
                Serial.print("]:\t");
                Serial.println("1");               
            }
                        
            delay(waterVol);
            digitalWrite(waterPort[RewardPort], LOW);
             
            /* set the response to be returned based on
               the value received. The response is queried first,
               making sure that a response hasn't been set. If
               a response has already been recorded, the first
               response stands as the one reported.
               Also play the associated reward tone */
               
            if (rewardCond == 'L'){ // hit left
                response = !response? 'L': response;
                tone(speakerPin, toneGoodLeft, 50);
            } 
            if (rewardCond == 'R'){ // hit right
                response = !response? 'R': response;
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
            
            // pause for 1.5s to allow for drinking
            ActiveDelay(t + 1500, false);
            
            return response;
        }
        else if (count[!RewardPort] >= minlickCount){
                        
            // declare the fail condition??
            
            if (RewardPort == left){
                response = 'r'; // bad right
            }
            else if (RewardPort == right){
                response = 'l'; // bad left
            }
            
            if (!response) {
                tone(speakerPin, toneBad, 150);
            }
            
            if (break_wrongChoice){
                if (timeout) {
                    N_to = Timeout(timeout); //count the number of timeouts                 
                    Serial.print("N_timeouts:\t");
                    Serial.println(N_to);
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

char runTrial() { 
    
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
    int DUR[2] = {-1, -1};
    
    // local time
    t_init = millis() + trial_delay;
    t = t_now(t_init);
    
    // select the frequency pair to use
    if (rewardCond == 'L') {
        DUR[0] = left_DUR[rbit][0];
        DUR[1] = left_DUR[rbit][1];
    }
    else if (rewardCond == 'R') {
        DUR[0] = right_DUR[rbit][0];
        DUR[1] = right_DUR[rbit][1];
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
    
    response = ActiveDelay(t_stimONSET, bool(t_noLickPer));
    
    if ((response != '-') and t_noLickPer){
        
        if (response == 'L'){
            response = 'l';
        }
        if (response == 'R'){
            response = 'r';
        }

        //tone(speakerPin, toneBad, 150);

        Serial.print("response:\t");
        Serial.println(response);
        Serial.print("response_time:\t");
        Serial.println(t_now(t_init));

        Serial.println("count[0]:\tnan");
        Serial.println("count[1]:\tnan");
        Serial.println("DUR[0]:\tnan");
        Serial.println("DUR[1]:\tnan");

        return response;
    }
    
    t = t_now(t_init);
    
    TrialStimulus(DUR[0]); // lock the intensity at highest
        Serial.print("stim0_count[0]:\t");
        Serial.println(count[0]);
        Serial.print("stim0_count[1]:\t");
        Serial.println(count[1]);
    t = t_now(t_init);
    
    ActiveDelay(t_stimONSET + t_stimDELAY, false);
    t = t_now(t_init);
    
    TrialStimulus(DUR[1]); // lock the intensity at highest
        Serial.print("stim1_count[0]:\t");
        Serial.println(count[1]);
        Serial.print("stim1_count[1]:\t");
        Serial.println(count[1]);
    t = t_now(t_init);

    // TODO include contingency to report on lick early without breaking?
    ActiveDelay(t + t_rDELAY, false);
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
    
    Serial.print("response:\t");
    Serial.println(response);
    Serial.print("response_time:\t");
    Serial.println(response_time);
        
    Serial.print("DUR[0]:\t");
    Serial.println(DUR[0]);
    
    Serial.print("DUR[1]:\t");
    Serial.println(DUR[1]);
    
    return response;
}

char Habituation(){
    
    bool rbit = random(0,2); // a random bit
    bool port = 0;
    int duration[2] = {0,0};
    t_init = millis();
    
    // Check the lick sensor
    char response = get_response();
    
    if (response != '-') {
        
        /* 
        1. Determine the appropriate stimulus
        2. set active port 
        3. counts number of sequential licks
            - Uses the C ternary operator, which has the form:
              `A = boolean ? assignment if true : assignment if false;`
              the active port count gets incremented to a maximum of ten,
              while the non-active port count gets decremented to a minimum
              of zero. This is an important caveat as the counts are 
              made with unsigned variables, meaning that one less than zero
              is actually 255!              
        */
        if (response == 'L') {
            duration[0] = left_DUR[rbit][0];
            duration[1] = left_DUR[rbit][1];
            port = left;
            reward_count[left] = (reward_count[left] < 10) ? reward_count[left] += 1 : 10;
            reward_count[right] = reward_count[right] ? reward_count[right] -= 1 : 0;
        }
        else if (response == 'R'){
            duration[0] = right_DUR[rbit][0];
            duration[1] = right_DUR[rbit][1];
            port = right;
            
            reward_count[right] = (reward_count[right] < 10) ? reward_count[right] += 1 : 10;
            reward_count[left] = reward_count[left] ? reward_count[left] -= 1 : 0;
        }

        
        // only activate if less than 10 in a row on this port
        if (reward_count[port] < 10) {
            
            // stim0, stim1, reward...
            TrialStimulus(duration[0]);            
            delay(t_stimDELAY);
            TrialStimulus(duration[1]);
            deliver_reward(port, waterVol);
                    
            ActiveDelay(3500u, false);
        
            /* Output should allow me to make the following table:
                stim0   stim1   response
                ------- ------- --------
            */
            Serial.print("DUR[0]:\t");
            Serial.println(duration[0]);
            
            Serial.print("DUR[1]:\t");
            Serial.println(duration[1]);
            Serial.print("response:\t");
            Serial.println(response);
            Serial.print("reward_count:\t");
            Serial.println(int(reward_count[port]));
        }

        Serial.println("-- Status: Ready --");
    }

  return response;    
}

/*----------------------------------------------++
||                Utility                       ||
++----------------------------------------------*/

void printCounts(byte count[2]) {
    
    Serial.print("count[0]:\t");
    if (count[0] != -1) {
        Serial.println(count[0]);
    }
    else {
        Serial.println('nan');
    }
 
 Serial.print("count[1]:\t");
    if (count[1] != -1) {
        Serial.println(count[1]);
    }
    else {
        Serial.println('nan');
    }            
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
        else if (variable_name == "timeout") {
                timeout = variable_value.toInt();
                Serial.print("timeout:\t");
                Serial.println(timeout);
                return 1;
        }
        else if (variable_name == "t_stimDUR") {
                t_stimDUR = variable_value.toInt();
                Serial.print("t_stimDUR:\t");
                Serial.println(t_stimDUR);
                return 1;
        }
        else if (variable_name == "t_stimONSET") {
                t_stimONSET = variable_value.toInt();
                Serial.print("t_stimONSET:\t");
                Serial.println(t_stimONSET);
                return 1;
        }
        else if (variable_name == "t_rDELAY") {
                t_rDELAY = variable_value.toInt();
                Serial.print("t_rDELAY:\t");
                Serial.println(t_rDELAY);
                return 1;
        }
        else if (variable_name == "t_rDUR") {
                t_rDUR = variable_value.toInt();
                Serial.print("t_rDUR:\t");
                Serial.println(t_rDUR);
                return 1;
        }
        else if (variable_name == "waterVol") {
                waterVol = variable_value.toInt();
                Serial.print("waterVol:\t");
                Serial.println(waterVol);
                return 1;
        }
        else if (variable_name == "DUR_short") {
                DUR_short = variable_value.toInt();
                Serial.print("DUR_short:\t");
                Serial.println(DUR_short);
                return 1;
        }
        else if (variable_name == "DUR_long") {
                DUR_long = variable_value.toInt();
                Serial.print("DUR_long:\t");
                Serial.println(DUR_long);
                return 1;
        }
        else if (variable_name == "OFF") {
                OFF = variable_value.toInt();
                Serial.print("OFF:\t");
                Serial.println(OFF);
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

int getSepIndex(String input, char separator) {
    /*
      Returns the index of the separator character
      in a string.
    */
    
    char c = 1;
    int i = 0;
   
    while (c != 0) {
        c = input[i];
        if (c == separator){ 
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



