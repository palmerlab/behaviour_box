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
        t_local = t_since(delay_init);

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
        reward = 1;
    }
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
    loggedWrite(lightPin, LOW);

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


void TrialStimulus() {
    // turn the stimulus on only if it should go ON
    if (audit_stim) {do_audit_stim();}
    else if (somat_stim) {do_somat_stim();}
    else {ActiveDelay(stimDUR);}
    return;
}

void do_somat_stim() {
    // turn the stimulus on only if it should go ON
    loggedWrite(stimulusPin, HIGH);
    ActiveDelay(stimDUR);
    loggedWrite(stimulusPin, LOW);
    return;
}

void do_audit_stim() {
    // turn the stimulus on only if it should go ON

    Send_time(speakerPin);
    tone(speakerPin, audit_frequency, stimDUR);
    ActiveDelay(stimDUR);
    Send_time(-speakerPin);
    return;
}


void conditional_tone(int frequency, int duration) {
    // wrapper function so I don't need to put a billion if statements
    if (audio) {

        Send_time(speakerPin);
        tone(speakerPin, frequency, duration);
        Send_time(-speakerPin);
    }
}
