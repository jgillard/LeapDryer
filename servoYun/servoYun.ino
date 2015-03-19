#include <Bridge.h>
#include <YunServer.h>
#include <YunClient.h>
#include <Servo.h>

YunServer server;
int nozzlePin = 6;
int motorPin = 9;
Servo nozzleServo;
Servo motorServo;

void setup() {
  Serial.begin(9600);
  pinMode(13,OUTPUT);
  nozzleServo.attach(nozzlePin);
  motorServo.attach(motorPin);
  digitalWrite(13, LOW);
  Bridge.begin(); //takes 2 seconds
  digitalWrite(13, HIGH);
  server.listenOnLocalhost(); 
  server.begin();
}

void digitalCommand(YunClient client) {
  int pin, value;
  pin = client.parseInt();
  if (client.read() == '/') {
    value = client.parseInt();
    digitalWrite(pin, value);
  }
  client.print(F("Pin D"));
  client.print(pin);
  client.print(F(" set to "));
  client.println(value);
}

void analogCommand(YunClient client) {
  int pin, value;
  pin = client.parseInt();
  if (client.read() == '/') {
    value = client.parseInt();
    analogWrite(pin, value);
  }
  client.print(F("Pin D"));
  client.print(pin);
  client.print(F(" set to analog "));
  client.println(value);

  String key = "D";
  key += pin;
  Bridge.put(key, String(value));
}

void servoCommand(YunClient client) {
  int nozzleVal, motorVal;
  nozzleVal = client.parseInt();
  if (client.read() == '/') {
    motorVal = client.parseInt();
  }
  nozzleVal = constrain(nozzleVal, 0, 160);
  motorVal = constrain(motorVal, 20, 75);
  nozzleServo.write(nozzleVal);
  motorServo.write(motorVal);
  
  client.print(F("Nozzle servo set to "));
  client.println(nozzleVal);
  client.print(F("Motor servo set to "));
  client.println(motorVal);
}

void process(YunClient client) {
  String command = client.readStringUntil('/');
  if (command == "digital") {
    digitalCommand(client);
  }
  if (command == "analog") {
    analogCommand(client);
  }
  if (command == "servo") {
    servoCommand(client);
  }
}

void loop() {
  YunClient client = server.accept();

  if (client) {
    process(client);
    client.stop();
  }

  delay(50); 
}

