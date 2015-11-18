String version = "\tlick_controller 151117";

//TODO: make a conditioning protocol
//TODO: rename singlestim operant
//TODO: find an obvious method for producing constant noise

/*
    Authour: Naoya Takahashi
        modified by Andrew Micallef
      
    This program delivers sensory stimulation and opens water 
    valve when the animal touches the licking sensor within a 
    certain time window.

    Setup connections:
    ------------------
      
    ---------   -----------------  ------------  
    DIGITAL     output             variable
    ---------   -----------------  ------------
    pin 2       recording trigger  `recTrig`  
    pin 4       stimulus TTL       `whiskStim`
    pin 6       speaker for cues   `tonePin`
    pin 8       syringe pump TTL   `waterValve`
    pin 9       vacuum tube valve  `vacValve`
    pin 13      lick report        `licking`
    ---------   -----------------  ------------
    ANALOG IN   input
    ---------   -----------------  ------------
    A0          piezo lick sensor  lickSens
    ---------   -----------------  ------------
    Table: connections to lick controller

      
    Start program:
    --------------

    Trial intervals will randomized between 'minITI' and 'maxITI'. 
    During a trial, the animal has to wait a stimulation without 
    licking (no-lick period, 'nolickPer').

    If it licks during no-lick period, the time of stimulation 
    will be postponed by giving a time out (randomized between 
    'minTimeOut' and 'maxTimeOut').

    When a stimulation is delivered (stimulus duration: 'stimDur'), 
    the animal need to respond (touch the sensor) within a certain 
    time window ('crPer') to get a water reward.

    Delayed licking after the time window will not be rewarded. 
    Opening duration of the water valve is defined by 'valveDur'.

    A TTL trigger for recording will be delivered 
    'baseLineTime' (1 s in default setting) before the stimulus.
  
 */






// IO port settings:
const int recTrig = 2;    // digital pin 2 triggers ITC-18
const int stimulus = 4;    // digital pin 4 control whisker stimulation
const int tonePin = 6;
const int waterPort = 8;    // digital pin 8 control water valve 
const int vacValve = 9;     // digital pin 9 controls vacuum
const int lickRep = 13;      // led connected to digital pin 13
const int lickSens = A0; // the piezo is connected to analog pin 0

int lickThres = 450;

// timing parameters
int t_init;
int t_start;

int toneBad = 500; //Hz
int toneDur = 100; 

// Global value to keep track of the total water consumed
int waterCount = 0; 
int waterVol = 5; //uL per dispense


void setup (){
    // Open serial communications and wait for port to open:
    Serial.begin(9600);
    // This requires RX and TX channels (pins 0 and 1)
    while (!Serial) {
        ; // wait for serial port to connect. Needed for native USB port only
    }
    //Confirm connection and telegraph the code version
    Serial.println("\tArduino online");
    Serial.println("\tcontrol");
    Serial.println(version);
    
    //was three lines before
    Serial.print("\tLick Threshold:\t"); Serial.print((float(lickThres)/1024)*5); Serial.println(" V");
    
    randomSeed(analogRead(5));

    pinMode(recTrig, OUTPUT); // declare the recTrig as as OUTPUT
    pinMode(waterPort, OUTPUT); // declare the waterValve as as OUTPUT
    pinMode(vacValve, OUTPUT); // declare the vacValve as as OUTPUT
    pinMode(stimulus, OUTPUT); // declare the whiskStim as as OUTPUT
    pinMode(lickRep, OUTPUT); // declare the licking as as OUTPUT
    pinMode(tonePin, OUTPUT);
}


void loop () {
    
    int mode = serialComs();
    
    if (mode >= 0){
        // single trial returns an inter trial interval   
        Serial.println( 
          "modeString\ttrial_no\twaterCount\ttrial_delay\tistimeout\tstimTrial\tresponse\tlickCount"
        );
        
        int n_trial = 0;
        int interTrialInt = runTrial(n_trial, mode, 500);
        
        
        while (!Serial.available()){
            n_trial += 1;
            interTrialInt = runTrial(n_trial, mode, interTrialInt);
        }
    }
    else {
        if (senseLick()){
            tone(tonePin, toneBad, 10);
            delay(100);
        }
    }
}

