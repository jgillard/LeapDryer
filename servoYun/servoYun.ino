#include <Bridge.h>
#include <YunServer.h>
#include <YunClient.h>
#include <Servo.h>

YunServer server;
int motorPin = 9;
Servo motorServo;

void setup() {
  Serial.begin(9600);
  pinMode(13,OUTPUT);
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

  String key = "D";
  key += pin;
  Bridge.put(key, String(value));
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
  int degVal;
  //if (client.read() == '/') {
  degVal = client.parseInt();
  degVal = constrain(degVal, 0, 160);
  motorServo.write(degVal);

  client.print(F("Motor Servo set to "));
  client.println(degVal);

  String key = "MS";
  Bridge.put(key, String(degVal));
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

