/* -------------------------------------------------------++
||                       sensors.h                        ||
++--------------------------------------------------------*/

bool senseLick();

/* -------------------------------------------------------++
||                       states.h                         ||
++--------------------------------------------------------*/

int ActiveDelay(unsigned long wait, bool break_on_lick = false,
                  bool print_resp_time = false );

bool deliver_reward(bool water);

void punish(int del);

int Timeout(unsigned long wait, int depth = 0);

void preTrial();

int TrialStimulus();

void conditional_tone(int frequency, int duration);

/* -------------------------------------------------------++
||                 single_port_setup.h                    ||
++--------------------------------------------------------*/

void Habituation();

char runTrial();

/* -------------------------------------------------------++
||                    SerialComms.h                       ||
++--------------------------------------------------------*/

String getSerialInput();

int getSepIndex(String input, char seperator);

int UpdateGlobals(String input);

/* -------------------------------------------------------++
||                      timing.h                          ||
++--------------------------------------------------------*/

long t_since(unsigned long t_init);
