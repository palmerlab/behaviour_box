void Habituation();

char TrialReward();

char runTrial();

int count_responses(int duration);

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
    float pre_count = 0;                  //number of licks
    float post_count = 0;                  //number of licks
    int delta = 0;
    int N_to;                       //number of timeouts

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
    
    // wait 
    //ActiveDelay(t_stimONSET - t_rewardDUR, false);
    pre_count = (float) count_responses(t_stimONSET) / ((float) t_stimONSET / 1000);

    if (response and t_noLickPer){

        response = 'e';

        Serial.print("response:\t");
        Serial.println(response);

        Serial.println("delta:\tnan");
        Serial.println("post_count:\tnan");
        Serial.println("pre_count:\tnan");
        Serial.println("t_stimDUR:\tnan");

        return response;
    }

    t = t_since(t_init);

    post_count = (float) TrialStimulus(break_on_early);
    t = t_since(t_init);


    //tone(speakerPin, toneGood, 50);
    
    ActiveDelay(t_rewardDEL, false);
    
    
    t = t_since(t_init);
    post_count += (float) count_responses(t_rewardDUR);
    
    post_count = post_count / ((float) t_rewardDUR / 1000);
    
    delta = post_count - pre_count;
    
    while (t < t_trialDUR){
        t = t_since(t_init);
    }
    
    if (trialType == 'G') {
        if (post_count >= minlickCount) {
            deliver_reward();
            response = 'H';
        }
        else {
            response = '-';
            Serial.println("Water:\t0");
        }
    }
    else if (trialType == 'N'){
        if (delta >= minlickCount) {
            punish(200);
            response = 'f';
            Serial.println("Water:\t0");

            /*
            In the event that we are in the trial stimulus I want
            the punishment delay not to blow out the stimulus.
            The arithmetic reduces the punish time according to 
            the stimulus end
            */

            if (timeout) {
                N_to = Timeout(timeout); //count the number of timeouts
                Serial.print("N_timeouts:\t");
                Serial.println(N_to);
            }
            
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
    
    Serial.print("delta:\t");
    Serial.println(delta);
    
    Serial.print("pre_count:\t");
    Serial.println(pre_count);
    
    Serial.print("post_count:\t");
    Serial.println(post_count);
    
    Serial.print("t_stimDUR:\t");
    Serial.println(t_stimDUR);

    return response;
}

void Habituation(){

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

int count_responses(int duration) {
    
    /*
    Counts the number of hits on the lick sensor over `duration`
    of milliseconds.
    
    */

    int t0 = t_since(t_init);
    int t = t0;
    bool lick = 0;
    int count = 0;

    if (verbose) {
        Serial.print("#Enter `count_responses`:\t");
        Serial.println(t);
    }

    while (t < (t0 + duration)) {

        t = t_since(t_init);
        lick = senseLick();
        count += lick;
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
    delay(t_stimDUR);
    digitalWrite(stimulusPin, LOW); //this is a safety catch

    if (verbose) {
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
    }
    return count;
}
