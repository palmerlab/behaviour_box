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
        Serial.print("#\tfrequency:\t");
        Serial.println(frequency);
        if (not frequency){
            Serial.print("#Exit `TrialStimulus`:\t");
            Serial.println(t);
            return count;
        }
        //flutter code HERE
        if (frequency == 200) { // do flutter 1 for 500ms

          digitalWrite(stimulusPin, HIGH);
          delay(500);
          digitalWrite(stimulusPin,LOW);
         
        }

        else if (frequency == 20) {// do flutter 2 for 500ms

          int high_in_millisecond = 15;  // how long 5V is sent (in ms)
          int low_in_millisecond = 5; // how long 0V is sent (in ms)
          int nb_of_iterations = 25; // nb of pulse repetition

                for (int i=0; i < nb_of_iterations; i++){
                    digitalWrite(stimulusPin, HIGH);
                    delay(high_in_millisecond);
                    digitalWrite(stimulusPin, LOW);
                    delay(low_in_millisecond);
              }

        }
    if (verbose) {
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
    }
    return count;
}
}

void conditional_tone(int frequency, int duration) {
    // wrapper function so I don't need to put a billion if statements
    if (audio) {
        tone(speakerPin, frequency, duration);
    }
}
