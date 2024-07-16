import tkinter as tk
from tkinter import messagebox, IntVar
import threading
import time
from memory import *

BASE_ADDRESS_LIFE = 0x0000E240
BASE_ADDRESS_ARMOR = 0x0000E240
BASE_ADDRESS_LUKE = 0x0016BAC0
BASE_ADDRESS_LASER = 0x0016BAC0
BASE_ADDRESS_AIRCRAFT = 0x0000E240

OFFSETS_LIFE = [0x964]
OFFSETS_ARMOR = [0x96C]
OFFSETS_LUKE = [0x304, 0x5C, 0x968]
OFFSETS_LASER = [0x12C]
OFFSETS_AIRCRAFT = [0x984]


def continuous_write(base, offsets, value, key):
    while running_states.get(key, False):
        set_value(base, offsets, value)
        time.sleep(0.5)


def set_custom_value(base, offsets, entry, checkbox_var, min_val, max_val, key):
    try:
        custom_value = int(entry.get())
        if custom_value < min_val:
            custom_value = min_val
        elif custom_value > max_val:
            custom_value = max_val

        if checkbox_var.get() == 1:
            running_states[key] = True
            threads[key] = threading.Thread(target=continuous_write, args=(base, offsets, custom_value, key))
            threads[key].start()
        else:
            running_states[key] = False
            set_value(base, offsets, custom_value)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid integer value")


def create_gui():
    root = tk.Tk()
    root.title("Pham Thanh Tung")
    icon_path = 'icon.ico'
    root.iconbitmap(icon_path)

    frame = tk.Frame(root, padx=10, pady=10)
    frame.pack(padx=10, pady=10)

    def create_entry_with_lock(frame, row, label_text, base, offsets, min_val, max_val, key):
        label = tk.Label(frame, text=label_text)
        label.grid(row=row, column=0, pady=5)

        entry_frame = tk.Frame(frame)
        entry_frame.grid(row=row, column=1, pady=5)

        entry = tk.Entry(entry_frame, width=10)
        entry.grid(row=0, column=0)

        placeholder_text = f"{min_val} - {max_val}"
        entry.insert(0, placeholder_text)
        entry.bind("<FocusIn>", lambda event, entry=entry: on_entry_click(event, entry, placeholder_text))
        entry.bind("<FocusOut>", lambda event, entry=entry: on_focus_out(event, entry, placeholder_text))

        checkbox_var = IntVar()
        checkbox = tk.Checkbutton(frame, text="Lock", variable=checkbox_var,
                                  command=lambda: set_custom_value(base, offsets, entry, checkbox_var, min_val,
                                                                   max_val, key))
        checkbox.grid(row=row, column=2, padx=5, pady=5)

        button = tk.Button(frame, text=f"Set {label_text}", width=10,
                           command=lambda: set_custom_value(base, offsets, entry, checkbox_var, min_val, max_val, key))
        button.grid(row=row, column=3, padx=5, pady=5)

    def on_entry_click(event, entry, placeholder_text):
        if entry.get() == placeholder_text:
            entry.delete(0, "end")
            entry.config(fg="black")

    def on_focus_out(event, entry, placeholder_text):
        if entry.get() == "":
            entry.insert(0, placeholder_text)
            entry.config(fg="grey")

    create_entry_with_lock(frame, 0, "Life:", BASE_ADDRESS_LIFE, OFFSETS_LIFE, 0, 2, 'life')
    create_entry_with_lock(frame, 1, "Armor:", BASE_ADDRESS_ARMOR, OFFSETS_ARMOR, 0, 4, 'armor')
    create_entry_with_lock(frame, 2, "Luke:", BASE_ADDRESS_LUKE, OFFSETS_LUKE, 0, 5, 'luke')
    create_entry_with_lock(frame, 3, "Laser:", BASE_ADDRESS_LASER, OFFSETS_LASER, 0, 3000, 'laser')
    create_entry_with_lock(frame, 4, "Aircraft:", BASE_ADDRESS_AIRCRAFT, OFFSETS_AIRCRAFT, 0, 3, 'aircraft')

    root.protocol("WM_DELETE_WINDOW", on_closing)  # Hook closing event

    # Bắt đầu kiểm tra quá trình game từ luồng chính của GUI
    start_checking(root)

    root.mainloop()


def on_closing():
    stop_threads()  # Dừng tất cả các luồng trước khi thoát chương trình
    sys.exit()


if __name__ == "__main__":
    create_gui()
