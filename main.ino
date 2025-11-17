#include <Servo.h>

/*
 ==========================================================
   5-DOF ROBOT ARM + GRIPPER
   THREE BUTTON-TRIGGERED PICK-AND-PLACE SEQUENCES

 ==========================================================
*/

// ---------------- SERVO OBJECTS ----------------
Servo Base;       // rotates arm left/right
Servo Shoulder;   // lifts link 1
Servo Elbow;      // moves link 2
Servo Wrist;      // rotates wrist
Servo Gripper;    // open/close

// ---------------- SERVO PINS -------------------
const int PIN_BASE     = 3;
const int PIN_SHOULDER = 5;
const int PIN_ELBOW    = 6;
const int PIN_WRIST    = 9;
const int PIN_GRIPPER  = 10;

// ---------------- BUTTON PINS ------------------
const int BTN_ACTION1 = 22;
const int BTN_ACTION2 = 23;
const int BTN_ACTION3 = 24;

// ---------------- JOYSTICK (OPTIONAL) ----------
const int JOY_X = A0;
const int JOY_Y = A1;
bool joystickMode = false;   // change to true for manual mode

// ==========================================================
// PLACEHOLDER POSES — CHANGE THESE LATER
// ==========================================================

// Home calibration position
int homePose[5] = {90, 90, 90, 90, 30};

// x1 → pick point 1
int x1Pose[5] = {70, 110, 120, 90, 30};

// x2 → place point 1
int x2Pose[5] = {60, 140, 100, 90, 30};

// x3 → pick point 2
int x3Pose[5] = {95, 100, 130, 90, 30};

// x4 → place point 2
int x4Pose[5] = {75, 115, 95, 90, 30};

// x5 → full extension point (hold 10 sec)
int x5Pose[5] = {45, 70, 55, 90, 30};

// Gripper open/close angles (placeholder)
int gripOpen  = 30;
int gripClose = 120;

// ==========================================================
// ------------------- Smooth Movement Function -------------
// ==========================================================
void moveToPose(int pose[5], int stepDelay = 10) {

  // Gradually move each joint to target
  for (int step = 0; step <= 180; step++) {

    Base.write(    map(step, 0, 180, Base.read(),     pose[0]) );
    Shoulder.write(map(step, 0, 180, Shoulder.read(), pose[1]) );
    Elbow.write(   map(step, 0, 180, Elbow.read(),    pose[2]) );
    Wrist.write(   map(step, 0, 180, Wrist.read(),    pose[3]) );
    Gripper.write( map(step, 0, 180, Gripper.read(),  pose[4]) );

    delay(stepDelay);
  }
}

// ==========================================================
// ----------------------- ACTION 1 -------------------------
// ==========================================================
void doAction1() {

  moveToPose(homePose);

  moveToPose(x1Pose);

  Gripper.write(gripClose);  // pick
  delay(800);

  moveToPose(x2Pose);

  Gripper.write(gripOpen);   // drop
  delay(500);

  moveToPose(homePose);
}

// ==========================================================
// ----------------------- ACTION 2 -------------------------
// ==========================================================
void doAction2() {

  moveToPose(homePose);

  moveToPose(x3Pose);

  Gripper.write(gripClose);
  delay(800);

  moveToPose(x4Pose);

  Gripper.write(gripOpen);
  delay(500);

  moveToPose(homePose);
}

// ==========================================================
// ----------------------- ACTION 3 -------------------------
// ==========================================================
void doAction3() {

  moveToPose(homePose);

  moveToPose(x4Pose);

  Gripper.write(gripClose);
  delay(800);

  moveToPose(x5Pose);   // hold position
  delay(10000);         // hold 10 seconds

  // LOWER item (placeholder logic)
  int lowerPose[5] = { x5Pose[0], x5Pose[1] + 20, x5Pose[2] + 20, x5Pose[3], x5Pose[4] };
  moveToPose(lowerPose);

  Gripper.write(gripOpen);   // release
  delay(500);

  moveToPose(homePose);
}

// ==========================================================
// ---------------- JOYSTICK MANUAL MODE --------------------
// ==========================================================
void joystickControl() {

  int x = analogRead(JOY_X);
  int y = analogRead(JOY_Y);

  if (x < 400) Base.write(Base.read() - 1);
  if (x > 600) Base.write(Base.read() + 1);

  if (y < 400) Shoulder.write(Shoulder.read() - 1);
  if (y > 600) Shoulder.write(Shoulder.read() + 1);

  delay(10);
}

// ==========================================================
// ------------------------- SETUP --------------------------
// ==========================================================
void setup() {

  // PREVENT SERVO TWITCH:
  // Write safe known values BEFORE attaching
  Base.write(homePose[0]);
  Shoulder.write(homePose[1]);
  Elbow.write(homePose[2]);
  Wrist.write(homePose[3]);
  Gripper.write(gripOpen);

  delay(500);  // let Arduino initialize fully

  // NOW attach (prevents startup jump)
  Base.attach(PIN_BASE);
  Shoulder.attach(PIN_SHOULDER);
  Elbow.attach(PIN_ELBOW);
  Wrist.attach(PIN_WRIST);
  Gripper.attach(PIN_GRIPPER);

  pinMode(BTN_ACTION1, INPUT_PULLUP);
  pinMode(BTN_ACTION2, INPUT_PULLUP);
  pinMode(BTN_ACTION3, INPUT_PULLUP);

  moveToPose(homePose, 5);  // go to home immediately
}

// ==========================================================
// -------------------------- LOOP ---------------------------
// ==========================================================
void loop() {

  if (joystickMode) {
    joystickControl();
    return;
  }

  if (digitalRead(BTN_ACTION1) == LOW) {
    doAction1();
    delay(1000);
  }

  if (digitalRead(BTN_ACTION2) == LOW) {
    doAction2();
    delay(1000);
  }

  if (digitalRead(BTN_ACTION3) == LOW) {
    doAction3();
    delay(1000);
  }
}
