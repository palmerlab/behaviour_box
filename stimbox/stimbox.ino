String version = ("#stimbox151119");

unsigned long ON = 1000;

unsigned long OFF[] = {5000, 5000};

int count;

// for use in showing the timer
unsigned long t_i = 0;
unsigned long t_f = 0;

int stimulusPIN = 3; //avoid pin 13, 0 and 1
int TTLin = A1;
int TTLval = 0;

void setup() {

pinMode(stimulusPIN, OUTPUT);
 
 randomSeed(analogRead(5));
 
 Serial.begin(9600);
 while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
 }
 Serial.println("#Arduino online");
 Serial.println(version);
 
 Serial.println("frequency (Hz)\ton Period (ms)\toff Period (ms)\tcount\tTimer");
}

// the loop routine runs over and over again forever:
void loop() {

    digitalWrite(13, LOW);
    digitalWrite(stimulusPIN, LOW);

    if(Serial.available() > 0){SerialComs()}
    
    TTLval = analogRead(TTLin);

    if (TTLval > 512){

        count = 0; 
        t_i = millis();

        while (TTLval > 512){
            count += 1;
            flutter(ON, OFF);
            TTLval = analogRead(TTLin);
        }

        t_f = millis();
        display_output();

        // this is safe, there is at least a 10 ms delay
        // to next pulse
    }
        
}



void flutter(unsigned long on, unsigned long off){
    digitalWrite(stimulusPIN, HIGH);
    digitalWrite(13, HIGH);
    
    delayMicroseconds(on);
    
    digitalWrite(stimulusPIN, LOW);
    digitalWrite(13, LOW);
    delayMicroseconds(off);
}

unsigned long Timer (unsigned long t_i, unsigned long t_f) {
  unsigned long timer = 0;
  
  if(t_i > t_f){
    timer = 0 - 1;
    timer = t_i + (timer - t_f);
  }
  else{
    timer = t_f - t_i;  
  }
  return timer;
}

void display_output(){
    Serial.print(frequency); Serial.print("\t");
    Serial.print((int)on); Serial.print("\t");
    Serial.print(off); Serial.print("\t");
    Serial.print(count); Serial.print("\t");
    Serial.print(Timer(t_i, t_f)); Serial.print("\n");
}

void SerialComs(){
    
    
    String input;
    
    while (Serial.available()) {
        delay(3);  //delay to allow buffer to fill
        char c = Serial.read();  //gets one byte from serial buffer
        input += c; //makes the string input
    }

    if (input.length() > 0) {
        /*
            parse: %d:%d&%d%d
            to OFF[%1] = %2
               OFF[%3] = %4
               
            http://arduino.stackexchange.com/questions/1013/
            how-do-i-split-an-incoming-string
        */
        // Read each command pair
        
        char* command = strtok(input, "&");
        while (command != 0)
        {
            // Split the command in two values
            char* separator = strchr(command, ':');
            if (separator != 0)
            {
                // Actually split the string in 2: replace ':' with 0
                
                *separator = 0; // replaces : with null terminator
                int index = atoi(command); //the decimal before the :
                
                ++separator; //points to memory adress after null
                OFF[index] = atoi(separator); //decimal after :

            }
            // Find the next command in input string
            command = strtok(0, "&");
        }

        input = "";
    }

}



