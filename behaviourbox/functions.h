/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/

void init_trial(char trialType);

char Habituation();

char ActiveDelay(unsigned long wait, bool break_on_lick = false);

void deliver_reward(bool port, char waterVol);

void punish(int del);

int Timeout(unsigned long wait, int depth = 0);
    
bool TrialStimulus(bool break_on_early);

void preTrial();

char TrialReward();

char runTrial();

/*--------------------------------------------------------++
||                  THE FUNCTIONS                         ||
++--------------------------------------------------------*/

void init_trial(char trialType){
    // This function sets the right and left
    // stimulus intensities to the same or different
    // depending on the value of `right_same`

    if (trialType == 'G'){
        rewardCond = 'B';
    }
    else if (trialType == 'N') {
        rewardCond = '-';
    }
    else {
        t_stimDUR = 0;
    }
}

char ActiveDelay(unsigned long wait, bool break_on_lick) {

    unsigned long t = t_now(t_init);

    char response = '-';

    if (verbose) {
        Serial.print("#Enter `ActiveDelay`:\t");
        Serial.println(t);
    }

    while (t < wait) {
        t = t_now(t_init);

        response = (response == '-')? get_response() : response;

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
    
    
    if (verbose) { 
        Serial.print("WaterPort[");
        Serial.print(port);
        Serial.print("]:\t");
        Serial.println("1");
    }
}

void punish(int del){

    digitalWrite(buzzerPin, HIGH);
    delay(del);
    digitalWrite(buzzerPin, LOW);
}

int Timeout(unsigned long wait, int depth) {

    unsigned long t_init = millis();
    unsigned long t = t_now(t_init);

   //delay(500); // Delay prevents punishing continued licking
    punish(150);

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

        if (t%1000 < 20){
            digitalWrite(statusLED, HIGH);
        }
        else {
            digitalWrite(statusLED, LOW);
        }

        // 3. trigger the recording
        if (t > -10){
            digitalWrite(recTrig, HIGH);
            digitalWrite(bulbTrig, HIGH);
        }
    }
    
    tone(speakerPin, 10000, 100); // cue tone
    digitalWrite(recTrig, LOW);

    if (verbose) {
        Serial.print("#Exit `preTrial`:\t");
        Serial.println(t);
    }
} 

bool TrialStimulus(bool break_on_early) {

    int t_local = millis();
    int t = t_now(t_local);

    // TODO this should be abstracted

    if (verbose) {
        // TODO make verbosity a scale instead of Boolean
        Serial.print("#Enter `TrialStimulus`:\t");

        Serial.println(t_now(t_init));
        
        Serial.print("#\tt_stimDUR:\t");
        Serial.println(t_stimDUR);
    }

    if (not t_stimDUR){
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
        return 0;
        
    }
    digitalWrite(stimulusPin, HIGH);
    
    while (t < t_stimDUR){
        /* Run the buzzer while:
           1. update the time
           2. check for licks
        */

        get_response();

        t = t_now(t_local);

        if ((lickOn[lick_port_L] or lickOn[lick_port_R])
                and break_on_early) {
            Serial.print("#\tLick Detected");
            Serial.print("#Exit `TrialStimulus`:\t");
            Serial.println(t);
            return 0;
        }
    }

    digitalWrite(stimulusPin, LOW); //this is a safety catch

    if (verbose) {
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
    }
    return 1;
}
