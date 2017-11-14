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

    while (t < wait) {
        t = t_since(t_init);
        count += senseLick();

        if (break_on_lick and (count>=lickCount)){
            return count;
        }
    }
    return count;
}

void deliver_reward(bool water) {
    /* Open the water port on `port` for a
        duration defined by waterVol */
    if (water){
        digitalWrite(waterPort, HIGH);
        delay(waterVol);
        digitalWrite(waterPort, LOW);
        conditional_tone(5000, 100);
    }
    reward = 1;
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

    while (t < (t0 + duration)) {
        t = t_since(t_init);
        lick = senseLick();
        count += lick;

        if ((count >= lickCount) and (lickTrig) and (!water)){
            deliver_reward(1);
            water = 1;
        }
    }

    return count;
}

void TrialStimulus() {

    // turn the stimulus on only if it should go ON
    if (stimDUR) { digitalWrite(stimulusPin, HIGH); }
    delay(stimDUR);
    digitalWrite(stimulusPin, LOW);
    return;
}


void conditional_tone(int frequency, int duration) {
    // wrapper function so I don't need to put a billion if statements
    if (audio) {
        tone(speakerPin, frequency, duration);
    }
}
