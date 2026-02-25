import tkinter as tk
from tkinter import ttk, messagebox
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
        ports.append(p.device)  # e.g., "COM5"
    return ports


def connect_serial():
    """Connect using the selected COM port."""
    global ser, ready

    port = port_var.get().strip()
    if not port:
        messagebox.showwarning("No COM Port", "Select a COM port first.")
        return

    # Close previous connection if any
    if ser and ser.is_open:
        try:
            ser.close()
        except Exception:
            pass

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)  # allow Arduino reset on connect
        ready = True
        status_var.set(f"Connected: {port} @ {BAUD_RATE}")
        print(f"✔ Connected to {port}")
    except Exception as e:
        ser = None
        ready = False
        status_var.set("Not connected")
        messagebox.showerror("Serial Error", f"Could not connect to {port}\n\n{e}")
        print("⚠ Serial error:", e)


def disconnect_serial():
    global ser, ready
    ready = False
    if ser and ser.is_open:
        try:
            ser.close()
        except Exception:
            pass
    ser = None
    status_var.set("Not connected")


def refresh_ports():
    ports = list_com_ports()
    port_combo["values"] = ports
    if ports:
        # Keep current selection if still valid; otherwise select first
        current = port_var.get()
        if current not in ports:
            port_var.set(ports[0])
    else:
        port_var.set("")


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
# ---------------------------------------------------------
def send_angles(a1, a2, a3, a4, a5):
    if not ready:
        return
    if ser and ser.is_open:
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
def slider_changed(_val):
    global ready
    # Do not force ready=True if not connected; only send when connected
    if ser and ser.is_open:
        ready = True
        send_angles(s1.get(), s2.get(), s3.get(), s4.get(), s5.get())


def go_home():
    global ready
    if not (ser and ser.is_open):
        messagebox.showwarning("Not connected", "Connect to a COM port first.")
        return
    ready = True
    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


# ---------------------------------------------------------
# ACTIONS A, B, C WITH DISPLAY UPDATES
# ---------------------------------------------------------
def actionA():
    global ready
    if not (ser and ser.is_open):
        messagebox.showwarning("Not connected", "Connect to a COM port first.")
        return
    ready = True

    display("A")  # GO RIGHT
    move_all_slow([90, 155, 105, 115, 90])
    time.sleep(1)

    display("A")  # GO LEFT
    move_all_slow([90, 155, 105, 70, 90])
    time.sleep(1)

    display("A")  # GO RIGHT
    move_all_slow([90, 155, 105, 115, 90])
    time.sleep(1)

    display("A")  # GO LEFT
    move_all_slow([90, 155, 105, 70, 90])
    time.sleep(1)

    display("A")  # GO RIGHT
    move_all_slow([90, 155, 105, 115, 90])
    time.sleep(1)

    display("A")  # GO LEFT
    move_all_slow([90, 155, 105, 70, 90])
    time.sleep(1)

    display("A")  # GO CENTER
    move_all_slow([90, 156, 90, 100, 90])

    display("A")  # GO CENTER DOWN
    move_all_slow([90, 156, 110, 100, 90])

    display("A")  # GO CENTER
    move_all_slow([90, 156, 90, 100, 90])

    display("A")  # GO CENTER DOWN
    move_all_slow([90, 156, 110, 100, 90])

    display("A")  # GO CENTER
    move_all_slow([90, 156, 90, 100, 90])

    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


def actionB():
    global ready
    if not (ser and ser.is_open):
        messagebox.showwarning("Not connected", "Connect to a COM port first.")
        return
    ready = True

    display("B")  # GO CENTER
    move_all_slow([90, 156, 90, 100, 90])
    time.sleep(1)

    display("B")  # GO HOME
    move_all_slow([90, 90, 90, 90, 90])
    time.sleep(1)

    display("B")  # GO CENTER
    move_all_slow([90, 156, 90, 100, 90])
    time.sleep(1)

    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


def actionC():
    global ready
    if not (ser and ser.is_open):
        messagebox.showwarning("Not connected", "Connect to a COM port first.")
        return
    ready = True

    display("C")
    move_all_slow([90, 59, 164, 48, 90])
    time.sleep(2)

    display("C")
    move_all_slow([90, 90, 90, 90, 90])
    time.sleep(2)

    display("C")
    move_all_slow([90, 64, 166, 153, 90])
    time.sleep(2)

    display("SMILE")
    move_all_slow([90, 90, 90, 90, 90])


# ---------------------------------------------------------
# GUI SETUP
# ---------------------------------------------------------
root = tk.Tk()
root.title("Servo Controller")
root.geometry("460x700")

# --- Serial connection bar ---
top = tk.Frame(root)
top.pack(fill="x", padx=12, pady=10)

tk.Label(top, text="COM Port:", font=("Arial", 10, "bold")).pack(side="left")

port_var = tk.StringVar(value="")
port_combo = ttk.Combobox(top, textvariable=port_var, width=12, state="readonly")
port_combo.pack(side="left", padx=6)

btn_refresh = tk.Button(top, text="Refresh", command=refresh_ports)
btn_refresh.pack(side="left", padx=6)

btn_connect = tk.Button(top, text="Connect", command=connect_serial)
btn_connect.pack(side="left", padx=6)

btn_disconnect = tk.Button(top, text="Disconnect", command=disconnect_serial)
btn_disconnect.pack(side="left", padx=6)

status_var = tk.StringVar(value="Not connected")
status_lbl = tk.Label(root, textvariable=status_var, anchor="w")
status_lbl.pack(fill="x", padx=12)

# Populate COM ports on launch
refresh_ports()

DEFAULT_ANGLE = 90

s1 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="GRIPPER", command=slider_changed)
s2 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="ROTATION", command=slider_changed)
s3 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="LINK 2", command=slider_changed)
s4 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="LINK 1", command=slider_changed)
s5 = tk.Scale(root, from_=0, to=180, orient="horizontal", label="BASE", command=slider_changed)

for s in (s1, s2, s3, s4, s5):
    s.set(DEFAULT_ANGLE)
    s.pack(fill="x", padx=20, pady=4)

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


def on_close():
    disconnect_serial()
    root.destroy()


root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
