/*--------------------------------------------------------++
||                   THE TRIAL MODES                      ||
++--------------------------------------------------------*/

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
    int pre_count0 = 0;                   //number of licks
    int pre_count1 = 0;                   //number of licks
    int pre_count = 0;                   //number of licks
    int post_count = 0;                  //number of licks
    int rew_count = 0;
    int N_to;                              //number of timeouts
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
    pre_count0 += ActiveDelay(t_noLickPer, false);
    t = t_since(t_init);
    pre_count1 += ActiveDelay(t_stimONSET - t, (t_noLickPer>0));
    t = t_since(t_init);

    // Break out on early lick
    if ((pre_count1>0) and t_noLickPer){

        response = 'e';

        Serial.print("\tresponse:");
        Serial.println(response);

        Serial.println("\tpost_count:nan");
        Serial.println("\tpre_count:nan");
        Serial.println("\trew_count:nan");
        Serial.println("\tt_stimDUR:nan");

        return response;
    }

    pre_count = pre_count0+pre_count1;

    t = t_since(t_init);

    post_count = TrialStimulus();
    t = t_since(t_init);

    ActiveDelay(t_rewardDEL, false);

    conditional_tone(7000, 100);

    t = t_since(t_init);
    post_count += ActiveDelay(t_rewardDUR, lickTrigReward);

    if ((t_since(t_init) - t) < t_rewardDUR) {
      // keeps counting even if the reward was triggered already
        deliver_reward(lickTrigReward and (trialType == 'G'));
        response = 1;
        rew_count += ActiveDelay((t_rewardDUR - (t_since(t_init) - t)) , 0);
    }
    if (trialType == 'G'){
        if (response) {
            response = 'H';
        }
        else if (post_count >= minlickCount) {
            response = 'H';
            deliver_reward(1);
        }
        else {
            response = '-';
            deliver_reward(0);
        }
    }
    else if (trialType == 'N') {
        if (post_count >= minlickCount) {
            response = 'f';
            punish(200);
            deliver_reward(0);

            if (timeout) {
                N_to = Timeout(timeout); //count the number of timeouts
                Serial.print("\tN_timeouts:");
                Serial.println(N_to);
            }
        }
        else {
            response = 'R';
            deliver_reward(reward_nogo);
        }
    }
    else {
            response = '?';
            deliver_reward(0);
    }//switch

    //continue trial till end (for the bulb trigger)
    t = t_since(t_init);
    if (t < t_trialDUR){
        rew_count += ActiveDelay((t_trialDUR - t), 0);
    }

    Serial.print("\tresponse:");
    Serial.println(response);

    Serial.print("\tpre_count:");
    Serial.println(pre_count);

    Serial.print("\tpost_count:");
    Serial.println(post_count);

    Serial.print("\trew_count:");
    Serial.println(rew_count);

    Serial.print("\tt_stimDUR:");
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
        TrialStimulus();
        deliver_reward(1);

        ActiveDelay(3500u, false);

        /* Output should allow me to make the following table:
            stim0   stim1   response
            ------- ------- --------
        */

        Serial.print("\tt_stimDUR:");
        Serial.println(t_stimDUR);
        Serial.print("\treward_count:");
        Serial.println(int(reward_count));

        Serial.println("-- Status: Ready --");
    }
}
