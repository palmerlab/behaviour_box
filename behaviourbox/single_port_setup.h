char Habituation_single();

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
