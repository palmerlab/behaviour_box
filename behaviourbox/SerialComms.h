/*----------------------------------------------------------------------------++
||                         Serial Coms      version 4                         ||
++----------------------------------------------------------------------------*/

void printer(String name, String value){
  Serial.println(name+':'+value);
}

void Send_status() {

  printer("response", String(response));
  printer("pre_count", String(pre_count));
  printer("post_count", String(post_count));
  printer("rew_count", String(rew_count));
  printer("stimDUR", String(stimDUR));
  printer("reward", String(reward));
  printer("N_timeouts", String(N_to));
}

void Send_params() {

    printer("lickThres", String(lickThres));
    printer("timeout", String(timeout));
    printer("reward_nogo", String(reward_nogo));
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
