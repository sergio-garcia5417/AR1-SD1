#include <Servo.h>
#include <LedControl.h>

// ============================================================
// PIN MAP (YOUR NEW WIRING)
// ============================================================
// MAX7219 8×8 LED MATRIX
// DIN = 11, CS = 12, CLK = 13
const int MATRIX_DIN = 11;
const int MATRIX_CLK = 13;
const int MATRIX_CS  = 12;

// SERVOS
// S1 = 10, S2 = 9, S3 = 8, S4 = 7, S5 = 6
const int S1_PIN = 10;
const int S2_PIN = 9;
const int S3_PIN = 8;
const int S4_PIN = 7;
const int S5_PIN = 6;

// LedControl(DIN, CLK, CS, numberOfDevices)
LedControl lc = LedControl(MATRIX_DIN, MATRIX_CLK, MATRIX_CS, 1);

// SERVOS
Servo s1, s2, s3, s4, s5;

int currentPos[5] = {90, 90, 90, 90, 90};
int targetPos[5]  = {90, 90, 90, 90, 90};

const int STEP_SIZE = 2;
const unsigned long STEP_DT = 20;

unsigned long lastStepTime = 0;
bool firstCommandReceived = false;

// ============================================================
// IDLE SCROLL ANIMATION SETTINGS (LANL SRNS)
// ============================================================
bool idleAnimEnabled = true;
unsigned long idleLastStep = 0;
const unsigned long IDLE_STEP_MS = 80;
int idleColIndex = 0;
byte idleFrame[8] = {0,0,0,0,0,0,0,0};

// ============================================================
// 8×8 PATTERNS (STATIC LETTERS FOR A/B/C COMMANDS)
// ============================================================
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
// BIT HELPERS (FOR FLIPPING IMAGE)
// ============================================================
byte reverseByte(byte b) {
  b = (b & 0xF0) >> 4 | (b & 0x0F) << 4;
  b = (b & 0xCC) >> 2 | (b & 0x33) << 2;
  b = (b & 0xAA) >> 1 | (b & 0x55) << 1;
  return b;
}

// ============================================================
// DRAW AN 8×8 IMAGE (FLIPPED 180° TO FIX UPSIDE-DOWN DISPLAY)
// ============================================================
void drawImageFlipped(const byte img[8]) {
  for (int row = 0; row < 8; row++) {
    byte flippedRow = reverseByte(img[7 - row]);
    lc.setRow(0, row, flippedRow);
  }
}

// ============================================================
// SCROLLING GLYPHS (5 columns each), stored as COLUMNS
// Each byte is vertical bits: bit0=top row, bit6=bottom row, bit7 unused.
// ============================================================

// LANL
const byte GLYPH_L[5] = { B01111111, B01000000, B01000000, B01000000, B01000000 };
const byte GLYPH_A[5] = { B01111110, B00010001, B00010001, B00010001, B01111110 };

// N HORIZONTALLY FLIPPED (requested): reverse column order
const byte GLYPH_N[5] = { B01111111, B00000010, B00000100, B00001000, B01111111 };

// SRNS
// S VERTICALLY FLIPPED (requested): top↔bottom bits (resulting columns below)
const byte GLYPH_S[5] = {
  B01000110,
  B01001001,
  B01001001,
  B01001001,
  B00110001
};
const byte GLYPH_R[5] = { B01111111, B00001001, B00011001, B00101001, B01000110 };

// ============================================================
// MESSAGE LAYOUT: "LANL SRNS"
// ============================================================
const int IDLE_LEADING_BLANKS  = 8;
const int IDLE_TRAILING_BLANKS = 8;

const int LETTER_W = 5;
const int COL_SPACING = 1;        // do NOT name this SP on AVR
const int GAP_BETWEEN_WORDS = 2;  // extra gap after LANL

const int LANL_COLS = (LETTER_W + COL_SPACING) * 4 - COL_SPACING; // 23
const int SRNS_COLS = (LETTER_W + COL_SPACING) * 4 - COL_SPACING; // 23

const int IDLE_TOTAL_COLS =
  IDLE_LEADING_BLANKS +
  LANL_COLS +
  GAP_BETWEEN_WORDS +
  SRNS_COLS +
  IDLE_TRAILING_BLANKS;

// ============================================================
// SCROLL ENGINE (NON-BLOCKING)
// ============================================================
void shiftFrameLeft(byte frame[8], byte newCol) {
  for (int r = 0; r < 8; r++) {
    byte bit = (newCol >> r) & 0x01;
    frame[r] = (byte)((frame[r] << 1) | bit);
  }
}

void drawFrameFlipped(const byte frame[8]) {
  for (int row = 0; row < 8; row++) {
    byte flippedRow = reverseByte(frame[7 - row]);
    lc.setRow(0, row, flippedRow);
  }
}

