import tkinter as tk
from tkinter import ttk
import serial
import serial.tools.list_ports
import time

BAUD_RATE = 115200

ser = None
ready = False

# ---------------------------------------------------------
# SERIAL HELPERS
# ---------------------------------------------------------
def list_com_ports():
    ports = []
    for p in serial.tools.list_ports.comports():
        # show something like: "COM5 - Arduino Mega 2560 (CH340)"
        desc = p.description if p.description else ""
        ports.append(f"{p.device} - {desc}".strip(" -"))
    return ports

def selected_port_device():
    # Extract "COM5" from "COM5 - Arduino..."
    val = port_var.get().strip()
    if not val:
        return ""
    return val.split(" - ")[0].strip()

def connect_serial():
    global ser, ready
    ready = False

    # Close any existing connection
    if ser and ser.is_open:
        try:
            ser.close()
        except:
            pass
        ser = None

    dev = selected_port_device()
    if not dev:
        status_var.set("⚠ Select a COM port first.")
        return

    try:
        ser = serial.Serial(dev, BAUD_RATE, timeout=1)
        time.sleep(2)
        status_var.set(f"✔ Connected to {dev} @ {BAUD_RATE}")
    except Exception as e:
        ser = None
        status_var.set(f"⚠ Serial error: {e}")

def refresh_ports():
    ports = list_com_ports()
    port_combo["values"] = ports
    if ports and not port_var.get():
        port_var.set(ports[0])
    status_var.set("Ports refreshed.")

# ---------------------------------------------------------
# SEND DISPLAY COMMAND TO ARDUINO (MAX7219 MATRIX)
# ---------------------------------------------------------
def display(text):
    if ser and ser.is_open:
        cmd = f"DISPLAY:{text}\n"
        ser.write(cmd.encode())
        time.sleep(0.05)

# ---------------------------------------------------------
# SEND ANGLES AND SMOOTH MOVEMENT
# ORDER MUST MATCH ARDUINO:
#   a1 -> S1 (PIN 10) GRIPPER
#   a2 -> S2 (PIN 9)  ROTATION
#   a3 -> S3 (PIN 8)  LINK 2
#   a4 -> S4 (PIN 7)  LINK 1
#   a5 -> S5 (PIN 6)  BASE
# ---------------------------------------------------------
def send_angles(a1, a2, a3, a4, a5):
    if not ready:
        return
    if ser and ser.is_open:
        msg = f"{int(a1)},{int(a2)},{int(a3)},{int(a4)},{int(a5)}\n"
        ser.write(msg.encode())

def smooth_move(slider, target):
    current = int(slider.get())
    target = int(target)
    if current == target:
        send_angles(gripper.get(), rotation.get(), link2.get(), link1.get(), base.get())
        return

    step = 1 if target > current else -1
    for angle in range(current, target, step):
        slider.set(angle)
        send_angles(gripper.get(), rotation.get(), link2.get(), link1.get(), base.get())
        time.sleep(0.02)

    slider.set(target)
    send_angles(gripper.get(), rotation.get(), link2.get(), link1.get(), base.get())

def move_all_slow(targets):
    sliders = [gripper, rotation, link2, link1, base]
    for slider, target in zip(sliders, targets):
        smooth_move(slider, target)

# ---------------------------------------------------------
# BASIC COMMANDS
# ---------------------------------------------------------
def slider_changed(_val=None):
    global ready
    ready = True
    send_angles(gripper.get(), rotation.get(), link2.get(), link1.get(), base.get())

def go_home():
    global ready
    ready = True
    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])

