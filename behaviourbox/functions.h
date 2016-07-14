/* -------------------------------------------------------++
||                  THE PROTOTYPES                        ||
++--------------------------------------------------------*/

void init_trial(char trialType);

char Habituation();

char ActiveDelay(unsigned long wait, bool break_on_lick = false);

void deliver_reward(bool port, char waterVol);

void punish(int del);

int Timeout(unsigned long wait, int depth = 0);
    
bool TrialStimulus(bool break_on_early);

void preTrial();

char TrialReward();

char runTrial();

/*--------------------------------------------------------++
||                  THE FUNCTIONS                         ||
++--------------------------------------------------------*/

void init_trial(char trialType){
    // This function sets the right and left
    // stimulus intensities to the same or different
    // depending on the value of `right_same`

    if (trialType == 'G'){
        rewardCond = 'B';
    }
    else if (trialType == 'N') {
        rewardCond = '-';
    }
    else {
        t_stimDUR = 0;
    }
}

char ActiveDelay(unsigned long wait, bool break_on_lick) {

    unsigned long t = t_now(t_init);

    char response = 0;

    if (verbose) {
        Serial.print("#Enter `ActiveDelay`:\t");
        Serial.println(t);
    }

    while (t < wait) {
        t = t_now(t_init);

        response = (response == '-')? response : get_response();

        if (break_on_lick and (response != '-')){
            if (verbose) { 
                Serial.print("#Exit `ActiveDelay`:\t");
                Serial.println(t);
            }
            return response;
        }
    }

    if (verbose) {
        Serial.print("#Exit `ActiveDelay`:\t");
        Serial.println(t);
    }

    return response;
}

void deliver_reward(bool port, char waterVol) {
    /* Open the water port on `port` for a 
        duration defined by waterVol */

    digitalWrite(waterPort[port], HIGH);
    delay(waterVol);
    digitalWrite(waterPort[port], LOW);
}

void punish(int del){

    digitalWrite(buzzerPin, HIGH);
    delay(del);
    digitalWrite(buzzerPin, LOW);
}

int Timeout(unsigned long wait, int depth) {

    unsigned long t_init = millis();
    unsigned long t = t_now(t_init);

   //delay(500); // Delay prevents punishing continued licking
    punish(150);

    while (t < wait) {
        t = t_now(t_init);

        if (get_response() != '-') {
            if (depth < 10) {
                depth ++;
                depth = Timeout(wait, depth);
                break;
            }
        }
    }
    return depth;
}

void preTrial() {   
    /* while the trial has not started 
       1. update the time
       2. check for licks
       4. trigger the recording by putting recTrig -> HIGH
    */
    long t = t_now(t_init);

    if (verbose) {
        Serial.print("#Enter `preTrial`:\t");
        Serial.println(t);
    }

    while (t < 0){
        // 1. update time
        // 2. check for licks
        t = t_now(t_init);

        if (t%1000 < 20){
            digitalWrite(statusLED, HIGH);
        }
        else {
            digitalWrite(statusLED, LOW);
        }

        // 3. trigger the recording
        if (t > -10){
            digitalWrite(recTrig, HIGH);
            digitalWrite(bulbTrig, HIGH);
        }
    }

    digitalWrite(recTrig, LOW);

    if (verbose) {
        Serial.print("#Exit `preTrial`:\t");
        Serial.println(t);
    }
} 

bool TrialStimulus(bool break_on_early) {

    int t_local = millis();
    int t = t_now(t_local);

    // TODO this should be abstracted

    if (verbose) {
        // TODO make verbosity a scale instead of Boolean
        Serial.print("#Enter `TrialStimulus`:\t");

        Serial.println(t_now(t_init));
        
        Serial.print("#\tt_stimDUR:\t");
        Serial.println(t_stimDUR);
    }

    if (not t_stimDUR){
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
        return 0;
        
    }
    digitalWrite(stimulusPin, HIGH);
    
    while (t < t_stimDUR){
        /* Run the buzzer while:
           1. update the time
           2. check for licks
        */

        get_response();

        t = t_now(t_local);

        if ((lickOn[lick_port_L] or lickOn[lick_port_R])
                and break_on_early) {
            Serial.print("#\tLick Detected");
            Serial.print("#Exit `TrialStimulus`:\t");
            Serial.println(t);
            return 0;
        }
    }

    digitalWrite(stimulusPin, LOW); //this is a safety catch

    if (verbose) {
        Serial.print("#Exit `TrialStimulus`:\t");
        Serial.println(t);
    }
    return 1;
}

