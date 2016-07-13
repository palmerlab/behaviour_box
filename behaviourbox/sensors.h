char get_response();

bool senseLick(bool sensor);

char get_response(){

    char response = 0;

    senseLick(lick_port_L);
    senseLick(lick_port_R);

    if (lickOn[lick_port_L] 
        and lickOn[lick_port_R]) {
        response = 'B'; // could happen?
    }
    else if (lickOn[lick_port_L]){
        response = 'L';
    }
    else if (lickOn[lick_port_R]){
        response = 'R';
    }
    else {
        // set the response to nothing if there was none
        response = '-';
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

