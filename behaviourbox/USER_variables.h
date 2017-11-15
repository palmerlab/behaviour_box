/*============================================================================++
||                                IO port settings:                           ||
++===========================================================================++*/

const byte bulbTrig = 4;          // Bulb mode trigger for ThorImage
const byte stimulusPin = 5;       // digital pin 3 control whisker stimulation
const byte buzzerPin = 6;         // punishment buzzer
const byte speakerPin = 7;        // reward / cue tone
const byte statusLED = 13;        // led connected to digital pin 13
const byte lightPin = 2;          // Plug into Opto LED
const byte lickSens = A0;
const byte waterPort = 10;        // digital pins 10, 11 control water valve

/*==============================================================================
||                           USER ADJUSTABLE VARIABLES
||                              adjust these HERE
++=============================================================================*/

// timing parameters
// -----------------

unsigned int noLickDUR = 1000;  // ms
unsigned int stimONSET = 2000;  // ms
unsigned int stimDUR = 500;     // ms
unsigned int respDEL = 150;   // ms
unsigned int respDUR = 2000;  // ms
unsigned int trialDUR = 5000;  // ms
unsigned int timeout = 0;         // ms

/* THE LICK PARAMETERS
----------------------
The licking is defined by three paramaters:
- **lickThres**
  The threshold is an integer number from 0 - 1023, and represents the minimmum
  voltage required to call a lick. Note that you need to convert between scales
  here. To convert from volts you need to divide by 5.0 / 1024.
- **lickWidth**
  a simple debounce method to smooth out licks
  I don't recomend changing this, 5 ms works nicley to prevent over
  counting licks. If you are detecting too many licks try raising
  the threshold first
- **lickCount**
  number of licks required to give a reward
  2 is a good number, 0 makes for a conditioning trial
*/
int lickThres = 1.5 / (5.0/1024);
byte lickWidth = 5;
byte lickCount = 0;
//------------------------------------------------------------------------------

// If 1 the reward is given on lick, if 0 the reward is given
// at the end of the reward period
bool lickTrigReward = 1;
byte waterVol = 10;               // ms the valve is open for
bool audio = true;               // flag for audio feed back
