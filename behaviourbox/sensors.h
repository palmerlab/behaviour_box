char get_response();
//char get_response_dual();
//char get_response_single();

bool senseLick(bool sensor);


char get_response(){
    /*
    Returns either:
        -`'G'` for a lick (as in 'Go')
        - or `'-'` for no response
    */

    char response = '-';

    senseLick(lick_port);

    if (lickOn[lick_port]){
        response = 'G';
    }

    return response;
}


bool senseLick(bool sensor) {
    // 1. check to see if the lick sensor has moved
    // 2. check if the sensor is above threshold
    // 3. report if the state of lickOn has change

    bool CallSpike = false; // Who You Gonna Call?

    if (lickOn[sensor] == false) { 
        CallSpike = true;
        // counted = true
    }

    if (analogRead(lickSens[sensor]) >= lickThres){
        lickOn[sensor] = true;
    }
    else {
        lickOn[sensor] = false;
    }
    // if the sensor was off, and now it is on, return 1
    return (CallSpike and lickOn[sensor]);
}

