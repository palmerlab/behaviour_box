/*--------------------------------------------------------++
||                  IO port settings:                     ||
++--------------------------------------------------------*/


const byte recTrig = 3;           // triggers ITC-18
const byte bulbTrig = 4;          // Bulb mode trigger for ThorImage
const byte stimulusPin = 5;       // digital pin 3 control whisker stimulation
const byte buzzerPin = 6;         // punishment buzzer
const byte speakerPin = 7;        // reward / cue tone
const byte statusLED = 13;        // led connected to digital pin 13
const byte lickSens = A0;

const char waterPort = 10; // digital pins 10, 11 control water valve

const String end_trial_msg = "- Status: Ready";

/*-----------------------------------------------------------------------------

REFENENCED IN sensors.h
=======================
*/

bool lickOn = false;

// timing parameters
// -----------------

unsigned long t_init;             // ms
unsigned int t_noLickPer = 1000;  // ms
unsigned int trial_delay = 500;   // ms
unsigned int t_stimONSET = 2000;  // ms
unsigned int t_stimDUR = 500;     // ms
unsigned int t_rewardDEL = 150;   // ms
unsigned int t_rewardDUR = 2000;  // ms
unsigned int t_trialDUR = 5000;  // ms
unsigned int timeout = 0;         // ms

byte debounce = 5;         // a simple debounce method

char mode = '-';                  //one of 'h'abituation, 'o'perant
byte minlickCount = 5;
bool lickTrigReward = 1;
bool reward_nogo = 0;

// stimulus parameters
// -------------------


// Reward
// ------

// Global value to keep track of the total water consumed
// this really shouldn't get much higher than 100.

byte waterVol = 10;               // uL per dispense
char trialType = 'G';             // 'G' or 'N'

int lickThres = 450;

bool verbose = true;
bool punish_tone = false;
bool audio = false;               // flag for audio feed back
