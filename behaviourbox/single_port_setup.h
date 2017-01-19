/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/

void Habituation();

char runTrial();

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
    float pre_count = 0;                   //number of licks
    float post_count = 0;                  //number of licks
    int delta = 0;
    int N_to;                              //number of timeouts
    bool water = 0;                        //internal flag to 

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
    pre_count = count_responses(t_stimONSET, 0);
    //pre_count = (float) pre_count / ((float) t_stimONSET / 1000);

    if (response and t_noLickPer){

        response = 'e';

        Serial.print("\tresponse:");
        Serial.println(response);

        Serial.println("\tdelta:nan");
        Serial.println("\tpost_count:nan");
        Serial.println("\tpre_count:nan");
        Serial.println("\tt_stimDUR:nan");

        return response;
    }

    t = t_since(t_init);

    post_count = TrialStimulus();
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
            Serial.print("\tWater:");
            Serial.println(water);
        }
    }
    else if (trialType == 'N'){
        if (delta >= minlickCount) {
            punish(200);
            response = 'f';
            Serial.print("\tWater:");
            Serial.println(water);

            /*
            In the event that we are in the trial stimulus I want
            the punishment delay not to blow out the stimulus.
            The arithmetic reduces the punish time according to 
            the stimulus end
            */

            if (timeout) {
                N_to = Timeout(timeout); //count the number of timeouts
                Serial.print("\tN_timeouts:");
                Serial.println(N_to);
            }
        }
        else {
            response = 'R';
            Serial.print("\tWater:");
            Serial.println(water);
        }
    }
    else {
        response = '?';
        Serial.print("\tWater:");
        Serial.println(water);
    }

    Serial.print("\tresponse:");
    Serial.println(response);
    
    Serial.print("\tdelta:");
    Serial.println(delta);
    
    Serial.print("\tpre_count:");
    Serial.println(pre_count);
    
    Serial.print("\tpost_count:");
    Serial.println(post_count);
    
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
        TrialStimulus(0);
        deliver_reward();

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
