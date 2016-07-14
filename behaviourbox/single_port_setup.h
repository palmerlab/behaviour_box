char Habituation_single();

char TrialReward_single();

char runTrial_single();


char runTrial_single() { 

    // returns 0 if the stimulus was applied
    // returns 1 if a timeout is required
    // until next trial

    // local variables and initialisation of the trial
    /* t_init is initialised such that t_now
       returns 0 at the start of the trial, and 
       increases from there. */ 
    unsigned long t;
    int response_time = 0;
    char response = 0;

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

    if ((response == 'G') and t_noLickPer){

        response = 'e';

        //punish(150);

        Serial.print("response:\t");
        Serial.println(response);
        Serial.print("response_time:\t");
        Serial.println(t_now(t_init));

        Serial.println("count[0]:\tnan");
        Serial.println("count[1]:\tnan");
        Serial.println("t_stimDUR:\tnan");

        return response;
    }

    t = t_now(t_init);

    TrialStimulus(break_on_early);
    t = t_now(t_init);

    // TODO include contingency to report on lick early without breaking?
    ActiveDelay(t + t_rewardDEL, false);
    t = t_now(t_init);

    /* this is a little complicated:
       1. TrialReward returns 0 if break_wrongChoice is set.
          therefore if TrialReward is false, the incorrect
          sensor was tripped during the reward period. A 
          bad tone is played; and the function returns, 
          resetting the program
    */

    response = TrialReward_single();

    if (response) {
        response_time = t_now(t_init);
    }
    else {
        response = '-';
    }
    
    Serial.print("response:\t");
    Serial.println(response);
    Serial.print("response_time:\t");
    Serial.println(response_time);

    Serial.print("t_stimDUR:\t");
    Serial.println(t_stimDUR);

    return response;
}

char Habituation_single(){

    bool port = 0;
    t_init = millis();

    // Check the lick sensor
    char response = get_response_single();

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





char TrialReward_single() {
    /* 
    returns a character:
            ---- --------------------------------------
             'L' correct hit on left port
             'R' correct hit on right port
             'l' incorrect lick on left port
             'r' incorrect lick on right port
             '-' unknown
             'M' No lick detected during reward period
            ---- --------------------------------------  
    */

    int t0 = t_now(t_init);
    int t = t0;
    bool RewardTest = 0;
    bool RewardPort = lick_port;
    char response = 0;
    byte count = 0;
    int N_to; //number of timeouts

    if (verbose) {
        Serial.print("#Enter `TrialReward`:\t");
        Serial.println(t);
    }

    while (t < t0 + t_rewardDUR) {

        t = t_now(t_init);

        get_response();

        count = count + lickOn[lick_port];

        // response reports if there was a lick in the reward period

        if ((count >= minlickCount) and (rewardCond == 'B')) {
            /* This next block opens the water port on the 
            correct side and returns the response */
            digitalWrite(waterPort[lick_port], HIGH);

            if (verbose) { 
                Serial.print("WaterPort[");

                Serial.print(RewardPort);
                Serial.print("]:\t");
                Serial.println("1");
            }

            delay(waterVol);
            digitalWrite(waterPort[lick_port], LOW);

            /* set the response to be returned based on
               the value received. The response is queried first,
               making sure that a response hasn't been set. If
               a response has already been recorded, the first
               response stands as the one reported.
               Also play the associated reward tone */

            if ((rewardCond == 'B')){ // hit
                response = 'H';
                tone(speakerPin, toneGood, 50);
            }

            if (verbose) { 
                Serial.print("count:\t");
                Serial.println(count);

                Serial.print("#Exit `TrialReward`:\t");
                Serial.println(t);
            }

            // pause for 1.5s to allow for drinking
            ActiveDelay(t + 1500, false);

            return response;
        }
        else if ((count >= minlickCount)){

            // declare the fail condition??

            response = 'f'; // bad left

            if (!response) {
                punish(150);
            }

            if (break_wrongChoice){
                if (timeout) {
                    N_to = Timeout(timeout); //count the number of timeouts                 
                    Serial.print("N_timeouts:\t");
                    Serial.println(N_to);
                }
                if (verbose) { 
                    Serial.print("count:\t");
                    Serial.println(count);
                    
                    Serial.print("#Exit `TrialReward`:\t");
                    Serial.println(t);
                }
                return response;
            }
        }

        digitalWrite(waterPort[left], LOW);
        digitalWrite(waterPort[right], LOW);
       //safety catch
    }

    // miss 
    if (verbose) { 
        Serial.print("count:\t");
        Serial.println(count);

        Serial.print("#Exit `TrialReward`:\t");
        Serial.println(t);
    }
    return response;
}