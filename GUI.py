import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import time

BAUD_RATE = 115200

ser = None
ready = False
relay_state = False   # False = OFF, True = ON


# ---------------------------------------------------------
# SERIAL HELPERS
# ---------------------------------------------------------
def list_com_ports():
    return [p.device for p in serial.tools.list_ports.comports()]


def connect_serial():
    global ser, ready

    port = port_var.get().strip()
    if not port:
        messagebox.showwarning("No COM Port", "Select a COM port first.")
        return

    if ser and ser.is_open:
        ser.close()

    try:
        ser = serial.Serial(port, BAUD_RATE, timeout=1)
        time.sleep(2)
        ready = True
        status_var.set(f"Connected: {port} @ {BAUD_RATE}")
        print(f"✔ Connected to {port}")
    except Exception as e:
        ser = None
        ready = False
        status_var.set("Not connected")
        messagebox.showerror("Serial Error", f"Could not connect to {port}\n\n{e}")


def disconnect_serial():
    global ser, ready
    ready = False
    if ser and ser.is_open:
        ser.close()
    ser = None
    status_var.set("Not connected")


def refresh_ports():
    ports = list_com_ports()
    port_combo["values"] = ports
    if ports:
        if port_var.get() not in ports:
            port_var.set(ports[0])
    else:
        port_var.set("")


# ---------------------------------------------------------
# RELAY CONTROL
# ---------------------------------------------------------
def toggle_relay():
    global relay_state

    if not (ser and ser.is_open):
        messagebox.showwarning("Not connected", "Connect to a COM port first.")
        return

    if relay_state:
        ser.write(b"RELAY:OFF\n")
        relay_btn.config(text="RELAY OFF", bg="red")
        relay_state = False
    else:
        ser.write(b"RELAY:ON\n")
        relay_btn.config(text="RELAY ON", bg="green")
        relay_state = True


# ---------------------------------------------------------
# DISPLAY COMMAND
# ---------------------------------------------------------
def display(text):
    if ser and ser.is_open:
        cmd = f"DISPLAY:{text}\n"
        ser.write(cmd.encode())
        time.sleep(0.05)


# ---------------------------------------------------------
# SERVO CONTROL
# ---------------------------------------------------------
def send_angles(a1, a2, a3, a4, a5):
    if ready and ser and ser.is_open:
        msg = f"{int(a1)},{int(a2)},{int(a3)},{int(a4)},{int(a5)}\n"
        ser.write(msg.encode())


def slider_changed(_val):
    if ser and ser.is_open:
        send_angles(s1.get(), s2.get(), s3.get(), s4.get(), s5.get())


def go_home():
    if not (ser and ser.is_open):
        messagebox.showwarning("Not connected", "Connect first.")
        return
    display("SMILE")
    send_angles(90, 90, 90, 90, 90)


# ---------------------------------------------------------
# GUI SETUP
# ---------------------------------------------------------
root = tk.Tk()
root.title("Servo + Relay Controller")
root.geometry("460x760")

# Serial bar
top = tk.Frame(root)
top.pack(fill="x", padx=12, pady=10)

tk.Label(top, text="COM Port:", font=("Arial", 10, "bold")).pack(side="left")

port_var = tk.StringVar(value="")
port_combo = ttk.Combobox(top, textvariable=port_var, width=12, state="readonly")
port_combo.pack(side="left", padx=6)

tk.Button(top, text="Refresh", command=refresh_ports).pack(side="left", padx=6)
tk.Button(top, text="Connect", command=connect_serial).pack(side="left", padx=6)
tk.Button(top, text="Disconnect", command=disconnect_serial).pack(side="left", padx=6)

status_var = tk.StringVar(value="Not connected")
tk.Label(root, textvariable=status_var).pack(fill="x", padx=12)

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

tk.Button(root, text="HOME", font=("Arial", 14, "bold"), command=go_home, bg="#d0d0ff").pack(pady=10)

# ---------------------------------------------------------
# 🔴 RELAY BUTTON (BIG)
# ---------------------------------------------------------
relay_btn = tk.Button(
    root,
    text="RELAY OFF",
    font=("Arial", 18, "bold"),
    bg="red",
    fg="white",
    height=2,
    command=toggle_relay
)
relay_btn.pack(pady=20, fill="x", padx=40)


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
