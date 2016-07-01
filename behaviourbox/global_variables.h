/*--------------------------------------------------------++
||                  IO port settings:                     ||
++--------------------------------------------------------*/

const byte recTrig = 3;           // triggers ITC-18
const byte bulbTrig = 4;          // Bulb mode trigger for ThorImage
const byte stimulusPin = 5;       // digital pin 3 control whisker stimulation
const byte buzzerPin = 6;         // punishment buzzer
const byte speakerPin = 7;        // reward / cue tone
const byte statusLED = 13;        // led connected to digital pin 13
const char lickSens[] = {A0,A1};

const char waterPort[] = {10,11}; // digital pins 10, 11 control water valve 


/*-----------------------------------------------------------------------------

REFENENCED IN sensors.h
=======================
*/

// Electrodes on the MPR121 to be used.

byte lick_port_L = 0;           // the left lick port
byte lick_port_R = 1;           // the right lick port

bool lickOn[] = {false, false};

// timing parameters
// -----------------

unsigned long t_init;             // ms
unsigned int t_noLickPer = 1000;  // ms
unsigned int trial_delay = 500;   // ms
unsigned int t_stimONSET = 2000;  // ms
unsigned int t_stimDUR = 500;     // ms
unsigned int t_rewardDEL = 150;   // ms
unsigned int t_rewardDUR = 2000;  // ms
unsigned int timeout = 0;         // ms

char mode = '-';                  //one of 'h'abituation, 'o'perant
char rewardCond = 'B';            // a value that is 'L' 'R', 'B' or 'N' to represent lick port to be used
byte minlickCount = 5;

byte reward_count[] = {0, 0};     // Globals to count number of continuous left and rights

// stimulus parameters
// -------------------

bool right = 1;
bool left = 0;

// audio
// -----
bool auditory = 0;

int toneGoodLeft = 6000;          // Hz
int toneGoodRight = 7000;         // Hz
int toneGood = 2000;              // Hz
int toneBad = 500;                // Hz
int toneDur = 100;                // Hz

// Reward
// ------

// Global value to keep track of the total water consumed
// this really shouldn't get much higher than 100. 

char waterVol = 10;               // uL per dispense
char trialType = 'G';             // 'G' or 'N'

int lickThres = 450;

bool verbose = true;
bool break_wrongChoice = false;   // stop if the animal makes a mistake
bool break_on_early = false;      // stop if the animal licks during the stimulus presentation