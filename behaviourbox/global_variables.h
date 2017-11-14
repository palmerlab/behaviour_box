/*--------------------------------------------------------++
||                  IO port settings:                     ||
++--------------------------------------------------------*/


const byte recTrig = 3;           // triggers ITC-18
const byte bulbTrig = 4;          // Bulb mode trigger for ThorImage
const byte stimulusPin = 5;       // digital pin 3 control whisker stimulation
const byte buzzerPin = 6;         // punishment buzzer
const byte speakerPin = 7;        // reward / cue tone
const byte statusLED = 13;        // led connected to digital pin 13
const byte lightPin = 2;          // Plug into Opto LED
const byte lickSens = A0;

const char waterPort = 10; // digital pins 10, 11 control water valve


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

byte reward_count = 0;     // Globals to count number of continuous left and rights

// stimulus parameters
// -------------------


// Reward
// ------

// Global value to keep track of the total water consumed
// this really shouldn't get much higher than 100.

byte waterVol = 10;               // uL per dispense
char trialType = 'G';             // 'G' or 'N'

int lickThres = 450;

byte Nports = 2;                  // flag for 2AFC vs GoNoGo
bool verbose = true;
bool break_wrongChoice = false;   // stop if the animal makes a mistake
bool punish_tone = false;
bool audio = false;               // flag for audio feed back

bool light_stim = false;          // flags for opto-stimulation
bool light_resp = false;          //



int Output_params() {

    // lickThres
    Serial.print("lickThres:");
    Serial.println(lickThres);
    // mode
    Serial.print("mode:");
    Serial.println(mode);
    // trialType
    Serial.print("trialType:");
    Serial.println(trialType);
    // break_wrongChoice
    Serial.print("break_wrongChoice:");
    Serial.println(break_wrongChoice);
    // minlickCount
    Serial.print("minlickCount:");
    Serial.println(minlickCount);
    // t_noLickPer
    Serial.print("t_noLickPer:");
    Serial.println(t_noLickPer);
    // timeout
    Serial.print("timeout:");
    Serial.println(timeout);
    // reward_nogo
    Serial.print("reward_nogo:");
    Serial.println(reward_nogo);
    // lickTrigReward
    Serial.print("lickTrigReward:");
    Serial.println(lickTrigReward);
    // t_stimONSET
    Serial.print("t_stimONSET:");
    Serial.println(t_stimONSET);
    // t_stimDUR
    Serial.print("t_stimDUR:");
    Serial.println(t_stimDUR);
    // t_rewardDEL
    Serial.print("t_rewardDEL:");
    Serial.println(t_rewardDEL);
    // t_rewardDUR
    Serial.print("t_rewardDUR:");
    Serial.println(t_rewardDUR);
    // t_trialDUR
    Serial.print("t_trialDUR:");
    Serial.println(t_trialDUR);
    // waterVol
    Serial.print("waterVol:");
    Serial.println(waterVol);
    // punish_tone
    Serial.print("punish_tone:");
    Serial.println(punish_tone);
    // debounce
    Serial.print("debounce:");
    Serial.println(debounce);
    // audio
    Serial.print("audio:");
    Serial.println(audio);
    // light_stim
    Serial.print("light_stim:");
    Serial.println(light_stim);
    // light_resp
    Serial.print("light_resp:");
    Serial.println(light_resp);
    return 0;
}