int runTrial (int trial_no, int modeSwitch, int trial_delay) {
    // returns number of milliseconds
    // until next trial
    
    // TODO add a dual stim contingency
    // stim1 = analagueWrite(pin, value)
    
    // local variables and initialisation of the trial
    String outString = "";
    int t; // local time
    int timeout = 0;
    int lickCount = 0;

    //timing parameters    
    int t_noLickPer;   // ms
    int t_stimSTART;   // ms
    int t_stimEND;     // ms
    int t_rewardSTART; // ms
    int t_rewardEND;   // ms
    int t_trialEND;   // ms
    int minITI;        // ms
    int maxITI;        // ms
    int maxTimeOut;    // ms
    int minTimeOut;    // ms
    
   String modeString;
   
   // sets paramaters according to the training phase (mode)
   switch (modeSwitch){
     case 0: 
        modeString = "conditioning0"; 
        t_noLickPer = 0;   // ms
        t_stimSTART = 4000;   // ms
        t_stimEND = 4500;     // ms
        t_rewardSTART = 4500; // ms
        t_rewardEND = 10000;   // ms
        t_trialEND = 10000;   // ms
        minITI = 3000;        // ms
        maxITI = 6000;        // ms
        maxTimeOut = 0;    // ms
        minTimeOut = 0;    // ms
     break;
     
     case 1: 
        modeString = "operant1";
        t_noLickPer = 0;   // ms
        t_stimSTART = 4000;   // ms
        t_stimEND = 4500;     // ms
        t_rewardSTART = 5000; // ms
        t_rewardEND = 7000;   // ms
        t_trialEND = 10000;   // ms
        minITI = 3000;        // ms
        maxITI = 6000;        // ms
        maxTimeOut = 0;    // ms
        minTimeOut = 0;    // ms
     break;
     
      case 2: 
        modeString = "operant2";
        t_noLickPer = 3000;   // ms
        t_stimSTART = 4000;   // ms
        t_stimEND = 4500;     // ms
        t_rewardSTART = 5000; // ms
        t_rewardEND = 6000;   // ms
        t_trialEND = 10000;   // ms
        minITI = 3000;        // ms
        maxITI = 6000;        // ms
        maxTimeOut = 500;    // ms
        minTimeOut = 1000;    // ms
     break;
     
     case 3: 
        modeString = "operant3";
        t_noLickPer = 3000;   // ms
        t_stimSTART = 4000;   // ms
        t_stimEND = 4500;     // ms
        t_rewardSTART = 5000; // ms
        t_rewardEND = 7000;   // ms
        t_trialEND = 10000;   // ms
        minITI = 3000;        // ms
        maxITI = 6000;        // ms
        maxTimeOut = 1000;    // ms
        minTimeOut = 3000;    // ms
     break;
     
     default: 
       Serial.println("invalid mode"); 
       return 3000;
     break;
   }
  
    bool stimTrial = random(0,5);
    bool response = false;
    bool lickOn = false;
    bool firstLick = true;
    bool rewardAvailable = true;
    
    //start the clock
    t_init = millis() + trial_delay;
    
    // t_init is initialised such that t_now
    // returns 0 at the start of the trial, and 
    // increases from there.
    t = t_now();
    Serial.print("\ttrial starts in:\t");
    Serial.print(t); Serial.println(" ms");
    
    while (t < 0) {
        /* while the trial has not started 
           1. update the time
           2. check for licks
           3. punish licks with additional timeout
           4. trigger the recording by putting recTrig -> HIGH
        */
        
        // 1. update time
        // 2. check for licks
        t = t_now();
        lickOn = senseLick();
        
        digitalWrite(vacValve, HIGH);

        /* 3. punish licks\
              additional time out requires that time is added to 
              `t_init`. Apply a cool down period; the animal 
              usually makes multiple licks and so it is important 
              that an arbitrary limit is set, else she will end up
              with infinite time out.
        */
        
        // 4. trigger the recording
        if (t > -10){
            digitalWrite(recTrig, HIGH);
        }
    
    // note, recTrig is switched off immediately after the
    // loop to avoid artifacts in the recording
    
    } digitalWrite(recTrig, LOW); digitalWrite(vacValve, LOW);
    
    
    Serial.print("\tTrial Start:\t"); Serial.println(t); Serial.print("\tGo trial:\t"); Serial.println(stimTrial);
    
    //trial start phase    
    while (t < t_stimSTART){
        /* The trial has started but the stimulus
           is yet to be delivered, so long as timeout
           is not in place
           1. update the time
           2. check for licks
           3. punish licks with additional timeout\
              this breaks the function and ultimatley results
              in a line being printed with the lick time `t`.
        */

        // 1. update the time
        // 2. check for licks  
        t = t_now();
        lickOn = senseLick();
        
        // 3. punish licks with additional timeout
        if ((lickOn) and (t_noLickPer) and (t > t_noLickPer)) {
            /* conditions
                : 
                1. if the animal has licked
                2. if there is a no lick period 
                    (is false during conditioning)
                3. if the no lick period has started
                    (the timenow is greater than no lick time)
            */ 
            
            // 3.2. report that a timeout has occurred
            Serial.print("\ttimeout added:\t");
            Serial.print(timeout); Serial.println(" ms");
            
            // 3.3. report to the animal that timeout has occurred
            tone(tonePin, toneBad, toneDur);
            
            // 3.4. make a standard output line
           
            Serial.print(modeString); Serial.print("\t"); 
            Serial.print(trial_no); Serial.print("\t"); 
            Serial.print(waterCount); Serial.print("\t"); 
            Serial.print(trial_delay); Serial.print("\t"); 
            Serial.print(timeout>0); Serial.print("\t"); 
            Serial.print(stimTrial); Serial.print("\t"); 
            Serial.print(response); Serial.print("\t"); 
            Serial.print(lickCount); Serial.print("\n");
             
            // exits, starting a new trial in the higher loop
            // 3.1. set a timout value
            return random(maxTimeOut, minTimeOut);
        }
    }
    
     Serial.print("\tStim Start:\t"); Serial.println(t);
    
    //The stimulus phase
    while (t < t_stimEND){
        /* Run the buzzer while:
           1. update the time
           2. check for licks
        */
        t = t_now();
        lickOn = senseLick();
        
        if(stimTrial){digitalWrite(stimulus, HIGH);}
    } digitalWrite(stimulus, LOW);
    
     Serial.print("\tStim Endt:\t"); Serial.println(t);
    
    // post stimulus delay
    while (t < t_rewardSTART){
        /* this acts as a grace period, 
           licks do not count still
           1. update the time
           2. check for licks
        */
        t = t_now();
        lickOn = senseLick();
        //if (lickOn){Serial.println("gotcha");}
    }
    
    Serial.print("\tReward Start:\t"); Serial.println(t);
    
    // reward period
    while (t < t_rewardEND) {
        t = t_now();
        lickOn = senseLick();
        lickCount += lickOn;
        // response reports if there was a lick in the reward
        // period.
        
        if ((modeSwitch == 0) and stimTrial and rewardAvailable) {
            // a freebie for conditioning trials
            digitalWrite(waterPort, HIGH);
            delay(10);
            digitalWrite(waterPort, LOW);
            rewardAvailable = false;
        }
        
        if (lickOn){
            if (stimTrial){
                // the condition is that the animal has licked,
                // but that no response has been reported yet
                if (!response){
                    response=lickOn;    
                    digitalWrite(waterPort, HIGH);
                    //delay(300); // a shit thing, but it seems essential
                    
                } else if (firstLick == true){
                    // if this is the first lick in the response
                    // period; loop for 20 ms to deliver some water
                    
                    delay(10);
                    // shut off the waterport, and set firstLick false so only one
                    // reward per trial
                    digitalWrite(waterPort, LOW);
                    firstLick = false;    
                }
            }
            delay(10); // space out the lick reports a bit
        }
        digitalWrite(waterPort, LOW); //safety catch
    }
    
    Serial.print("\ttrial End:\t"); Serial.println(t - t_trialEND); Serial.print("\tLicks? :\t"); Serial.println(response);
    
    // fixed cool down period
    while (t < t_trialEND){
        t = t_now();
        lickOn = senseLick();
    }
    
    waterCount += (int(response) * waterVol);
    
    
    Serial.print(modeString); Serial.print("\t"); 
    Serial.print(trial_no); Serial.print("\t"); 
    Serial.print(waterCount); Serial.print("\t"); 
    Serial.print(trial_delay); Serial.print("\t"); 
    Serial.print(timeout>0); Serial.print("\t"); 
    Serial.print(stimTrial); Serial.print("\t"); 
    Serial.print(response); Serial.print("\t"); 
    Serial.print(lickCount); Serial.print("\n"); 
                
    return random(minITI, maxITI);
}


