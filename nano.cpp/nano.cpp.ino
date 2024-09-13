#include <Servo.h>

Servo leftServo; 
Servo rightServo;
int stopSpeed = 90; // 90 is stop, 0 is full speed one way, 180 is full speed the other way

void setup() {
  leftServo.attach(2);  
  rightServo.attach(3);
  Serial.begin(9600);  
  leftServo.write(stopSpeed); 
  rightServo.write(stopSpeed);
}

void moveUp() {
  leftServo.write(100);
  rightServo.write(80);
  }

void moveDown() {
  leftServo.write(80);
  rightServo.write(100);
}


void moveLeft() {
  rightServo.write(80);
}

void moveRight() {
  leftServo.write(100);
}

void dontMove() {
  leftServo.write(stopSpeed); 
  rightServo.write(stopSpeed);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();  // Read the incoming byte
    if (command == 'U') {  // "Up" arrow command
      moveUp(); 
    } else if (command == 'D') {  // "Down" arrow command
      moveDown();
    } else if (command == 'L') {  // "Left" arrow command
      moveLeft();
    } else if (command == 'R') {  // "Right" arror command
      moveRight();
    } else if (command == 'S') {  // "Stop" command
      dontMove();
    }
  }
}
