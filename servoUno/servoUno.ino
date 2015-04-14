#include <Servo.h>

int nozzlePin = 6;
int motorPin = 9;
Servo nozzleServo;
Servo motorServo;

void setup() {
  Serial.begin(115200);
  nozzleServo.attach(nozzlePin);
  motorServo.attach(motorPin);
}

void loop() {
  while (Serial.available() > 0) {
    int nozzleVal = Serial.parseInt();
    int motorVal = Serial.parseInt();
    if (Serial.read() == '\n') {
      Serial.println(nozzleVal);
      Serial.println(motorVal);
      nozzleServo.write(nozzleVal);
      motorServo.write(motorVal);
    }
  }
}

