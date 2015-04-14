#include <Servo.h>
#include <QueueArray.h>

int nozzlePin = 6;
int motorPin = 9;
int IRpin = 0;
Servo nozzleServo;
Servo motorServo;
QueueArray <int> queue;

void setup() {
  Serial.begin(115200);
  nozzleServo.attach(nozzlePin);
  motorServo.attach(motorPin);
  nozzleServo.write(110);
  motorServo.write(50);
}

void loop() {
  int dist = analogRead(IRpin);
  queue.enqueue(dist);
  if (queue.count() > 10) {
    queue.dequeue();
  }
  QueueArray <int> queueTemp;
  for (int i = 1; i < queue.count(); i++) {
    queueTemp.enqueue(queue.dequeue());
  }
  int avg = 0;
  int i = 0;
  while (queueTemp.isEmpty() == 0) {
   avg += queueTemp.dequeue();
  }
  avg = avg / i;
    
  Serial.println(dist);
  Serial.println(avg);
  
  int nozzleVal = -0.08 * dist + 127;
  int motorVal = 0.23 * dist - 50;
  
  int nozzleMaxMin[] = {110, 80};
  int motorMaxMin[] = {90, 1};
  
  if (nozzleVal > nozzleMaxMin[0]) { nozzleVal = nozzleMaxMin[0]; }
  else if (nozzleVal < nozzleMaxMin[1]) { nozzleVal = nozzleMaxMin[1]; }
  if (motorVal > motorMaxMin[0]) { motorVal = motorMaxMin[0]; }
  else if (motorVal < motorMaxMin[1]) { motorVal = motorMaxMin[1]; }
  
  nozzleServo.write(nozzleVal);
  motorServo.write(motorVal);
  
  delay(50);
}
