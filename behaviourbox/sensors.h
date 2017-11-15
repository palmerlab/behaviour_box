bool senseLick() {
    // 1. check to see if the lick sensor has moved:
    //     if the sensor was in a low state, allow the calling of a rising edge.
    // 2. check if the sensor is above threshold
    // 3. report if the state of lickOn has change

    bool lick = false; // Who You Gonna Call?

    if (analogRead(lickSens) >= lickThres){
        delay(lickWidth);
        lick = (analogRead(lickSens) >= lickThres);
    }
    // if the sensor was off, and now it is on, return 1
    if (lick) {
        conditional_tone(10000, 5);
        Send_time(lickSens);
    }
    return (lick);
}
