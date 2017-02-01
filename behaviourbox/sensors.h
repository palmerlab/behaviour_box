bool senseLick() {
    // 1. check to see if the lick sensor has moved:
    //     if the sensor was in a low state, allow the calling of a rising edge.
    // 2. check if the sensor is above threshold
    // 3. report if the state of lickOn has change
    
    bool CallSpike = false; // Who You Gonna Call?
    bool spike = false;
    
    if (lickOn == false) { 
        CallSpike = true;
    }
    
    if (analogRead(lickSens) >= lickThres){
        delay(debounce);
        lickOn = (analogRead(lickSens) >= lickThres);
    }
    
    else {
        lickOn = false;
    }
    // if the sensor was off, and now it is on, return 1
    spike = CallSpike and lickOn;
    if (spike) {
        conditional_tone(10000, 5);
    }
    
    return (spike);
}