# ---------------------------------------------------------
# ACTIONS A, B, C WITH DISPLAY UPDATES (UNCHANGED ANGLE LISTS)
# BUT NOW THEY MAP TO:
# [GRIPPER, ROTATION, LINK2, LINK1, BASE]
# ---------------------------------------------------------
def actionA():
    global ready
    ready = True

    display("A")
    move_all_slow([90, 150, 120, 90, 120]) #MOVE TO PICK UP
    time.sleep(.5)
    
    move_all_slow([115, 150, 120, 90, 120]) #CLOSE GRIPPER AT PICK UP
    time.sleep(.5)
    
    move_all_slow([115, 150, 120, 90, 75]) #MOVE TO DROP
    time.sleep(.5)
    
    move_all_slow([60, 150, 120, 90, 75]) #OPEN GRIPPER
    time.sleep(.5)
    
    move_all_slow([60, 150, 120, 90, 120]) #MOVE TO PICK UP
    time.sleep(.5)
    
    move_all_slow([115, 150, 120, 90, 120]) #CLOSE GRIPPER AT PICK UP
    time.sleep(.5)
    
    move_all_slow([115, 150, 120, 90, 75]) #MOVE TO DROP
    time.sleep(.5)
    
    move_all_slow([60, 150, 120, 90, 75]) #OPEN GRIPPER
    time.sleep(.5)
    move_all_slow([60, 90, 90, 90, 90]) #KEEP GRIPPER OPEN FOR CLEAR

    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


def actionB():
    global ready
    ready = True

    display("B")
    move_all_slow([90, 90, 152, 90, 130]) #LEFT
    time.sleep(.5)
    
    move_all_slow([115, 90, 152, 90, 130]) #LEFT GRAB
    time.sleep(.5)
    
    move_all_slow([115, 90, 152, 90, 50]) #RIGHT
    time.sleep(.5)
    
    move_all_slow([60, 90, 152, 90, 50]) #RIGHT DROP
    time.sleep(.5)
    
    move_all_slow([60, 90, 152, 90, 130]) #LEFT
    time.sleep(.5)
    
    move_all_slow([115, 90, 152, 90, 130]) #LEFT GRAB
    time.sleep(.5)
    
    move_all_slow([115, 90, 152, 90, 50]) #RIGHT
    time.sleep(.5)
    
    move_all_slow([60, 90, 152, 90, 50]) #RIGHT DROP
    time.sleep(.5)
    
    move_all_slow([60, 90, 152, 90, 130]) #LEFT
    time.sleep(.5)
    
    move_all_slow([115, 90, 152, 90, 130]) #LEFT GRAB
    time.sleep(.5)
    
    move_all_slow([115, 90, 152, 90, 50]) #RIGHT
    time.sleep(.5)
    
    move_all_slow([60, 90, 152, 90, 50]) #RIGHT DROP
    time.sleep(.5)
    
    move_all_slow([60, 90, 90, 90, 90])

    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])

def actionC():
    global ready
    ready = True

    display("C")
    move_all_slow([90, 134, 151, 90, 125]) #START

    move_all_slow([115, 134, 151, 90, 125])

    move_all_slow([115, 134, 115, 90, 77])

    move_all_slow([115, 134, 115, 90, 77])

    move_all_slow([90, 134, 115, 90, 77])
    
    move_all_slow([90, 134, 151, 90, 125]) #START

    move_all_slow([115, 134, 151, 90, 125])

    move_all_slow([115, 134, 115, 90, 77])

    move_all_slow([115, 134, 115, 90, 77])

    move_all_slow([90, 134, 115, 90, 77])
    
    move_all_slow([90, 134, 151, 90, 125]) #START

    move_all_slow([115, 134, 151, 90, 125])

    move_all_slow([115, 134, 115, 90, 77])

    move_all_slow([115, 134, 115, 90, 77])

    move_all_slow([90, 134, 115, 90, 77])
    
    move_all_slow([90, 134, 151, 90, 125]) #START

    move_all_slow([115, 134, 151, 90, 125])

    move_all_slow([115, 134, 115, 90, 77])

    move_all_slow([115, 134, 115, 90, 77])

    move_all_slow([90, 134, 115, 90, 77])
    
    move_all_slow([90, 120, 140, 90, 90])
    move_all_slow([90, 120, 155, 90, 90])
    move_all_slow([90, 120, 140, 90, 90])
    move_all_slow([90, 120, 155, 90, 90])
    move_all_slow([90, 120, 140, 90, 90])
    move_all_slow([90, 120, 155, 90, 90])
    time.sleep(.5)


    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])

