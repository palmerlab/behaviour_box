/*--------------------------------------------------------++
||                   THE TRIAL MODES                      ||
++--------------------------------------------------------*/

void run_opto_trial(byte trial_code) {

    // flush all output variables
    unsigned long t;
    response = 0;     //
    pre_count0 = 0;   //
    pre_count1 = 0;   //
    pre_count = 0;    //
    post_count = 0;   //
    rew_count = 0;    //
    N_to = 0;         //
    reward = 0;       //

    // set the dynamic variables based on the trial code
    stimulus   = (trial_code >> 2) & 1;
    light_stim = (trial_code >> 1) & 1;
    light_resp = (trial_code >> 0) & 1;

    printer("stimulus", String(stimulus));
    printer("light_stim", String(light_stim));
    printer("light_resp", String(light_resp));

    /* -----------------------------------------------------------------------
    ||                         START OF THE TRIAL
    ++-----------------------------------------------------------------------*/
    t_init = millis();
    t = t_since(t_init);

    // wait
    pre_count0 += ActiveDelay(noLickDUR, false);
    t = t_since(t_init);
    pre_count1 += ActiveDelay(stimONSET - t, (noLickDUR>0));
    t = t_since(t_init);

    // Break out on early lick
    if ((pre_count1>0) and noLickDUR){
        response = 'e';
        return;
    }

    pre_count = pre_count0+pre_count1;

    t = t_since(t_init);

    /* -----------------------------------------------------------------------
    ||                            STIMULUS
    ++-----------------------------------------------------------------------*/

    digitalWrite(lightPin, light_stim?1:0);
    TrialStimulus();
    digitalWrite(lightPin, LOW);
    t = t_since(t_init);

    /* -----------------------------------------------------------------------
    ||                         POST STIM DELAY
    ++-----------------------------------------------------------------------*/

    ActiveDelay(respDEL, false);

    /* -----------------------------------------------------------------------
    ||                        RESPONSE PERIOD
    ++-----------------------------------------------------------------------*/

    digitalWrite(lightPin, light_resp?1:0);
    conditional_tone(7000, 100);

    t = t_since(t_init);

    post_count += ActiveDelay(respDUR, lickTrigReward);

    if ((t_since(t_init) - t) < respDUR) {
      // keeps counting even if the reward was triggered already
        deliver_reward(lickTrigReward and (stimulus));
        response = 1;
        rew_count += ActiveDelay((respDUR - (t_since(t_init) - t)) , 0);
    }

    if (stimulus){
        if (response) {
            response = 'H';
        }
        else if (post_count >= lickCount) {
            response = 'H';
            deliver_reward(1);
        }
        else {
            response = '-';
        }
    }
    else {
        if (post_count >= lickCount) {
            response = 'f';
            punish(200);

            if (timeout) {
                N_to = Timeout(timeout); //count the number of timeouts
            }
        }
        else {
            response = 'R';
            deliver_reward(reward_nogo);
        }
    }

    digitalWrite(lightPin, LOW);

    /* -----------------------------------------------------------------------
    ||                    POST RESPONSE BASELINE
    ++-----------------------------------------------------------------------*/

    //continue trial till end (for the bulb trigger)
    t = t_since(t_init);
    if (t < trialDUR){
        rew_count += ActiveDelay((trialDUR - t), 0);
    }

    digitalWrite(bulbTrig, LOW);
    digitalWrite(recTrig, LOW);

    /* -----------------------------------------------------------------------
    ||                             END TRIAL
    ++-----------------------------------------------------------------------*/

    return;
}
