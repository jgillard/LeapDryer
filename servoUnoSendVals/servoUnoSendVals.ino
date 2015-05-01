#include <Servo.h>

int nozzlePin = 6;
int motorPin = 5;
Servo nozzleServo;
Servo motorServo;

void setup() {
  Serial.begin(115200);
  nozzleServo.attach(nozzlePin);
  motorServo.attach(motorPin);
  nozzleServo.write(110);
  motorServo.write(28);
}

void loop() {
  while (Serial.available() > 0) {
    int nozzleVal = Serial.parseInt();
    int motorVal = Serial.parseInt();
    if (Serial.read() == '\n') {
      digitalWrite(3, LOW);
      digitalWrite(4, LOW);
      Serial.println(nozzleVal);
      Serial.println(motorVal);
      nozzleServo.write(nozzleVal);
      motorServo.write(motorVal);
    }
  }
}
