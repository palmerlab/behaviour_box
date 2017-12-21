/*
  Opto Driver

 The circuit:
 * trigger wire attached to pin 2 behaviour_box arduino
 * 10K resistor attached to pin 2 from ground
 * LED attached from pin 5 to ground

based on example code:
 http://www.arduino.cc/en/Tutorial/ButtonStateChange

 */

const byte trigPin = 2;
const byte ledPin = 5;

bool lastTrigState = 0;
bool trigState = 0;

byte nb = 6;          //nb of light pulses to deliver
int duration = 10;    // duration of light pulse
int interval = 90;    // delay between pulses

void setup() {
    
    pinMode(trigPin, INPUT);
    pinMode(ledPin, OUTPUT);
    pinMode(13, OUTPUT);
}

void loop () {
    
    trigState = digitalRead(trigPin);
    
    if (trigState and not lastTrigState) {
        if (trigState == HIGH) {
            run_opto();
        }
    }
    // save the current state as the last state,
    //for next time through the loop
    lastTrigState = trigState;
}

void run_opto() {
    
    digitalWrite(13, HIGH);
    for (int i = 0; i < nb; i ++) {
        digitalWrite(ledPin, HIGH);
        delay(duration);
        digitalWrite(ledPin, LOW);
        delay(interval);
    }
    digitalWrite(13, LOW);
}
