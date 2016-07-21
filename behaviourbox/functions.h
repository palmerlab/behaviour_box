/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/

char Habituation();

char ActiveDelay(unsigned long wait, bool break_on_lick = false);

void deliver_reward();

void punish(int del);

int Timeout(unsigned long wait, int depth = 0);
    
int TrialStimulus(bool break_on_early);

void preTrial();

char TrialReward();

char runTrial();

/*--------------------------------------------------------++
||                  THE FUNCTIONS                         ||
++--------------------------------------------------------*/


char ActiveDelay(unsigned long wait, bool break_on_lick) {

    unsigned long t = t_since(t_init);

    char response = 0;

    if (verbose) {
        Serial.print("#Enter `ActiveDelay`:\t");
        Serial.println(t);
    }

    while (t < wait) {
        t = t_since(t_init);

        response = response? response : senseLick();

        if (break_on_lick and response){
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

void deliver_reward() {
    /* Open the water port on `port` for a 
        duration defined by waterVol */

    digitalWrite(waterPort, HIGH);
    delay(waterVol);
    digitalWrite(waterPort, LOW);
    
    if (verbose) { 
        Serial.print("Water:\t");
        Serial.println(waterVol);
    }
}

void punish(int del) {

    digitalWrite(buzzerPin, HIGH);
    delay(del);
    digitalWrite(buzzerPin, LOW);
}

int Timeout(unsigned long wait, int depth) {

    unsigned long t_init = millis();
    unsigned long t = t_since(t_init);

   //delay(500); // Delay prevents punishing continued licking
    punish(500);

    while (t < wait) {
        t = t_since(t_init);

        if (senseLick()) {
            
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
    long t = t_since(t_init);

    if (verbose) {
        Serial.print("#Enter `preTrial`:\t");
        Serial.println(t);
    }

    while (t < 0){
        // 1. update time
        // 2. check for licks
        t = t_since(t_init);

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
    
    //tone(speakerPin, 10000, 100); // cue tone
    digitalWrite(recTrig, LOW);

    if (verbose) {
        Serial.print("#Exit `preTrial`:\t");
        Serial.println(t);
    }
} 

int TrialStimulus(bool break_on_early) {

    int t_local = millis();
    int t = t_since(t_local);
    int count = 0;

    // TODO this should be abstracted

    if (verbose) {
        // TODO make verbosity a scale instead of Boolean
        Serial.print("#Enter `TrialStimulus`:\t");

        Serial.println(t_since(t_init));
        
        Serial.print("#\tt_stimDUR:\t");
        Serial.println(t_stimDUR);
    }

    if (not t_stimDUR){
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
        return count;
        
    }
    digitalWrite(stimulusPin, HIGH);
    
    while (t < t_stimDUR){
        /* Run the buzzer while:
           1. update the time
           2. check for licks
        */

        t = t_since(t_local);

        if (t_since(t_init) >= (t_stimONSET + t_rewardDEL) {
            count = count_responses(t_stimDUR - t, (trialType == 'N'));
        }

        if (lickOn and break_on_early) {
            Serial.print("#\tLick Detected");
            Serial.print("#Exit `TrialStimulus`:\t");
            Serial.println(t);
            return count;
        }
    }

    digitalWrite(stimulusPin, LOW); //this is a safety catch

    if (verbose) {
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
    }
    return count;
}