char TrialReward() {
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
    bool RewardPort = 0;
    char response = 0;
    byte count[] = {0,0};
    int N_to; //number of timeouts

    if (verbose) {
        Serial.print("#Enter `TrialReward`:\t");
        Serial.println(t);
    }

    while (t < t0 + t_rewardDUR) {

        t = t_now(t_init);

        get_response();

        count[left] = count[left] + lickOn[lick_port_L];
        count[right] = count[right] + lickOn[lick_port_R];

        // response reports if there was a lick in the reward period

        if (rewardCond == 'L') {
            RewardTest = (count[left] >= minlickCount);
            RewardPort = left;
        }
        else if (rewardCond ==  'R') {
            RewardTest = (count[right] >= minlickCount); 
            RewardPort = right;
        }
        else if (rewardCond == 'B') {
            RewardTest = (count[right] + count[left]) >= minlickCount;
            RewardPort = (count[right] > count[left]) ? right : left;
        }

        if (RewardTest) {
            /* This next block opens the water port on the 
            correct side and returns the response */
            digitalWrite(waterPort[RewardPort], HIGH);

            if (verbose) { 
                Serial.print("WaterPort[");

                Serial.print(RewardPort);
                Serial.print("]:\t");
                Serial.println("1");
            }

            delay(waterVol);
            digitalWrite(waterPort[RewardPort], LOW);

            /* set the response to be returned based on
               the value received. The response is queried first,
               making sure that a response hasn't been set. If
               a response has already been recorded, the first
               response stands as the one reported.
               Also play the associated reward tone */

            if ((rewardCond == 'L') or (rewardCond == 'B')){ // hit left
                response = !response? 'L': response;
                tone(speakerPin, toneGoodLeft, 50);
            }
            if ((rewardCond == 'R') or (rewardCond == 'B')){ // hit right
                response = !response? 'R': response;
                tone(speakerPin, toneGoodRight, 50);
            }

            if (verbose) { 
                Serial.print("count[0]:\t");
                Serial.println(count[left]);
                
                Serial.print("count[1]:\t");
                Serial.println(count[right]);
                
                Serial.print("#Exit `TrialReward`:\t");
                Serial.println(t);
            }

            // pause for 1.5s to allow for drinking
            ActiveDelay(t + 1500, false);

            return response;
        }
        else if ((count[0] >= minlickCount) or (count[1] >= minlickCount)){

            // declare the fail condition??

            if (RewardPort == left){
                response = 'r'; // bad right
            }
            else if (RewardPort == right){
                response = 'l'; // bad left
            }

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
                    Serial.print("count[0]:\t");
                    Serial.println(count[left]);
                    
                    Serial.print("count[1]:\t");
                    Serial.println(count[right]);
                    
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
        Serial.print("count[0]:\t");
        Serial.println(count[left]);

        Serial.print("count[1]:\t");
        Serial.println(count[right]);

        Serial.print("#Exit `TrialReward`:\t");
        Serial.println(t);
    }
    return response;
}

char runTrial() { 

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

    if ((response != '-') and t_noLickPer){

        if (response == 'L'){
            response = 'l';
        }
        if (response == 'R'){
            response = 'r';
        }

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
       1. check that there is a reward due, ie the condition
          is not `N`
       2. TrialReward returns 0 if break_wrongChoice is set.
          therefore if TrialReward is false, the incorrect
          sensor was tripped during the reward period. A 
          bad tone is played; and the function returns, 
          resetting the program
       3. Otherwise we wait until the trial period has ended
    */

    response = TrialReward();

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

char Habituation(){

    bool port = 0;
    t_init = millis();

    // Check the lick sensor
    char response = get_response();

    if (response != '-') {

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
        if (response == 'L') {
            port = left;
            reward_count[left] = (reward_count[left] < 10) ? reward_count[left] += 1 : 10;
            reward_count[right] = reward_count[right] ? reward_count[right] -= 1 : 0;
        }
        else if (response == 'R'){
            port = right;
            reward_count[right] = (reward_count[right] < 10) ? reward_count[right] += 1 : 10;
            reward_count[left] = reward_count[left] ? reward_count[left] -= 1 : 0;
        }

        // only activate if less than 10 in a row on this port
        if (reward_count[port] < 10) {
            
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
        }

        Serial.println("-- Status: Ready --");
    }

    return response;
}
