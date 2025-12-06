#include <Servo.h>
#include <LedControl.h>
#include <binary.h>

// MAX7219 8×8 LED MATRIX
// DIN = 12, CLK = 11, CS = 10
LedControl lc = LedControl(12, 11, 10, 1);

// SERVOS
Servo s1, s2, s3, s4, s5;

int currentPos[5] = {90, 90, 90, 90, 90};
int targetPos[5]  = {90, 90, 90, 90, 90};

const int STEP_SIZE = 2;
const unsigned long STEP_DT = 20;

unsigned long lastStepTime = 0;
bool firstCommandReceived = false;

// ============================================================
// 8×8 PATTERNS
// ============================================================

// HAPPY FACE 🙂
byte smile[8] = {
  B00111100,
  B01000010,
  B10100101,
  B10000001,
  B10100101,
  B10011001,
  B01000010,
  B00111100
};

// LETTER A
byte letterA[8] = {
  B00011000,
  B00100100,
  B01000010,
  B01000010,
  B01111110,
  B01000010,
  B01000010,
  B01000010
};

// LETTER B
byte letterB[8] = {
  B01111100,
  B01000010,
  B01000010,
  B01111100,
  B01000010,
  B01000010,
  B01000010,
  B01111100
};

// LETTER C
byte letterC[8] = {
  B00111100,
  B01000010,
  B01000000,
  B01000000,
  B01000000,
  B01000000,
  B01000010,
  B00111100
};


// ============================================================
// DRAW AN 8×8 IMAGE
// ============================================================
void drawImage(byte img[8]) {
  for (int row = 0; row < 8; row++) {
    lc.setRow(0, row, img[row]);
  }
}


// ============================================================
// DISPLAY COMMAND HANDLER
// ============================================================
void displayText(String txt) {
  txt.toUpperCase();

  if (txt == "A") {
    drawImage(letterA);
    return;
  }
  if (txt == "B") {
    drawImage(letterB);
    return;
  }
  if (txt == "C") {
    drawImage(letterC);
    return;
  }
  if (txt == ":)" || txt == "SMILE" || txt == "IDLE") {
    drawImage(smile);
    return;
  }

  // DEFAULT = smile
  drawImage(smile);
}


// ============================================================
// INITIALIZATION
// ============================================================
void setup() {
  Serial.begin(115200);

  // MATRIX INIT
  lc.shutdown(0, false);
  lc.setIntensity(0, 8);
  lc.clearDisplay(0);
  drawImage(smile);   // idle face at startup

  // SERVOS
  s1.attach(2);
  s2.attach(3);
  s3.attach(4);
  s4.attach(5);
  s5.attach(6);
}


// ============================================================
// MAIN LOOP
// ============================================================
void loop() {

  // ----------------------------------------------------------
  // 1. READ SERIAL INPUT
  // ----------------------------------------------------------
  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');

    // If Python sends a display command
    if (data.startsWith("DISPLAY:")) {
      String txt = data.substring(8);
      displayText(txt);
      return;
    }

    // Otherwise it is servo movement
    int c1 = data.indexOf(',');
    int c2 = data.indexOf(',', c1 + 1);
    int c3 = data.indexOf(',', c2 + 1);
    int c4 = data.indexOf(',', c3 + 1);

    if (c1 > 0 && c2 > 0 && c3 > 0 && c4 > 0) {

      targetPos[0] = data.substring(0,      c1).toInt();
      targetPos[1] = data.substring(c1 + 1, c2).toInt();
      targetPos[2] = data.substring(c2 + 1, c3).toInt();
      targetPos[3] = data.substring(c3 + 1, c4).toInt();
      targetPos[4] = data.substring(c4 + 1).toInt();

      // First command: prevent snapping
      if (!firstCommandReceived) {
        for (int i = 0; i < 5; i++) {
          currentPos[i] = targetPos[i];
        }
        writeAllServos();
        firstCommandReceived = true;
      }
    }
  }


  // ----------------------------------------------------------
  // 2. SMOOTH SERVO STEPPING
  // ----------------------------------------------------------
  if (!firstCommandReceived) return;

  unsigned long now = millis();
  if (now - lastStepTime >= STEP_DT) {
    lastStepTime = now;

    bool needUpdate = false;

    for (int i = 0; i < 5; i++) {

      if (currentPos[i] < targetPos[i]) {
        currentPos[i] += STEP_SIZE;
        if (currentPos[i] > targetPos[i])
          currentPos[i] = targetPos[i];
        needUpdate = true;
      }
      else if (currentPos[i] > targetPos[i]) {
        currentPos[i] -= STEP_SIZE;
        if (currentPos[i] < targetPos[i])
          currentPos[i] = targetPos[i];
        needUpdate = true;
      }
    }

    if (needUpdate) {
      writeAllServos();
    }
  }
}


// ============================================================
// UPDATE SERVOS
// ============================================================
void writeAllServos() {
  s1.write(currentPos[0]);
  s2.write(currentPos[1]);
  s3.write(currentPos[2]);
  s4.write(currentPos[3]);
  s5.write(currentPos[4]);
}
