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

    unsigned long delay_init = millis();
    unsigned long t_local = t_since(delay_init);
    int count = 0;

    while (t_local < wait) {
        t_local = t_since(delay_init);
        count += senseLick();

        if (break_on_lick and (count >= lickCount)){
            return count;
        }
    }
    return count;
}

void deliver_reward(bool water) {
    /* Open the water port on `port` for a
        duration defined by waterVol */
    if (water){
        loggedWrite(waterPort, HIGH);
        delay(waterVol);
        loggedWrite(waterPort, LOW);
        conditional_tone(5000, 100);
    }
    reward = 1;
}

void punish(int del) {
    conditional_tone(20000, 100);
    loggedWrite(buzzerPin, HIGH);
    delay(del);
    loggedWrite(buzzerPin, LOW);
}

int Timeout(unsigned long wait, int depth) {

    unsigned long t_timeout = millis();
    unsigned long t_local = t_since(t_timeout);

   //delay(500); // Delay prevents punishing continued licking
    punish(500);

    while (t_local < wait) {
        t_local = t_since(t_timeout);

        if (senseLick()) {
            if (depth == 2) {
                // don't record more than a couple of timeouts
                loggedWrite(bulbTrig, LOW);
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
    loggedWrite(stimulusPin, stimulus?1:0);
    ActiveDelay(stimDUR);
    loggedWrite(stimulusPin, LOW);
    return;
}


void conditional_tone(int frequency, int duration) {
    // wrapper function so I don't need to put a billion if statements
    if (audio) {
        Send_time(speakerPin);
        tone(speakerPin, frequency, duration);
    }
}
