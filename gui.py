import tkinter as tk
from tkinter import filedialog, messagebox
from functions import load_config, save_config, program_device, disconnect_device, read_serial_port, parse_serial_messages, calculate_battery_voltage
import serial
import time

class STM32ProgrammerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("STM32 Programmer")

        self.config = load_config()

        self.stm32_dir = self.config.get("Settings", "STM32_DIR", fallback="")
        self.elf_file = self.config.get("Settings", "ELF_FILE", fallback="")
        self.serial_port = self.config.get("Settings", "SERIAL_PORT", fallback="")

        # STM32 Directory Input
        self.stm32_dir_label = tk.Label(root, text="STM32_CLI Directory:")
        self.stm32_dir_label.grid(row=0, column=0, padx=10, pady=5)
        self.stm32_dir_entry = tk.Entry(root, width=80)
        self.stm32_dir_entry.grid(row=0, column=1, padx=10, pady=5)
        self.stm32_dir_entry.insert(0, self.stm32_dir)
        self.stm32_dir_button = tk.Button(root, text="Browse", command=self.browse_stm32_dir)
        self.stm32_dir_button.grid(row=0, column=2, padx=10, pady=5)

        # ELF File Input
        self.elf_file_label = tk.Label(root, text="ELF File:")
        self.elf_file_label.grid(row=1, column=0, padx=10, pady=5)
        self.elf_file_entry = tk.Entry(root, width=80)
        self.elf_file_entry.grid(row=1, column=1, padx=10, pady=5)
        self.elf_file_entry.insert(0, self.elf_file)
        self.elf_file_button = tk.Button(root, text="Browse", command=self.browse_elf_file)
        self.elf_file_button.grid(row=1, column=2, padx=10, pady=5)

        # Serial Port Input
        self.serial_port_label = tk.Label(root, text="Serial Port:")
        self.serial_port_label.grid(row=2, column=0, padx=10, pady=5)
        self.serial_port_entry = tk.Entry(root, width=80)
        self.serial_port_entry.grid(row=2, column=1, padx=10, pady=5)
        self.serial_port_entry.insert(0, self.serial_port)

        # Run Button
        self.run_button = tk.Button(root, text="Run", command=self.run)
        self.run_button.grid(row=3, column=1, padx=10, pady=10)

    def browse_stm32_dir(self):
        self.stm32_dir = filedialog.askopenfilename(title="Select STM32_CLI Executable")
        self.stm32_dir_entry.delete(0, tk.END)
        self.stm32_dir_entry.insert(0, self.stm32_dir)
        save_config(self.stm32_dir, self.elf_file, self.serial_port)
        print(f"STM32_CLI Directory selected: {self.stm32_dir}")

    def browse_elf_file(self):
        self.elf_file = filedialog.askopenfilename(title="Select ELF File")
        self.elf_file_entry.delete(0, tk.END)
        self.elf_file_entry.insert(0, self.elf_file)
        save_config(self.stm32_dir, self.elf_file, self.serial_port)
        print(f"ELF File selected: {self.elf_file}")

    def run(self):
        # Retrieve current values from the GUI
        self.stm32_dir = self.stm32_dir_entry.get()
        self.elf_file = self.elf_file_entry.get()
        self.serial_port = self.serial_port_entry.get()

        print(f"Running with STM32_DIR: {self.stm32_dir}, ELF_FILE: {self.elf_file}, SERIAL_PORT: {self.serial_port}")

        if not self.stm32_dir or not self.elf_file or not self.serial_port:
            messagebox.showerror("Error", "Please provide STM32_CLI Directory, ELF File, and Serial Port.")
            return

        try:
            ser = serial.Serial(self.serial_port, 115200, timeout=5)  # Set baud rate to 115200
            time.sleep(2)  # wait for the serial connection to initialize
            print(f"Serial port {self.serial_port} opened successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open serial port: {str(e)}")
            return

        if program_device(self.stm32_dir, self.elf_file):
            # Add a delay before reading from the serial port
            time.sleep(5)
            disconnect_device(self.stm32_dir)
            messages = read_serial_port(ser)
            if messages:
                version, raw_voltage = parse_serial_messages(messages)
                battery_voltage = calculate_battery_voltage(raw_voltage)

                print(f"Version: {version}, Raw Voltage: {raw_voltage}, Battery Voltage: {battery_voltage}")

                if battery_voltage < 1.0:
                    messagebox.showinfo("Result", "Fail: No Battery Connected")
                else:
                    messagebox.showinfo("Result", f"Pass: Firmware Version {version}, Battery Voltage {battery_voltage:.2f}V")
            else:
                messagebox.showerror("Error", "Failed to read from the serial port.")
        
        # Close the serial port
        ser.close()
        print(f"Serial port {self.serial_port} closed.")
        
        # Disconnect the device after reading the serial messages
        
