#include <Servo.h>

int nozzlePin = 6;
int motorPin = 5;
int IRpin = 5;
int redLED = 9;
int yellowLED = 10;
int greenLED = 11;
Servo nozzleServo;
Servo motorServo;
int queue[5];

int nozzleMaxMin[] = {110, 90};
int motorMaxMin[] = {90, 1};
//int farVal = 350;
//int closeVal = 600;

void setup() {
  Serial.begin(115200);
  nozzleServo.attach(nozzlePin);
  motorServo.attach(motorPin);
  nozzleServo.write(120);
  motorServo.write(40);
  pinMode(redLED, OUTPUT);
  pinMode(yellowLED, OUTPUT);
  pinMode(greenLED, OUTPUT);
  startupLEDs();

  // m = (nozzleMaxMin[0] - nozzleMaxMin[1]) / (farVal - closeVal);
}

void startupLEDs() {
  digitalWrite(redLED, HIGH);
  delay(1000);
  digitalWrite(yellowLED, HIGH);
  delay(1000);
  digitalWrite(greenLED, HIGH);

}

void loop() {
  int dist = analogRead(IRpin);
  int sum = 0;
  int avg = 0;
  for (int i = 0; i < 4; i++) {
    queue[i] = queue[i+1];
    sum += queue[i];
  }
  queue[3] = dist;
  sum += queue[3];
  avg = sum / 4;
    
  Serial.print("Dist: ");
  Serial.print(dist);
  Serial.print(" Avg: ");
  Serial.print(avg);
  
  int nozzleVal = -0.08 * dist + 138;
  int motorVal = 0.22 * dist - 75;
  
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
  
  if (dist > 500) { digitalWrite(yellowLED, LOW); }
  else { digitalWrite(yellowLED, HIGH); }
  if (dist > 400) { digitalWrite(greenLED, LOW); }
  else { digitalWrite(greenLED, HIGH); }
  
 
}
