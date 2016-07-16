char Habituation();

char TrialReward();

char runTrial();

byte count_responses(int duration, bool no_go = false);


char runTrial() { 

    // returns 0 if the stimulus was applied
    // returns 1 if a timeout is required
    // until next trial

    // local variables and initialisation of the trial
    /* t_init is initialised such that t_now
       returns 0 at the start of the trial, and 
       increases from there. */ 
    unsigned long t;
    char response = 0;
    byte count = 0;

    // local time
    t_init = millis() + trial_delay;
    t = t_now(t_init);

    /*trial_phase0
    while the trial has not started 
       1. update the time
       2. check for licks
       3. trigger the recording by putting recTrig -> HIGH
    */

    preTrial();
    t = t_now(t_init);

    ActiveDelay(t_noLickPer, false);
    t = t_now(t_init);

    response = ActiveDelay(t_stimONSET, t_noLickPer);

    if ((response != '-') and t_noLickPer){

        response = 'e';

        Serial.print("response:\t");
        Serial.println(response);

        Serial.println("count:\tnan");
        Serial.println("t_stimDUR:\tnan");

        return response;
    }

    t = t_now(t_init);

    TrialStimulus(break_on_early);
    t = t_now(t_init);

    ActiveDelay(t_stimONSET + t_rewardDEL, false);
    t = t_now(t_init);

    //tone(speakerPin, toneGood, 50);
    count = count_responses(t_rewardDUR, (trialType == 'N'));
    
    if (trialType == 'G') {
        if (count >= minlickCount) {
            deliver_reward(lick_port, waterVol);
            response = 'H';
        }
        else {
            response = '-';
        }
    }
    else if (trialType == 'N'){
        if (count >= minlickCount) {
            response = 'f';
        }
        else {
            response = 'R';
        }
    }
    else {
        response = '?';
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

    bool port = 0;
    t_init = millis();

    // Check the lick sensor
    char response = get_response();

    if (response == 'G') {

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
        deliver_reward(port, waterVol);

        ActiveDelay(3500u, false);

        /* Output should allow me to make the following table:
            stim0   stim1   response
            ------- ------- --------
        */

        Serial.print("t_stimDUR:\t");
        Serial.println(t_stimDUR);
        Serial.print("response:\t");
        Serial.println(response);
        Serial.print("reward_count:\t");
        Serial.println(int(reward_count[port]));

        Serial.println("-- Status: Ready --");
    }

    return response;
}

byte count_responses(int duration, bool no_go) {

    int t0 = t_now(t_init);
    int t = t0;
    byte count = 0;
    char response = 0;
    int N_to; //number of timeouts

    if (verbose) {
        Serial.print("#Enter `count_responses`:\t");
        Serial.println(t);
    }

    while (t < t0 + duration) {

        t = t_now(t_init);
        response = get_response();
        count = count + lickOn[lick_port];

        if ((break_wrongChoice) and (response != '-') and (no_go)){
            punish(1500);
    
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
            return response;
        }
    }
    
    if (verbose) {
        Serial.print("#Exit `count_responses`:\t");
        Serial.println(t);
    }
    
    return count;
}