byte idleNextColumn(int colIndex) {
  int idx = colIndex - IDLE_LEADING_BLANKS;
  if (idx < 0) return 0x00;

  // ---- LANL (23 cols)
  if (idx >= 0 && idx < LANL_COLS) {
    if (idx >= 0 && idx <= 4) return GLYPH_L[idx];
    if (idx == 5) return 0x00;

    if (idx >= 6 && idx <= 10) return GLYPH_A[idx - 6];
    if (idx == 11) return 0x00;

    if (idx >= 12 && idx <= 16) return GLYPH_N[idx - 12];
    if (idx == 17) return 0x00;

    if (idx >= 18 && idx <= 22) return GLYPH_L[idx - 18];
    return 0x00;
  }

  // ---- gap
  idx -= LANL_COLS;
  if (idx < GAP_BETWEEN_WORDS) return 0x00;

  // ---- SRNS (23 cols)
  idx -= GAP_BETWEEN_WORDS;
  if (idx >= 0 && idx < SRNS_COLS) {
    if (idx >= 0 && idx <= 4) return GLYPH_S[idx];
    if (idx == 5) return 0x00;

    if (idx >= 6 && idx <= 10) return GLYPH_R[idx - 6];
    if (idx == 11) return 0x00;

    if (idx >= 12 && idx <= 16) return GLYPH_N[idx - 12];
    if (idx == 17) return 0x00;

    if (idx >= 18 && idx <= 22) return GLYPH_S[idx - 18];
    return 0x00;
  }

  return 0x00;
}

void idleAnimReset() {
  for (int i = 0; i < 8; i++) idleFrame[i] = 0x00;
  idleColIndex = 0;
  idleLastStep = millis();
  drawFrameFlipped(idleFrame);
}

void idleAnimUpdate() {
  if (!idleAnimEnabled) return;

  unsigned long now = millis();
  if (now - idleLastStep < IDLE_STEP_MS) return;
  idleLastStep = now;

  byte col = idleNextColumn(idleColIndex);
  shiftFrameLeft(idleFrame, col);
  drawFrameFlipped(idleFrame);

  idleColIndex++;
  if (idleColIndex >= IDLE_TOTAL_COLS) idleColIndex = 0;
}

// ============================================================
// DISPLAY COMMAND HANDLER
// ============================================================
void displayText(String txt) {
  txt.trim();
  txt.toUpperCase();

  if (txt == "A") { idleAnimEnabled = false; drawImageFlipped(letterA); return; }
  if (txt == "B") { idleAnimEnabled = false; drawImageFlipped(letterB); return; }
  if (txt == "C") { idleAnimEnabled = false; drawImageFlipped(letterC); return; }

  if (txt == ":)" || txt == "SMILE" || txt == "IDLE") {
    idleAnimEnabled = true;
    idleAnimReset();
    return;
  }

  idleAnimEnabled = true;
  idleAnimReset();
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

// ============================================================
// INITIALIZATION
// ============================================================
void setup() {
  Serial.begin(115200);

  lc.shutdown(0, false);
  lc.setIntensity(0, 8);
  lc.clearDisplay(0);

  idleAnimEnabled = true;
  idleAnimReset();

  s1.attach(S1_PIN);
  s2.attach(S2_PIN);
  s3.attach(S3_PIN);
  s4.attach(S4_PIN);
  s5.attach(S5_PIN);
}

// ============================================================
// MAIN LOOP
// ============================================================
void loop() {
  idleAnimUpdate();

  if (Serial.available()) {
    String data = Serial.readStringUntil('\n');
    data.trim();

    if (data.startsWith("DISPLAY:")) {
      String txt = data.substring(8);
      displayText(txt);
    } else {
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

        if (!firstCommandReceived) {
          for (int i = 0; i < 5; i++) currentPos[i] = targetPos[i];
          writeAllServos();
          firstCommandReceived = true;
        }
      }
    }
  }

  if (!firstCommandReceived) return;

  unsigned long now = millis();
  if (now - lastStepTime >= STEP_DT) {
    lastStepTime = now;

    bool needUpdate = false;

    for (int i = 0; i < 5; i++) {
      if (currentPos[i] < targetPos[i]) {
        currentPos[i] += STEP_SIZE;
        if (currentPos[i] > targetPos[i]) currentPos[i] = targetPos[i];
        needUpdate = true;
      } else if (currentPos[i] > targetPos[i]) {
        currentPos[i] -= STEP_SIZE;
        if (currentPos[i] < targetPos[i]) currentPos[i] = targetPos[i];
        needUpdate = true;
      }
    }

    if (needUpdate) writeAllServos();
  }
}
