import threading
import time
import tkinter as tk
from tkinter import messagebox

from pymem import *
from pymem.exception import ProcessNotFound, MemoryReadError, MemoryWriteError
from pymem.process import *

AC_CLIENT_PROCESS = "HeavyWeapon.exe"

mem = None
module = None
game_found = False
running_states = {}
threads = {}


def initialize_pymem():
    global mem, module, game_found
    try:
        mem = Pymem(AC_CLIENT_PROCESS)
        module = module_from_name(mem.process_handle, AC_CLIENT_PROCESS).lpBaseOfDll
        game_found = True
    except (ProcessNotFound, pymem.exception.ProcessError):
        game_found = False


def check_game_process(root):
    global game_found
    initialize_pymem()
    if not game_found:
        root.after(0, lambda: messagebox.showerror("Error", "Cannot find game process. Please start the game."))
        stop_threads()  # Dừng tất cả các luồng khi không tìm thấy game
        time.sleep(2)  # Chờ 5 giây trước khi tiếp tục kiểm tra lại
    else:
        root.after(1000, lambda: check_game_process(root))  # Kiểm tra lại sau mỗi giây


def get_pointer_address(base, offsets):
    addr = mem.read_int(base)
    for offset in offsets[:-1]:
        addr = mem.read_int(addr + offset)
    addr += offsets[-1]
    return addr


def set_value(base, offsets, value):
    try:
        target_address = get_pointer_address(module + base, offsets)
        mem.write_int(target_address, value)
        print(f"Value set to {value} at {target_address}")
    except (MemoryReadError, MemoryWriteError) as e:
        messagebox.showerror("Error", f"Error accessing memory: {e}")


def stop_threads():
    global running_states, threads
    for key in running_states:
        running_states[key] = False
    for key in threads:
        threads[key].join()


# Khởi chạy luồng kiểm tra game
def start_checking(root):
    check_game_thread = threading.Thread(target=lambda: check_game_process(root))
    check_game_thread.start()
