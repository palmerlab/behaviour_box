/*----------------------------------------------------------------------------++
||                       sensors.h                        ||
++----------------------------------------------------------------------------*/

bool senseLick();

/*----------------------------------------------------------------------------++
||                       states.h                         ||
++----------------------------------------------------------------------------*/

int ActiveDelay(unsigned long wait, bool break_on_lick = false);

void deliver_reward(bool water);

void punish(int del);

int Timeout(unsigned long wait, int depth = 0);

void preTrial();

int count_responses(int duration);

void TrialStimulus();

void conditional_tone(int frequency, int duration);

/*----------------------------------------------------------------------------++
||                 opto_simple.h                    ||
++----------------------------------------------------------------------------*/

void run_opto_trial(byte trial_code);

/*----------------------------------------------------------------------------++
||                         Serial Coms      version 4                         ||
++----------------------------------------------------------------------------*/

void printer(String name, String value);
void Send_params();
void Send_status();

/*----------------------------------------------------------------------------++
||                      timing.h                          ||
++----------------------------------------------------------------------------*/

long t_since(unsigned long t_init);
