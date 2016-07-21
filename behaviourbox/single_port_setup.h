char Habituation();

char TrialReward();

char runTrial();

int count_responses(int duration, bool no_go = false);

int TrialStimulus(bool break_on_early);

char runTrial() { 

    // returns 0 if the stimulus was applied
    // returns 1 if a timeout is required
    // until next trial

    // local variables and initialisation of the trial
    /* t_init is initialised such that t_since
       returns 0 at the start of the trial, and 
       increases from there. */ 
    unsigned long t;
    char response = 0;
    int count = 0;

    // local time
    t_init = millis() + trial_delay;
    t = t_since(t_init);

    /*trial_phase0
    while the trial has not started 
       1. update the time
       2. check for licks
       3. trigger the recording by putting recTrig -> HIGH
    */

    preTrial();
    t = t_since(t_init);

    ActiveDelay(t_noLickPer, false);
    t = t_since(t_init);

    response = ActiveDelay(t_stimONSET, t_noLickPer);

    if (response and t_noLickPer){

        response = 'e';

        Serial.print("response:\t");
        Serial.println(response);

        Serial.println("count:\tnan");
        Serial.println("t_stimDUR:\tnan");

        return response;
    }

    t = t_since(t_init);

    count = TrialStimulus(break_on_early);
    t = t_since(t_init);

    ActiveDelay(t_stimONSET + t_rewardDEL, false);
    t = t_since(t_init);

    //tone(speakerPin, toneGood, 50);
    count = count + count_responses(t_rewardDUR, (trialType == 'N'));

    if (trialType == 'G') {
        if (count >= minlickCount) {
            deliver_reward();
            response = 'H';
        }
        else {
            response = '-';
            Serial.println("Water:\t0");
        }
    }
    else if (trialType == 'N'){
        if (count >= minlickCount) {
            response = 'f';
            Serial.println("Water:\t0");
        }
        else {
            response = 'R';
            Serial.println("Water:\t0");
        }
    }
    else {
        response = '?';
        Serial.println("Water:\t0");
    }


    Serial.print("response:\t");
    Serial.println(response);
    
    Serial.print("count:\t");
    Serial.println(count);
    
    Serial.print("t_stimDUR:\t");
    Serial.println(t_stimDUR);

    return response;
}

char Habituation(){

    t_init = millis();

    // Check the lick sensor
    if (senseLick()) {

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

        // stim0, stim1, reward...
        TrialStimulus(0);
        deliver_reward();

        ActiveDelay(3500u, false);

        /* Output should allow me to make the following table:
            stim0   stim1   response
            ------- ------- --------
        */

        Serial.print("t_stimDUR:\t");
        Serial.println(t_stimDUR);
        Serial.print("reward_count:\t");
        Serial.println(int(reward_count));

        Serial.println("-- Status: Ready --");
    }
}

int count_responses(int duration, bool no_go) {

    int t0 = t_since(t_init);
    int t = t0;
    int count = 0;
    bool lick = 0;
    int N_to; //number of timeouts

    if (verbose) {
        Serial.print("#Enter `count_responses`:\t");
        Serial.println(t);
    }

    while (t < (t0 + duration)) {

        t = t_since(t_init);
        lick = senseLick();
        count = count + lick;

        if (break_wrongChoice and (count >= minlickCount) and no_go) {
            
            punish(500);
    
            if (timeout) {
                N_to = Timeout(timeout); //count the number of timeouts                 
                Serial.print("N_timeouts:\t");
                Serial.println(N_to);
            }
            if (verbose) { 
                Serial.print("count:\t");
                Serial.println(count);
                
                Serial.print("#Exit `count_responses`:\t");
                Serial.println(t);
            }
            return count;
        }
    }
    
    if (verbose) {
        Serial.print("#Exit `count_responses`:\t");
        Serial.println(t);
    }
    
    return count;
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

        if (t_since(t_init) >= (t_stimONSET + t_rewardDEL)) {
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
