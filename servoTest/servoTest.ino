#include <Servo.h>
#include <BLEduino.h>
Servo servo;
BLEduino BLE;
int servoPin = 6;
int degVal = 80;
int prevVal = 0;

void setup() {
  BLE.begin();
  BLE.sendCommand(COMMAND_RESET);
  servo.attach(servoPin);
  servo.write(degVal);
  //Serial.begin(9600);
  //while(!Serial){;}
  //Serial.println("Ready");
}

void loop() {
  
  if(BLE.available()) {
    BLEPacket packet = BLE.read();
    uint8_t length = packet.length;
    uint8_t* data = packet.data;    
    sscanf((const char*)data, "%d", &degVal);

  //while (Serial.available() > 0) {
    //degVal = Serial.parseInt();
    
    if (degVal > -1) {
      degVal = constrain(degVal, 0, 160);
      servo.write(degVal);
      prevVal = degVal;
      //Serial.print("degVal: ");
      //Serial.println(degVal);
      
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
