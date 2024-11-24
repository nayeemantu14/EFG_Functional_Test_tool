import subprocess
import configparser
import os
import serial
import time
from tkinter import messagebox

config_file = "config.ini"

def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
    return config

def save_config(stm32_dir, elf_file, serial_port):
    config = configparser.ConfigParser()
    config['Settings'] = {
        'STM32_DIR': stm32_dir,
        'ELF_FILE': elf_file,
        'SERIAL_PORT': serial_port
    }
    with open(config_file, 'w') as configfile:
        config.write(configfile)

def program_device(stm32_dir, elf_file):
    try:
        command = [
            stm32_dir,
            "-c", "port=SWD", "freq=8000", "mode=NORMAL", "speed=Reliable",
            "-d", elf_file
        ]

        result = subprocess.run(command, text=True, capture_output=True)
        print(f"Program Device Command: {' '.join(command)}")
        print(f"Program Device Result: {result.stdout}")

        if result.returncode == 0:
            return True
        else:
            messagebox.showerror("Error", f"Programming failed: {result.stderr}")
            return False

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")
        return False

def disconnect_device(stm32_dir):
    try:
        command = [
            stm32_dir,
            "-c", "port=SWD", "dis"
        ]

        result = subprocess.run(command, text=True, capture_output=True)
        print(f"Disconnect Device Command: {' '.join(command)}")
        print(f"Disconnect Device Result: {result.stdout}")

        if result.returncode == 0:
            messagebox.showinfo("Success", "Disconnection successful.")
        else:
            messagebox.showerror("Error", f"Disconnection failed: {result.stderr}")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def read_serial_port(ser):
    try:
        print(f"Reading from serial port: {ser.port}")
        lines = []
        end_marker = "Entering Sleep."  # Define the end marker to stop reading
        start_time = time.time()
        timeout = 30  # Set a timeout for reading the serial port

        while True:
            line = ser.readline().decode('utf-8').strip()
            if line:
                print(f"Serial port message: {line}")
                lines.append(line)
                if end_marker in line:
                    break
            if time.time() - start_time > timeout:
                print("Serial read timed out.")
                break

        if not lines:
            print("No data received from the serial port.")
        return lines

    except Exception as e:
        print(f"Exception while reading from serial port: {str(e)}")
        messagebox.showerror("Error", f"An error occurred while reading the serial port: {str(e)}")
        return None

def parse_serial_messages(messages):
    version = ""
    battery_voltage = 0

    for message in messages:
        if "EFloodGuardLP" in message:
            version = message.split('(')[1].strip(')')
        if "Battery Voltage" in message:
            battery_voltage = int(message.split(':')[1].strip())

    return version, battery_voltage

def calculate_battery_voltage(raw_voltage):
    return (raw_voltage / 4095) * 3.3 * 2