# ---------------------------------------------------------
# GUI SETUP
# ---------------------------------------------------------
root = tk.Tk()
root.title("Servo Controller")
root.geometry("460x720")

DEFAULT_ANGLE = 90

# ---- Serial frame (COM dropdown + buttons)
serial_frame = tk.LabelFrame(root, text="Serial", padx=10, pady=10)
serial_frame.pack(fill="x", padx=15, pady=10)

port_var = tk.StringVar(value="")
port_combo = ttk.Combobox(serial_frame, textvariable=port_var, state="readonly", width=45)
port_combo.grid(row=0, column=0, columnspan=3, sticky="we", padx=5, pady=5)

btn_refresh = tk.Button(serial_frame, text="Refresh Ports", command=refresh_ports)
btn_refresh.grid(row=1, column=0, sticky="we", padx=5, pady=5)

btn_connect = tk.Button(serial_frame, text="Connect", command=connect_serial)
btn_connect.grid(row=1, column=1, sticky="we", padx=5, pady=5)

status_var = tk.StringVar(value="Select a COM port, then Connect.")
status_label = tk.Label(serial_frame, textvariable=status_var, anchor="w")
status_label.grid(row=2, column=0, columnspan=3, sticky="we", padx=5, pady=5)

serial_frame.columnconfigure(0, weight=1)
serial_frame.columnconfigure(1, weight=1)
serial_frame.columnconfigure(2, weight=1)

# Populate ports on startup
refresh_ports()

# ---- Sliders frame
sliders_frame = tk.LabelFrame(root, text="Servos (Pins: 10, 9, 8, 7, 6)", padx=10, pady=10)
sliders_frame.pack(fill="x", padx=15, pady=10)

# Labels requested:
# 10 GRIPPER, 9 ROTATION, 8 LINK 2, 7 LINK 1, 6 BASE
gripper  = tk.Scale(sliders_frame, from_=60, to=125, orient="horizontal", label="GRIPPER (S1 Pin 10)", command=slider_changed);  gripper.set(DEFAULT_ANGLE)
rotation = tk.Scale(sliders_frame, from_=0, to=180, orient="horizontal", label="LINK 1 (S2 Pin 9)", command=slider_changed); rotation.set(DEFAULT_ANGLE)
link2    = tk.Scale(sliders_frame, from_=0, to=180, orient="horizontal", label="LINK 2 (S3 Pin 8)", command=slider_changed);    link2.set(DEFAULT_ANGLE)
link1    = tk.Scale(sliders_frame, from_=0, to=180, orient="horizontal", label="EMPTY (S4 Pin 7)", command=slider_changed);    link1.set(DEFAULT_ANGLE)
base     = tk.Scale(sliders_frame, from_=0, to=180, orient="horizontal", label="BASE (S5 Pin 6)", command=slider_changed);       base.set(DEFAULT_ANGLE)

for w in (gripper, rotation, link2, link1, base):
    w.pack(fill="x", padx=10, pady=4)

# ---- Buttons
btn_home = tk.Button(root, text="HOME", font=("Arial", 14, "bold"), command=go_home, bg="#d0d0ff")
btn_home.pack(pady=8)

btn_actionA = tk.Button(root, text="ACTION A", font=("Arial", 14, "bold"), command=actionA, bg="#ffd0d0")
btn_actionA.pack(pady=8)

btn_actionB = tk.Button(root, text="ACTION B", font=("Arial", 14, "bold"), command=actionB, bg="#d0ffd0")
btn_actionB.pack(pady=8)

btn_actionC = tk.Button(root, text="ACTION C", font=("Arial", 14, "bold"), command=actionC, bg="#d0d0ff")
btn_actionC.pack(pady=8)

warning_label = tk.Label(
    root,
    text="⚠ ENSURE ROBOT IS HOMED BEFORE POWERING OFF",
    font=("Arial", 11, "bold"),
    fg="yellow",
    bg="black"
)
warning_label.pack(pady=12, fill="x", padx=15)

root.mainloop()
