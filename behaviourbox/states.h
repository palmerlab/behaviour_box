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

int ActiveDelay(unsigned long wait, bool break_on_lick,
                                  bool print_resp_time ) {

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

        if (print_resp_time  and (count>=minlickCount)){
            Serial.print("response_time:\t");
            Serial.println(t);
        }

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
        conditional_tone(5000, 100);
    }

    if (verbose) {
        Serial.print("Water:");
        Serial.println(water);
    }
    return 1;
}

void punish(int del) {

    conditional_tone(20000, 100);
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

    digitalWrite(recTrig, LOW);

    if (verbose) {
        Serial.print("#Exit `preTrial`:\t");
        Serial.println(t);
    }
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


void conditional_tone(int frequency, int duration) {
    // wrapper function so I don't need to put a billion if statements
    if (audio) {
        tone(speakerPin, frequency, duration);
    }
}
