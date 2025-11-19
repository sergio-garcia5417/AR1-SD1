#include <Servo.h>

// ---- Servo objects ----
Servo servo1;
Servo servo2;
Servo servo3;

// ---- Joystick pins ----
const int joyX = A0;
const int joyY = A1;
const int joyBtn = 2;

// ---- Servo pins ----
const int servo1Pin = 3;
const int servo2Pin = 4;
const int servo3Pin = 5;

// ---- Servo angles ----
float angle1 = 30;
float angle2 = 30;
float angle3 = 30;

// ---- Control settings ----
int activeServo = 1; // 1, 2, or 3
int deadzone = 40; // reduces twitch
float stepSize = 0.3; // smaller = smoother
int updateDelay = 15; // speed/smoothness
bool lastBtnState = HIGH;

void setup() {
Serial.begin(115200);

// Attach servos
servo1.attach(servo1Pin);
servo2.attach(servo2Pin);
servo3.attach(servo3Pin);

// Joystick button
pinMode(joyBtn, INPUT_PULLUP);

// Center servos
servo1.write(angle1);
delay(100);   // wait 20 ms

servo2.write(angle2);
  delay(100);   // wait 20 ms

servo3.write(angle3);
  delay(100);   // wait 20 ms


Serial.println("Starting in SERVO 1 Control Mode");
}

void loop() {

// ---------------- BUTTON TOGGLE ------------------
bool btnState = digitalRead(joyBtn);

if (btnState == LOW && lastBtnState == HIGH) {
// button press = cycle servo selection
activeServo++;
if (activeServo > 3) activeServo = 1;

Serial.print("Switched control to SERVO ");
Serial.println(activeServo);

delay(250); // debounce
}

lastBtnState = btnState;

// ---------------- READ JOYSTICK ------------------
int xVal = analogRead(joyX);
int yVal = analogRead(joyY);

int joyMagnitude = max(abs(xVal - 512), abs(yVal - 512));

// Only move if joystick leaves deadzone
if (joyMagnitude > deadzone) {
int direction = (xVal > 512 + deadzone || yVal > 512 + deadzone) ? 1 : -1;

// Adjust the selected servo
if (activeServo == 1) {
angle1 += direction * stepSize;
angle1 = constrain(angle1, 0, 180);
}
else if (activeServo == 2) {
angle2 += direction * stepSize;
angle2 = constrain(angle2, 0, 180);
}
else if (activeServo == 3) {
angle3 += direction * stepSize;
angle3 = constrain(angle3, 0, 180);
}
}

// ---------------- WRITE ANGLES -------------------
servo1.write(angle1);
servo2.write(angle2);
servo3.write(angle3);

delay(updateDelay); // smooth, slow control
}


