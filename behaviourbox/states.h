/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/

int ActiveDelay(unsigned long wait, bool break_on_lick = false);

bool deliver_reward(bool water);

void punish(int del);

int Timeout(unsigned long wait, int depth = 0);

void preTrial();

int count_responses(int duration);

int TrialStimulus();

/*--------------------------------------------------------++
||                THE STATE FUNCTIONS                     ||
++--------------------------------------------------------*/


/*
pre_trial baseline
_noick period
stimulus
delay
response_period
_reward
*/


int ActiveDelay(unsigned long wait, bool break_on_lick) {

    unsigned long t_init = millis();
    unsigned long t = t_since(t_init);

    int count = 0;

    if (verbose) {
        Serial.print("#Enter `ActiveDelay`:\t");
        Serial.println(wait);
    }

    while (t < wait) {
        t = t_since(t_init);
        count += senseLick();

        if (break_on_lick and (count>=minlickCount)){
            if (verbose) { 
                Serial.print("#Exit `ActiveDelay`:\t");
                Serial.println(t);
            }
            return count;
        }
    }
    
    if (verbose) {
        Serial.print("#Exit `ActiveDelay`:\t");
        Serial.println(t);
    }
    return count;
}

bool deliver_reward(bool water) {
    /* Open the water port on `port` for a 
        duration defined by waterVol */
    if (water){    
        digitalWrite(waterPort, HIGH);
        delay(waterVol);
        digitalWrite(waterPort, LOW);
    }
    
    if (verbose) { 
        Serial.print("Water:");
        Serial.println(water);
    }
    return 1;
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
            if (depth == 2) {
                // don't record more than a couple of timeouts
                digitalWrite(bulbTrig, LOW);
            }
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

int count_responses(int duration, bool lickTrig) {
    
    /*
    Counts the number of hits on the lick sensor over `duration`
    of milliseconds.
    */

    int t0 = t_since(t_init);
    int t = t0;
    bool lick = 0;
    int count = 0;
    bool water = 0;

    if (verbose) {
        Serial.print("#Enter `count_responses`:\t");
        Serial.println(t);
    }

    while (t < (t0 + duration)) {
        t = t_since(t_init);
        lick = senseLick();
        count += lick;
        
        if ((count >= minlickCount) and (lickTrig) and (!water)){
            deliver_reward(1);
            water = 1;
        }
    }

    if (verbose) {
        Serial.print("#Exit `count_responses`:\t");
        Serial.println(t);
    }

    return count;
}

int TrialStimulus() {

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
    delay(t_stimDUR);
    digitalWrite(stimulusPin, LOW); //this is a safety catch

    if (verbose) {
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
    }
    return count;
}
