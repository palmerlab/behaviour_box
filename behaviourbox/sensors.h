bool senseLick() {
    // 1. check to see if the lick sensor has moved:
    //     if the sensor was in a low state, allow the calling of a rising edge.
    // 2. check if the sensor is above threshold
    // 3. report if the state of lickOn has change

    bool CallSpike = false; // Who You Gonna Call?

    if (lickOn == false) {
        CallSpike = true;
    }

    if (analogRead(lickSens) >= lickThres){
        delay(lickWidth);
        lickOn = (analogRead(lickSens) >= lickThres);
    }

    else {
        lickOn = false;
    }
    // if the sensor was off, and now it is on, return 1
    if (CallSpike and lickOn) {
        conditional_tone(10000, 5);
        Serial.write(long(t_since(t_init)));
    }
    return (spike);
}
