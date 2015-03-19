#include <Servo.h>
#include <BLEduino.h>
Servo nozzleServo;
Servo motorServo;
BLEduino BLE;
int nozzlePin = 6;
int motorPin = 9;
int nozzleResetVal = 130;
int motorResetVal = 45;
int degVal = 0;

void resetServos();

void setup() {
  //BLE.begin();
  //BLE.sendCommand(COMMAND_RESET);
  Serial.begin(9600);
  while(!Serial){;}
  Serial.println("Ready");
  nozzleServo.attach(nozzlePin);
  motorServo.attach(motorPin);
  resetServos();
}

void resetServos() {
  motorServo.write(motorResetVal);
  delay(500);
  nozzleServo.write(160);
  delay(200);
  nozzleServo.write(nozzleResetVal);
  delay(500);
}

void waggleNozzle() {
  for (int i=0;i<10;i++) {
    nozzleServo.write(160);
    delay(500);
    nozzleServo.write(80);
    delay(500);
  }
}

void reply(int degVal) {
  char buf [3];
  sprintf(buf, "%i", degVal);
  
  uint8_t message = (uint8_t)degVal;
  uint8_t length = sizeof(message);
  uint8_t* ptr = &message;
  //Serial.println(*ptr);
  //Serial.println(*ptr, DEC);
  BLE.sendData(UART_SEND,ptr,length);
  //Serial.println("Message Sent");
  delay(5);
}

void loop() {
  /*
  if(BLE.available()) {
    BLEPacket packet = BLE.read();
    uint8_t length = packet.length;
    uint8_t* data = packet.data;    
    sscanf((const char*)data, "%d", &degVal);
  */
  if (Serial.available()) {
    degVal = Serial.parseInt();
    
    if (degVal > -1) {
      degVal = constrain(degVal, 0, 160);
      //nozzleServo.write(degVal);
      motorServo.write(degVal);
      // reply(degVal);
    } else if (degVal == -1) {
      waggleNozzle();
    } else if (degVal == -2) {
      resetServos();
    } else {
      Serial.println("a");
    }
  }
  delay(100);
}
