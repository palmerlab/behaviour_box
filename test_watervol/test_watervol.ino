
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(10, OUTPUT);
  pinMode(13, OUTPUT);
  
  for (int i = 0; i < 100;  i++) {
    digitalWrite(10, HIGH);   // turn the watervalve on
    digitalWrite(13, HIGH);
    delay(85);                       // wait for a 10 ms
    digitalWrite(10, LOW);    // turn the watervalve off
    digitalWrite(13, LOW);
    delay(100);
  }
}

void loop() {

}
