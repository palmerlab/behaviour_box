/*----------------------------------------------------------------------------++
||                         Serial Coms      version 4                         ||
++----------------------------------------------------------------------------*/

void printer(String name, String value) {
    Serial.println(name+':'+value);
}

void Send_status() {

    printer("stimulus", String(stimulus));
    printer("light_stim", String(light_stim));
    printer("light_resp", String(light_resp));

    printer("response", String(response));
    printer("reward", String(reward));
    printer("N_timeouts", String(N_to));
}

void Send_params() {

    printer("lickThres", String(lickThres));
    printer("timeout", String(timeout));
    printer("lickCount", String(lickCount));
    printer("lickTrigReward", String(lickTrigReward));

    printer("noLickDUR", String(noLickDUR));
    printer("stimONSET", String(stimONSET));
    printer("stimDUR", String(stimDUR));
    printer("respDEL", String(respDEL));
    printer("respDUR", String(respDUR));
    printer("trialDUR", String(trialDUR));

    printer("waterVol", String(waterVol));
    printer("lickWidth", String(lickWidth));
    printer("audio", String(audio));
}


void Send_time(byte chan) {

    unsigned long time = t_since(t_init);
    byte buff[3] = {0, 0, 0};

    buff[0] = (chan >>  0) & 255;
    buff[1] = (time >>  8) & 255;
    buff[2] = (time >> 16) & 255;

    Serial.write(buff, 3);
}

void Send_stop() {

    byte stop[3] = {0, 0, 0};
    Serial.write(stop, 3);
}

void loggedWrite(byte pin, bool state) {
    byte chan = (-1 * state) * pin;
    digitalWrite(pin, state);
    Send_time(chan);
}
