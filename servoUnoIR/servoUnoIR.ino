#include <Servo.h>
#include <QueueArray.h>

int nozzlePin = 6;
int motorPin = 9;
int IRpin = 0;
Servo nozzleServo;
Servo motorServo;
int queue[5];

void setup() {
  Serial.begin(115200);
  nozzleServo.attach(nozzlePin);
  motorServo.attach(motorPin);
  nozzleServo.write(120);
  motorServo.write(40);
}

void loop() {
  int dist = analogRead(IRpin);
  int sum = 0;
  int avg = 0;
  for (int i = 0; i < 5; i++) {
    queue[i] = queue[i+1];
    sum += queue[i];
  }
  queue[4] = dist;
  sum += queue[4];
  avg = sum / 5;
    
  Serial.print("Dist: ");
  Serial.print(dist);
  Serial.print(" Avg: ");
  Serial.print(avg);
  
  int nozzleVal = -0.1 * avg + 130;
  int motorVal = 0.26 * avg - 52;
  
  int nozzleMaxMin[] = {110, 80};
  int motorMaxMin[] = {90, 1};
  
  if (nozzleVal > nozzleMaxMin[0]) { nozzleVal = nozzleMaxMin[0]; }
  else if (nozzleVal < nozzleMaxMin[1]) { nozzleVal = nozzleMaxMin[1]; }
  if (motorVal > motorMaxMin[0]) { motorVal = motorMaxMin[0]; }
  else if (motorVal < motorMaxMin[1]) { motorVal = motorMaxMin[1]; }
  
  Serial.print("\tNozzle: ");
  Serial.print(nozzleVal);
  Serial.print(" Motor: ");
  Serial.println(motorVal);
  
  nozzleServo.write(nozzleVal);
  motorServo.write(motorVal);
}
