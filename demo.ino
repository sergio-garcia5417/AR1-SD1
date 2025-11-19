#include <Servo.h>

// ---- Servo objects ----
Servo servo1;
Servo servo2;
Servo servo3;

// ---- Pins ----
const int joyY = A1;
const int joyBtn = 2;

const int servo1Pin = 3;
const int servo2Pin = 4;
const int servo3Pin = 5;

// ---- Stored angles (no auto movement at startup) ----
float angle1 = 90;
float angle2 = 90;
float angle3 = 90;

// ---- Settings ----
int activeServo = 1;
int deadzone = 40;
float stepSize = 0.5;
int updateDelay = 15;
bool lastBtnState = HIGH;

void setup() {
  servo1.attach(servo1Pin);
  servo2.attach(servo2Pin);
  servo3.attach(servo3Pin);

  pinMode(joyBtn, INPUT_PULLUP);
}

void loop() {

  // Toggle active servo with button
  bool btnState = digitalRead(joyBtn);
  if (btnState == LOW && lastBtnState == HIGH) {
    activeServo++;
    if (activeServo > 3) activeServo = 1;
    delay(250); // debounce
  }
  lastBtnState = btnState;

  // Joystick Y-axis
  int yVal = analogRead(joyY);
  int diff = yVal - 512;

  // Move only when joystick leaves deadzone
  if (abs(diff) > deadzone) {
    float change = (diff > 0 ? stepSize : -stepSize);

    if (activeServo == 1) {
      angle1 = constrain(angle1 + change, 0, 180);
      servo1.write(angle1);
    }
    else if (activeServo == 2) {
      angle2 = constrain(angle2 + change, 0, 180);
      servo2.write(angle2);
    }
    else if (activeServo == 3) {
      angle3 = constrain(angle3 + change, 0, 180);
      servo3.write(angle3);
    }
  }

  delay(updateDelay);
}
