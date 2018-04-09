/*----------------------------------------------------------------------------++
||                         Serial Coms      version 4                         ||
++----------------------------------------------------------------------------*/

void printer(String name, String value) {
    Serial.println(name+':'+value);
}

void Send_status() {
    Serial.flush();
    printer("go_trial", String(go_trial));
    printer("somat_stim", String(somat_stim));
    printer("audit_stim", String(audit_stim));

    printer("response", String(response));
    printer("reward", String(reward));
    printer("N_timeouts", String(N_to));
    Send_stop();
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
    printer("audit_frequency", String(audit_frequency));

    printer("waterVol", String(waterVol));
    printer("lickWidth", String(lickWidth));
    printer("audio", String(audio));
    Send_stop();
}


void Send_time(byte chan) {

    unsigned int time = t_since(t_init);
    byte buff[3] = {0, 0, 0};

    buff[0] = chan;
    buff[1] = (time >>  0) & 255;
    buff[2] = (time >>  8) & 255;

    Serial.write(buff, 3);
}

void Send_stop() {

    byte stop[3] = {0, 0, 0};
    Serial.write(stop, 3);
}

void loggedWrite(byte pin, bool state) {
    byte chan = state? pin : -pin;
    digitalWrite(pin, state);
    Send_time(chan);
}
