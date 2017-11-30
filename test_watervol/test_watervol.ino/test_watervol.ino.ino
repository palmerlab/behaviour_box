
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(10, OUTPUT);
  pinMode(13, OUTPUT); //LED
    
  digitalWrite(10, HIGH);   // turn the watervalve on
  digitalWrite(13, HIGH); 
  delay(10);                       // wait for a 10 ms
  digitalWrite(10, LOW);    // turn the watervalve off    
  digitalWrite(13, LOW); 
}

void loop() {
            ;    // wait for a second
}
