import tkinter as tk 
import serial
import time

SERIAL_PORT = "COM5"
BAUD_RATE = 115200

ser = None
ready = False

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"✔ Connected to {SERIAL_PORT}")
except Exception as e:
    print("⚠ Serial error:", e)
    ser = None


# ---------------------------------------------------------
# SEND DISPLAY COMMAND TO ARDUINO (MAX7219 MATRIX)
# ---------------------------------------------------------
def display(text):
    if ser:
        cmd = f"DISPLAY:{text}\n"
        ser.write(cmd.encode())
        time.sleep(0.05)


# ---------------------------------------------------------
# SEND ANGLES AND SMOOTH MOVEMENT
# ---------------------------------------------------------

def send_angles(a1, a2, a3, a4, a5):
    if not ready:
        return
    if ser:
        msg = f"{int(a1)},{int(a2)},{int(a3)},{int(a4)},{int(a5)}\n"
        ser.write(msg.encode())


def smooth_move(slider, target):
    current = slider.get()
    step = 1 if target > current else -1

    for angle in range(current, target, step):
        slider.set(angle)
        send_angles(s1.get(), s2.get(), s3.get(), s4.get(), s5.get())
        time.sleep(0.02)

    slider.set(target)
    send_angles(s1.get(), s2.get(), s3.get(), s4.get(), s5.get())


def move_all_slow(targets):
    sliders = [s1, s2, s3, s4, s5]
    for slider, target in zip(sliders, targets):
        smooth_move(slider, target)


# ---------------------------------------------------------
# BASIC COMMANDS
# ---------------------------------------------------------

def slider_changed(val):
    global ready
    ready = True
    send_angles(s1.get(), s2.get(), s3.get(), s4.get(), s5.get())


def go_home():
    global ready
    ready = True
    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


# ---------------------------------------------------------
# ACTIONS A, B, C WITH DISPLAY UPDATES
# ---------------------------------------------------------

def actionA():
    global ready
    ready = True

    display("A")
    move_all_slow([90, 150, 112, 115, 90])
    time.sleep(4)

    display("A")
    move_all_slow([90, 150, 112, 55, 90])
    time.sleep(4)

    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


def actionB():
    global ready
    ready = True

    display("B")
    move_all_slow([90, 150, 112, 115, 90])
    time.sleep(4)

    display("B")
    move_all_slow([90, 150, 112, 55, 90])
    time.sleep(4)

    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


def actionC():
    global ready
    ready = True

    display("C")
    move_all_slow([90, 150, 112, 115, 90])
    time.sleep(4)

    display("C")
    move_all_slow([90, 150, 112, 55, 90])
    time.sleep(4)

    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


# ---------------------------------------------------------
# GUI SETUP
# ---------------------------------------------------------

root = tk.Tk()
root.title("Servo Controller")
root.geometry("420x620")

DEFAULT_ANGLE = 90

s1 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="PITCH", command=slider_changed); s1.set(DEFAULT_ANGLE)
s2 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="LINK 1", command=slider_changed); s2.set(DEFAULT_ANGLE)
s3 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="LINK 2", command=slider_changed); s3.set(DEFAULT_ANGLE)
s4 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="BASE", command=slider_changed); s4.set(DEFAULT_ANGLE)
s5 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="GRIPPER", command=slider_changed); s5.set(DEFAULT_ANGLE)

s1.pack(fill="x", padx=20)
s2.pack(fill="x", padx=20)
s3.pack(fill="x", padx=20)
s4.pack(fill="x", padx=20)
s5.pack(fill="x", padx=20)

btn_home = tk.Button(root, text="HOME", font=("Arial", 14, "bold"), command=go_home, bg="#d0d0ff")
btn_home.pack(pady=10)

btn_actionA = tk.Button(root, text="ACTION A", font=("Arial", 14, "bold"), command=actionA, bg="#ffd0d0")
btn_actionA.pack(pady=10)

btn_actionB = tk.Button(root, text="ACTION B", font=("Arial", 14, "bold"), command=actionB, bg="#d0ffd0")
btn_actionB.pack(pady=10)

btn_actionC = tk.Button(root, text="ACTION C", font=("Arial", 14, "bold"), command=actionC, bg="#d0d0ff")
btn_actionC.pack(pady=10)

warning_label = tk.Label(
    root,
    text="⚠ ENSURE ROBOT IS HOMED BEFORE POWERING OFF",
    font=("Arial", 11, "bold"),
    fg="yellow",
    bg="black"
)
warning_label.pack(pady=10)

root.mainloop()
