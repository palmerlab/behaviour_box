/*==============================================================================
||                           USER ADJUSTABLE VARIABLES
||                              adjust these HERE
++=============================================================================*/

// 1. set threshold
int lickThres = 400; //V

// timing parameters
// -----------------

unsigned int noLickDUR = 1000;  // ms   {{0, 1000 for later sessions}}
unsigned int respDEL = 500;   // ms  {{50, 150, 250, 500}}
unsigned int respDUR = 1500;  // ms {{2000}}
unsigned int timeout = 4000;         // ms  {{0, 5000}}
byte lickCount = 2;

unsigned int stimDUR = 200;     // ms
unsigned int stimONSET = 2000;  // ms
unsigned int trialDUR = 3000;  // ms
//unsigned int Durations[] = {10, 30, 50, 70, 90, 110};
//unsigned int Durations[] = {200, 200, 200, 200, 200, 200};
unsigned int Durations[] = { 10,  30,  50,  30,  10, 30,  
                              50,  70,  10, 110, 150, 200};
                                              
/*unsigned int Durations[] = {200, 200, 200, 200, 200, 200, 
                            200, 200, 200, 200, 200, 200};


/* THE LICK PARAMETERS
----------------------
The licking is defined by three paramaters:
- **lickThres**
    The threshold is an integer number from 0 - 1023, and represents the
    minimmum voltage required to call a lick. Note that you need to convert
    between scales here. To convert from volts you need to divide by 5.0 / 1024.
- **lickWidth**
    a simple debounce method to smooth out licks
    I don't recomend changing this, 5 ms works nicley to prevent over counting
    licks. If you are detecting too many licks try raising the threshold first
- **lickCount**
    number of licks required to give a reward 2 is a good number, 0 makes for
    a conditioning trial
*/

byte lickWidth = 15; // {{5 - 100}}

//------------------------------------------------------------------------------

// If `true` the reward is given on lick, if `false` the reward is given
// at the end of the reward period
bool lickTrigReward = true;
byte waterVol = 20;               // ms the valve is open for
bool audio = true;                // flag for audio feed back

/*============================================================================++
||                                IO port settings:                           ||
++===========================================================================++*/

const byte bulbTrig = 4;          // Bulb mode trigger for ThorImage
const byte stimulusPin = 5;       // digital pin 3 control whisker stimulation
const byte buzzerPin = 6;         // punishment buzzer
const byte speakerPin = 7;        // reward / cue tone
const byte statusLED = 13;        // led connected to digital pin 13
const byte lightPin = 2;          // Plug into Opto LED
const byte lickSens = 14;         // This is Analog 0
const byte waterPort = 10;        // digital pins 10, 11 control water valve

///
