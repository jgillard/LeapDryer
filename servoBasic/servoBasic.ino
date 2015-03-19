#include <Servo.h>
Servo servo;
int pin = 9;
int degVal = 80;

void setup() {
  Serial.begin(9600);
  while(!Serial){;}
  servo.attach(pin);
  servo.write(degVal);
  Serial.println("Ready");
}

void loop() {
  if (Serial.available()) {
    degVal = Serial.parseInt();
    degVal = constrain(degVal, 0, 160);
    servo.write(degVal);
    Serial.print("degVal: ");
    Serial.println(degVal);
  }
}
