String version = ("\tflutter151109");

int on = 5000;  // how long 5V is sent (in μs)
float off; // how long 0V is sent (in μs)
int count;

String readString;

// for use in showing the timer
unsigned long t_i = 0;
unsigned long t_f = 0;

unsigned int frequency = 100; //must be float for divison to work
bool rFreq = false;
int fMax  = 10;
int fMin = 0;
int fScalar = 5;

int my_pin = 3; //avoid pin 13, 0 and 1
int TTLin = A1;
int TTLval = 0;

void setup() {

pinMode(my_pin, OUTPUT);
 
 randomSeed(analogRead(5));
 
 Serial.begin(9600);
 while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB port only
 }
 Serial.println("\tArduino online");
 Serial.println("\tflutter");
 Serial.println(version);
 Serial.println("frequency (Hz)\ton Period (ms)\toff Period (ms)\tcount\tTimer");
}

// the loop routine runs over and over again forever:
void loop() {

  digitalWrite(13, LOW);
  digitalWrite(my_pin, LOW);
    
    if(Serial.available() > 0){
        
        while (Serial.available()) {
            delay(3);  //delay to allow buffer to fill
            char c = Serial.read();  //gets one byte from serial buffer
            readString += c; //makes the string readString
        }

        if (readString.length() > 0) {
            Serial.println();
            Serial.print("\tInput received, understood: ");
            Serial.println(readString);
           
            if(readString.substring(0,1) == "f"){
                readString = readString.substring(1);
                frequency = readString.toInt();
                Serial.print("\tfrequency set:");
                Serial.println(frequency);
                Serial.println("\tmanual mode disabled");
                rFreq = false;
                
            } else if (readString.substring(0,1) == "r") {
                Serial.println("\tfrequency set to random");
                Serial.println("\tmanual mode disabled");
                rFreq = true;

                
                // parse frequency limits
                if (readString[1]){
                    
                    //count spaces and length
                    int spaces = 0;
                    int i = 2;
                    int i_0 = i-1;
                    while (readString[i]){
                        //Serial.print(readString[i]);
                        //Serial.println(!readString[i+1]);
                        int tmp_int = 0;
                        if (readString[i] == ' '){
                            
                            spaces += 1;
                            tmp_int = readString.substring(i_0, i).toInt();
                            i_0 = i;
                            
                            switch (spaces) {
                                case 1: 
                                    fMin = tmp_int; 
                                    Serial.print("\tfMin: "); Serial.println(fMin);
                                break;
                                case 2: 
                                    fMax = tmp_int;
                                    Serial.print("fMax: "); Serial.println(fMax); 
                                break;
                                case 3: 
                                    fScalar = tmp_int;
                                    Serial.print("fScalar: "); Serial.println(fScalar); 
                                    fMax = fMax / fScalar;
                                break;
                                
                            }
                            
                        }
                        else if (!readString[i+1]){                        
                            spaces += 1;
                            tmp_int = readString.substring(i_0, i+1).toInt();
                            
                            switch (spaces) {
                                case 1: 
                                    fMin = tmp_int; 
                                    Serial.print("\tfMin: "); Serial.println(fMin);
                                break;
                                case 2: 
                                    fMax = tmp_int;
                                    Serial.print("fMax: "); Serial.println(fMax); 
                                break;
                                case 3: 
                                    fScalar = tmp_int;
                                    Serial.print("fScalar: "); Serial.println(fScalar); 
                                    fMin = fMin / fScalar;
                                    fMax = fMax / fScalar;
                                break;
                                
                            }  
                        }
                        i +=1;
                    }
                }

            } else {
                Serial.print("\tset frequency to a valid integer or 'r'andom\n\tfor random give input in form `r mmm MMM ss`\n\twhere m is min, M is max, and s is a step size");      
            }   
            
            readString = "";
         
        }
  }
  
   if (rFreq == true){
       frequency = random(fMin,fMax) * fScalar;
   }
   
    
        off = (1000000.0/(float)frequency);

        if (off <= 5000){
            off = off / 2;
            on = off;
        } else{
            on = 5000;
            off = off - on;
        }

        TTLval = analogRead(TTLin);
        if (TTLval > 512){
            count = 0; 
            t_i = millis();
            while (TTLval > 512){
                count += 1;
                flutter((unsigned long)off);
                TTLval = analogRead(TTLin);
            }
            t_f = millis();
            display_output();
        }
}

void flutter(unsigned long off){
  digitalWrite(my_pin, HIGH);
  digitalWrite(13, HIGH);
  delayMicroseconds(on);
  digitalWrite(my_pin, LOW);
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






