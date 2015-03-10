#include <Servo.h>
Servo servo;
int servoPin = 6;
int degVal = 80;
int prevVal = 0;

void setup() {

  Serial.begin(9600);
  servo.attach(servoPin);
  servo.write(degVal);
  Serial.println("Ready");
}

void loop() {
  

  while (Serial.available() > 0) {
    degVal = Serial.parseInt();
    
    if (Serial.read() == '\n') {
        if (degVal > -1) {
          degVal = constrain(degVal, 0, 160);
          servo.write(degVal);
          prevVal = degVal;
          Serial.println(degVal);
          delay(5);
        } 
        else {
          for (int i=0;i<10;i++) {
            servo.write(130);
            delay(500);
            servo.write(90);
            delay(500);
          }
        }
    }
  }
}
