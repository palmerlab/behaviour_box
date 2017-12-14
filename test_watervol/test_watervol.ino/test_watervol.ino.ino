
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(10, OUTPUT);
  pinMode(13, OUTPUT); //LED
  pinMode(A0, OUTPUT);
    
  digitalWrite(10, HIGH);   // turn the watervalve on
  digitalWrite(13, HIGH);
  delay(50);                       // wait for a 10 ms
  digitalWrite(10, LOW);    // turn the watervalve off    
  digitalWrite(13, LOW);
  analogWrite(A0, 0); 
}

void loop() {

}
