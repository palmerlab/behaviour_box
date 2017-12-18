
// the setup routine runs once when you press reset:
void setup() {
  // initialize serial communication at 11520 bits per second:
  Serial.begin(115200);
  pinMode(4, OUTPUT);
}

// the loop routine runs over and over again forever:
void loop() {
  // read the input on analog pin 0:
  int sensorValue = analogRead(A0);
  // print out the value you read:
  Serial.println(sensorValue);//(sensorValue/1024.0) * 5); // display output in V
  //Serial.println((sensorValue/1024.0) * 5); // display output in V
  delay(2);        // delay in between reads for stability

  if (sensorValue >= 150) {
    digitalWrite(4, HIGH);
    }
    else {
      digitalWrite(4, LOW);
      }
}