int t_now(){
    // is less than 0 before the trial starts
    // is greater than 0 after the start of trial
    return millis() - t_init;
}

bool senseLick(){
	// check to see if the lick sensor has moved
    // set lickDetected
	boolean lickDetected = false;
	int sensVal = analogRead(lickSens);
	
	if (sensVal <= lickThres){
		digitalWrite(lickRep, HIGH);
		lickDetected = true;
	} else {
		digitalWrite(lickRep, LOW);
		lickDetected = false;
	}
    digitalWrite(tonePin, !random(0, random(50)));
	return lickDetected;
}

int serialComs(){
    
    int mode = -1;
    String readString;
       
    if (Serial.available()) {
        while (Serial.available()) {
     
            delay(3);  //delay to allow buffer to fill
            char c = Serial.read();  //gets one byte from serial buffer
            readString += c; //makes the string readString
        }
        
        if (readString.length() > 0) {
            Serial.print("\tinput:\t");
            Serial.println(readString);
             
            char flag = readString[0];
            
            if(flag == '-'){
                // read the flag and update the appropriate variable
                flag = readString[1];
                if (flag == 't'){
					readString = readString.substring(2);
					lickThres = readString.toInt();
					Serial.print("\tlickThres set:\t");
                        Serial.print(lickThres);
                        Serial.print(" (");
                        Serial.print((float(lickThres)/1024)*5);
                        Serial.println(" V)");
				}
			} else if(flag == 'm'){
                mode = readString.substring(1).toInt();
                Serial.print("\tmode:\t");
                Serial.println(readString.substring(1).toInt());
                return mode;
            } else {
                Serial.println("\tcould not parse input");
            }
            
            readString = "";
        }             
    }
    return mode;
}

