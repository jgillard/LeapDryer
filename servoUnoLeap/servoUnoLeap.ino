#include <Servo.h>

int nozzlePin = 6;
int motorPin = 9;
Servo nozzleServo;
Servo motorServo;

void setup() {
  Serial.begin(115200);
  nozzleServo.attach(nozzlePin);
  motorServo.attach(motorPin);
  pinMode(3, OUTPUT); // YELLOW
  pinMode(4, OUTPUT); // RED
}

void loop() {
  while (Serial.available() > 0) {
    int nozzleVal = Serial.parseInt();
    int motorVal = Serial.parseInt();
    
    if (Serial.read() == '\n') {
      // NO HANDS
      if (motorVal == 90 && nozzleVal == 90) {
        digitalWrite(3, LOW);
        digitalWrite(4, HIGH);
        Serial.println(110);
        Serial.println(90);
        nozzleServo.write(110);
        motorServo.write(90);
      } 
      // ONE HAND
      if (motorVal == 92 && nozzleVal == 92) {
        digitalWrite(3, HIGH);
        digitalWrite(4, LOW);
      } 
      // ON EXIT
      else if (motorVal == 91 && nozzleVal == 91) {
        digitalWrite(3, LOW);
        digitalWrite(4, LOW);
      }
      else {
        digitalWrite(3, LOW);
        digitalWrite(4, LOW);
        Serial.println(nozzleVal);
        Serial.println(motorVal);
        nozzleServo.write(nozzleVal);
        motorServo.write(motorVal);
      }
    }
  }
}

