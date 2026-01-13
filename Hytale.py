import subprocess
import uuid
import sys
import os
import threading
import time
import base64
import json
import ctypes
import customtkinter as ctk
from http.server import BaseHTTPRequestHandler, HTTPServer
from tkinter import filedialog

# Global reference to app for logging and profile data
_app_instance = None

def is_admin():
    """Checks if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class HytaleApiHandler(BaseHTTPRequestHandler):
    """Handles requests redirected from Hytale's official servers."""
    def do_GET(self):
        if _app_instance:
            _app_instance.log_message(f"Intercepted GET: {self.headers.get('Host')}{self.path}", "emulator")

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        
        # Load active profile data
        profile = _app_instance.get_active_profile()
        
        if "user/profile" in self.path:
            user_data = {
                "username": profile.get("username", "ReiAyanami"),
                "uuid": profile.get("uuid", str(uuid.uuid4())),
                "identity_token": "emulated_jwt_token",
                "roles": ["player", "tester", "admin"],
                "avatar_data": profile.get("avatar_data", {}),
                "entitlements": ["hytale_base_game", "early_access_pack"]
            }
            self.wfile.write(json.dumps(user_data).encode())
        elif "friends" in self.path:
            self.wfile.write(json.dumps({"friends": [], "pending": []}).encode())
        elif "servers" in self.path:
            self.wfile.write(json.dumps({"servers": []}).encode())
        else:
            self.wfile.write(json.dumps({"status": "ok", "service": "HyLauncher-Emulator"}).encode())

    def do_POST(self):
        if _app_instance:
            _app_instance.log_message(f"Intercepted POST: {self.headers.get('Host')}{self.path}", "emulator")
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "success"}).encode())

    def log_message(self, format, *args):
        return

class HyLauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        global _app_instance
        _app_instance = self

        # Data initialization
        self.data = self.load_all_data()

        # Window Setup
        self.title("HyLauncher")
        self.geometry("1100x850")
        ctk.set_appearance_mode("dark")
        
        # Color Palette
        self.theme_teal = "#1abc9c"
        self.theme_dark = "#121212"
        self.theme_card = "#1e1e1e"
        self.theme_accent = "#3498db"

        # State Variables
        self.launch_mode = ctk.StringVar(value="simulated")
        self.emulator_port = 80 if is_admin() else 8080 

        # Start the Session Emulator
        self.start_emulator()

        # Layout Configuration
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 1. Sidebar (Left)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.theme_dark)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(8, weight=1)

        self.brand_label = ctk.CTkLabel(self.sidebar, text="HYLAUNCHER", font=ctk.CTkFont(size=28, weight="bold", family="Impact"))
        self.brand_label.grid(row=0, column=0, padx=20, pady=(40, 30))

        # Profile Quick-View
        self.profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.profile_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        active_p = self.get_active_profile()
        self.username_label = ctk.CTkLabel(self.profile_frame, text=active_p["username"], font=ctk.CTkFont(weight="bold"))
        self.username_label.pack(pady=5)

        # Nav
        self.nav_dash_btn = ctk.CTkButton(self.sidebar, text="  Dashboard", anchor="w", fg_color=self.theme_teal, command=lambda: self.switch_tab("dashboard"))
        self.nav_dash_btn.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.nav_acc_btn = ctk.CTkButton(self.sidebar, text="  Profiles & Accounts", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("account"))
        self.nav_acc_btn.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.nav_multi_btn = ctk.CTkButton(self.sidebar, text="  Multiplayer", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("multiplayer"))
        self.nav_multi_btn.grid(row=4, column=0, padx=20, pady=5, sticky="ew")

        self.nav_server_btn = ctk.CTkButton(self.sidebar, text="  Server Manager", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("server"))
        self.nav_server_btn.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.nav_settings_btn = ctk.CTkButton(self.sidebar, text="  Launcher Settings", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("settings"))
        self.nav_settings_btn.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        status_color = self.theme_teal if is_admin() else "#e67e22"
        status_text = f"● Mode: {'ADMIN' if is_admin() else 'USER'}"
        self.emu_status_label = ctk.CTkLabel(self.sidebar, text=status_text, text_color=status_color, font=ctk.CTkFont(size=10))
        self.emu_status_label.grid(row=8, column=0, pady=(0, 15))

        # 2. Main Container
        self.main_container = ctk.CTkFrame(self, fg_color="#151515", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # Tabs
        self.dashboard_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.account_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.multiplayer_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.server_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.settings_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")

        self.setup_ui_dashboard()
        self.setup_ui_account()
        self.setup_ui_multiplayer()
        self.setup_ui_server()
        self.setup_ui_settings()

        # Shared Console at the bottom
        self.grid_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.grid_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.grid_frame.grid_columnconfigure(0, weight=1)
        self.console = ctk.CTkTextbox(self.grid_frame, font=("Consolas", 11), fg_color=self.theme_card, height=180)
        self.console.pack(padx=10, pady=10, fill="both", expand=True)
        self.console.configure(state="disabled")

        self.log_message(f"System: HyLauncher initialized. Data stored in Documents.")
        self.check_files()
        self.switch_tab("dashboard")

    # --- DATA PERSISTENCE ---

    def load_all_data(self):
        path = os.path.join(self.setup_user_data(), "launcher_data.json")
        default_data = {
            "active_profile_id": "default",
            "game_root": r"E:\dl\install\release\package\game\latest",
            "profiles": {
                "default": {"name": "Default", "username": "ReiAyanami", "uuid": "13371337-1337-1337-1337-133713371337", "avatar_data": {}}
            },
            "servers": []
        }
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    # Ensure game_root is present even in older files
                    if "game_root" not in data:
                        data["game_root"] = default_data["game_root"]
                    return data
            except:
                return default_data
        return default_data

    def save_all_data(self):
        path = os.path.join(self.setup_user_data(), "launcher_data.json")
        with open(path, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_active_profile(self):
        pid = self.data.get("active_profile_id")
        if pid in self.data["profiles"]:
            return self.data["profiles"][pid]
        
        if self.data["profiles"]:
            first_id = list(self.data["profiles"].keys())[0]
            self.data["active_profile_id"] = first_id
            return self.data["profiles"][first_id]
            
        return {"name": "Recovery", "username": "Player", "uuid": str(uuid.uuid4()), "avatar_data": {}}

    # --- UI TABS ---

    def setup_ui_dashboard(self):
        self.dashboard_tab.grid_columnconfigure(0, weight=1)
        hero = ctk.CTkFrame(self.dashboard_tab, height=250, fg_color=self.theme_card, corner_radius=15)
        hero.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(hero, text="HYLAUNCHER", font=ctk.CTkFont(size=32, weight="bold")).place(relx=0.5, rely=0.3, anchor="center")
        
        self.play_btn = ctk.CTkButton(hero, text="PLAY HYTALE", width=300, height=60, font=ctk.CTkFont(size=20, weight="bold"), 
                                      fg_color=self.theme_teal, command=self.start_client_thread)
        self.play_btn.place(relx=0.5, rely=0.6, anchor="center")
        
        mode_frame = ctk.CTkFrame(hero, fg_color="transparent")
        mode_frame.place(relx=0.5, rely=0.85, anchor="center")
        ctk.CTkRadioButton(mode_frame, text="Unauthenticated (Simulated)", variable=self.launch_mode, value="simulated").pack(side="left", padx=10)
        ctk.CTkRadioButton(mode_frame, text="Pure Offline", variable=self.launch_mode, value="offline").pack(side="left", padx=10)

    def setup_ui_account(self):
        self.account_tab.grid_columnconfigure(0, weight=1)
        acc_frame = ctk.CTkScrollableFrame(self.account_tab, fg_color=self.theme_card, corner_radius=15)
        acc_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(acc_frame, text="PROFILE MANAGEMENT", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        # Profile Selector
        select_frame = ctk.CTkFrame(acc_frame, fg_color="transparent")
        select_frame.pack(fill="x", padx=20, pady=10)
        ctk.CTkLabel(select_frame, text="Select Profile:").pack(side="left", padx=10)
        
        self.profile_opt = ctk.CTkOptionMenu(select_frame, values=[p["name"] for p in self.data["profiles"].values()], command=self.change_profile_event)
        self.profile_opt.set(self.get_active_profile()["name"])
        self.profile_opt.pack(side="left", padx=10)
        
        ctk.CTkButton(select_frame, text="+ New", width=60, command=self.create_new_profile_event).pack(side="left", padx=5)
        ctk.CTkButton(select_frame, text="Delete", width=60, fg_color="maroon", command=self.delete_profile_event).pack(side="left", padx=5)

        ctk.CTkFrame(acc_frame, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=10)

        # Profile Details
        ctk.CTkLabel(acc_frame, text="Profile Display Name:").pack(padx=20, anchor="w")
        self.acc_prof_name = ctk.CTkEntry(acc_frame, width=400)
        self.acc_prof_name.pack(padx=20, pady=(0, 20), anchor="w")

        ctk.CTkLabel(acc_frame, text="In-Game Username:").pack(padx=20, anchor="w")
        self.acc_user_entry = ctk.CTkEntry(acc_frame, width=400)
        self.acc_user_entry.pack(padx=20, pady=(0, 20), anchor="w")
        
        ctk.CTkLabel(acc_frame, text="Persistent Player UUID:").pack(padx=20, anchor="w")
        self.acc_uuid_entry = ctk.CTkEntry(acc_frame, width=400)
        self.acc_uuid_entry.pack(padx=20, pady=(0, 10), anchor="w")
        ctk.CTkButton(acc_frame, text="Generate New UUID", width=150, command=self.regen_uuid, fg_color="gray30").pack(padx=20, pady=(0, 20), anchor="w")
        
        ctk.CTkLabel(acc_frame, text="Avatar Customization (JSON):").pack(padx=20, anchor="w")
        self.acc_avatar_text = ctk.CTkTextbox(acc_frame, height=150, width=600)
        self.acc_avatar_text.pack(padx=20, pady=(0, 20), anchor="w")
        
        ctk.CTkButton(acc_frame, text="APPLY CHANGES", width=200, height=40, fg_color=self.theme_teal, command=self.save_profile_event).pack(pady=20)

        self.refresh_account_ui()

    def setup_ui_multiplayer(self):
        self.multiplayer_tab.grid_columnconfigure(0, weight=1)
        self.multiplayer_tab.grid_rowconfigure(1, weight=1)

        hero = ctk.CTkFrame(self.multiplayer_tab, fg_color=self.theme_card, corner_radius=15)
        hero.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        ctk.CTkLabel(hero, text="NETWORK REDIRECTION (WORK IN PROGRESS)", font=ctk.CTkFont(size=20, weight="bold"), text_color="orange").pack(pady=10)
        
        self.redirect_btn = ctk.CTkButton(hero, text="AUTO-APPLY HOSTS REDIRECT (DISABLED)", fg_color="gray30", state="disabled")
        self.redirect_btn.pack(pady=10)

        browser_frame = ctk.CTkFrame(self.multiplayer_tab, fg_color=self.theme_card, corner_radius=15)
        browser_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        ctk.CTkLabel(browser_frame, text="SAVED SERVERS", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=10)

        add_frame = ctk.CTkFrame(browser_frame, fg_color="transparent")
        add_frame.pack(fill="x", padx=20, pady=5)
        self.srv_name_entry = ctk.CTkEntry(add_frame, placeholder_text="Server Name", width=150)
        self.srv_name_entry.pack(side="left", padx=5)
        self.srv_addr_entry = ctk.CTkEntry(add_frame, placeholder_text="IP:Port", width=200)
        self.srv_addr_entry.pack(side="left", padx=5)
        ctk.CTkButton(add_frame, text="Add Server", width=80, command=self.add_server_event).pack(side="left", padx=5)

        self.server_list_scroll = ctk.CTkScrollableFrame(browser_frame, fg_color="transparent")
        self.server_list_scroll.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_server_list()

    def setup_ui_server(self):
        self.server_tab.grid_columnconfigure(0, weight=1)
        hero = ctk.CTkFrame(self.server_tab, height=200, fg_color=self.theme_card, corner_radius=15)
        hero.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(hero, text="DEDICATED SERVER MANAGER", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        ctk.CTkButton(hero, text="START LOCAL SERVER", width=200, height=45, command=self.start_server_thread, fg_color=self.theme_accent).pack(pady=10)

    def setup_ui_settings(self):
        self.settings_tab.grid_columnconfigure(0, weight=1)
        container = ctk.CTkFrame(self.settings_tab, fg_color=self.theme_card, corner_radius=15)
        container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(container, text="LAUNCHER SETTINGS", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        ctk.CTkLabel(container, text="Hytale Game Directory (Root):").pack(padx=20, anchor="w")
        
        path_frame = ctk.CTkFrame(container, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.settings_path_entry = ctk.CTkEntry(path_frame, width=450)
        self.settings_path_entry.insert(0, self.data.get("game_root", ""))
        self.settings_path_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(path_frame, text="Browse", width=80, command=self.browse_game_path).pack(side="left", padx=5)
        ctk.CTkButton(path_frame, text="Auto Detect", width=100, fg_color=self.theme_teal, command=self.auto_detect_game).pack(side="left", padx=5)

        ctk.CTkLabel(container, text="Note: The root directory should contain the 'Client' and 'Server' folders.", text_color="gray", font=ctk.CTkFont(size=11)).pack(padx=20, anchor="w", pady=(0, 20))
        
        ctk.CTkButton(container, text="SAVE SETTINGS", width=200, height=40, fg_color=self.theme_accent, command=self.save_settings_event).pack(pady=10)

    # --- EVENTS & LOGIC ---

    def browse_game_path(self):
        folder = filedialog.askdirectory()
        if folder:
            self.settings_path_entry.delete(0, "end")
            self.settings_path_entry.insert(0, folder)

    def auto_detect_game(self):
        self.log_message("Scanning drives for Hytale installation...", "sys")
        found_path = None
        # Common search patterns
        drives = ['C', 'D', 'E', 'F', 'G']
        sub_paths = [
            r"Hytale\game\latest",
            r"Games\Hytale\game\latest",
            r"dl\install\release\package\game\latest"
        ]
        
        for drive in drives:
            for sub in sub_paths:
                test_path = f"{drive}:\\{sub}"
                if os.path.exists(os.path.join(test_path, "Client", "HytaleClient.exe")):
                    found_path = test_path
                    break
            if found_path: break
            
        if found_path:
            self.settings_path_entry.delete(0, "end")
            self.settings_path_entry.insert(0, found_path)
            self.log_message(f"Auto-detected Hytale at: {found_path}", "sys")
        else:
            self.log_message("Could not auto-detect Hytale. Please browse manually.", "warn")

    def save_settings_event(self):
        new_path = self.settings_path_entry.get().strip()
        if os.path.exists(os.path.join(new_path, "Client", "HytaleClient.exe")):
            self.data["game_root"] = new_path
            self.save_all_data()
            self.log_message("Settings saved. Game path updated.", "sys")
        else:
            self.log_message("Error: Invalid game directory. HytaleClient.exe not found in 'Client' subfolder.", "error")

    def switch_tab(self, tab_name):
        for tab in [self.dashboard_tab, self.account_tab, self.multiplayer_tab, self.server_tab, self.settings_tab]: tab.grid_forget()
        for btn in [self.nav_dash_btn, self.nav_acc_btn, self.nav_multi_btn, self.nav_server_btn, self.nav_settings_btn]: btn.configure(fg_color="transparent")
        
        if tab_name == "dashboard":
            self.dashboard_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_dash_btn.configure(fg_color=self.theme_teal)
        elif tab_name == "account":
            self.account_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_acc_btn.configure(fg_color=self.theme_accent)
        elif tab_name == "multiplayer":
            self.multiplayer_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_multi_btn.configure(fg_color=self.theme_accent)
        elif tab_name == "server":
            self.server_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_server_btn.configure(fg_color=self.theme_accent)
        elif tab_name == "settings":
            self.settings_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_settings_btn.configure(fg_color=self.theme_accent)

    def refresh_account_ui(self):
        p = self.get_active_profile()
        self.acc_prof_name.delete(0, "end")
        self.acc_prof_name.insert(0, p["name"])
        self.acc_user_entry.delete(0, "end")
        self.acc_user_entry.insert(0, p["username"])
        self.acc_uuid_entry.delete(0, "end")
        self.acc_uuid_entry.insert(0, p["uuid"])
        self.acc_avatar_text.delete("1.0", "end")
        self.acc_avatar_text.insert("1.0", json.dumps(p.get("avatar_data", {}), indent=2))
        self.username_label.configure(text=p["username"])

    def change_profile_event(self, name):
        target_pid = None
        for pid, p in self.data["profiles"].items():
            if p["name"] == name:
                target_pid = pid
                break
        
        if target_pid:
            self.data["active_profile_id"] = target_pid
            self.save_all_data()
            self.refresh_account_ui()

    def create_new_profile_event(self):
        new_id = str(uuid.uuid4())
        self.data["profiles"][new_id] = {
            "name": f"New Profile {len(self.data['profiles'])}",
            "username": "NewPlayer",
            "uuid": str(uuid.uuid4()),
            "avatar_data": {}
        }
        self.data["active_profile_id"] = new_id
        self.profile_opt.configure(values=[p["name"] for p in self.data["profiles"].values()])
        self.profile_opt.set(self.data["profiles"][new_id]["name"])
        self.save_all_data()
        self.refresh_account_ui()

    def delete_profile_event(self):
        if len(self.data["profiles"]) <= 1: return
        pid = self.data["active_profile_id"]
        del self.data["profiles"][pid]
        
        new_pid = list(self.data["profiles"].keys())[0]
        self.data["active_profile_id"] = new_pid
        
        self.profile_opt.configure(values=[p["name"] for p in self.data["profiles"].values()])
        self.profile_opt.set(self.data["profiles"][new_pid]["name"])
        self.save_all_data()
        self.refresh_account_ui()

    def save_profile_event(self):
        pid = self.data["active_profile_id"]
        try:
            avatar_json = self.acc_avatar_text.get("1.0", "end-1c")
            updated_name = self.acc_prof_name.get()
            self.data["profiles"][pid].update({
                "name": updated_name,
                "username": self.acc_user_entry.get(),
                "uuid": self.acc_uuid_entry.get(),
                "avatar_data": json.loads(avatar_json) if avatar_json.strip() else {}
            })
            self.save_all_data()
            
            self.profile_opt.configure(values=[p["name"] for p in self.data["profiles"].values()])
            self.profile_opt.set(updated_name)
            
            self.username_label.configure(text=self.data["profiles"][pid]["username"])
            self.log_message("Changes applied and profile updated.", "sys")
        except Exception as e:
            self.log_message(f"Save error: {e}", "error")

    def refresh_server_list(self):
        for widget in self.server_list_scroll.winfo_children(): widget.destroy()
        for idx, srv in enumerate(self.data["servers"]):
            frame = ctk.CTkFrame(self.server_list_scroll, fg_color="gray20")
            frame.pack(fill="x", padx=5, pady=2)
            ctk.CTkLabel(frame, text=srv["name"], width=150, anchor="w", font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
            ctk.CTkLabel(frame, text=srv["address"], width=200, anchor="w", text_color="gray").pack(side="left", padx=10)
            ctk.CTkButton(frame, text="JOIN", width=60, fg_color=self.theme_teal, command=lambda a=srv["address"]: self.join_server_direct(a)).pack(side="right", padx=5)
            ctk.CTkButton(frame, text="X", width=30, fg_color="maroon", command=lambda i=idx: self.delete_server_event(i)).pack(side="right", padx=5)

    def add_server_event(self):
        name = self.srv_name_entry.get()
        addr = self.srv_addr_entry.get()
        if name and addr:
            self.data["servers"].append({"name": name, "address": addr})
            self.save_all_data()
            self.refresh_server_list()
            self.srv_name_entry.delete(0, "end")
            self.srv_addr_entry.delete(0, "end")

    def delete_server_event(self, idx):
        self.data["servers"].pop(idx)
        self.save_all_data()
        self.refresh_server_list()

    def join_server_direct(self, address):
        threading.Thread(target=lambda: self.launch_client(server_address=address), daemon=True).start()

    def regen_uuid(self):
        self.acc_uuid_entry.delete(0, "end")
        self.acc_uuid_entry.insert(0, str(uuid.uuid4()))

    def start_emulator(self):
        def run():
            try:
                HTTPServer(('', self.emulator_port), HytaleApiHandler).serve_forever()
            except: pass
        threading.Thread(target=run, daemon=True).start()

    def log_message(self, message, type="info"):
        if any(f in message for f in ["Telemetry request failed", "at HytaleClient!", "System.Net.Http"]): return
        self.console.configure(state="normal")
        self.console.insert("end", f"[{type.upper()}] {message}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def launch_client(self, server_address=None):
        p = self.get_active_profile()
        game_root = self.data.get("game_root", "")
        client_exe = os.path.join(game_root, "Client", "HytaleClient.exe")
        
        if not os.path.exists(client_exe):
            self.log_message(f"Error: HytaleClient.exe not found at {client_exe}. Check Settings.", "error")
            return

        args = [client_exe, "--user-dir", self.setup_user_data(), "--name", p["username"], "--uuid", p["uuid"]]
        
        if self.launch_mode.get() == "simulated":
            token = base64.urlsafe_b64encode(json.dumps({"sub": p["uuid"], "name": p["username"], "scope": "hytale:client"}).encode()).decode().rstrip('=')
            args.extend(["--identity-token", f"hdr.{token}.sig", "--session-token", f"hdr.{token}.sig"])
        else:
            args.append("--auth-mode=offline")
        
        if server_address:
            args.extend(["--connect", server_address])
            self.log_message(f"Connecting to {server_address}...", "client")

        j = self.get_java_path()
        if j: args.extend(["--java-exec", j])
        self.run_process(args, os.path.dirname(client_exe), "CLIENT")

    def start_client_thread(self): threading.Thread(target=self.launch_client, daemon=True).start()
    def start_server_thread(self): threading.Thread(target=self.launch_server, daemon=True).start()
    
    def launch_server(self):
        game_root = self.data.get("game_root", "")
        server_jar = os.path.join(game_root, "Server", "HytaleServer.jar")
        
        if not os.path.exists(server_jar):
            self.log_message(f"Error: HytaleServer.jar not found at {server_jar}. Check Settings.", "error")
            return

        j = self.get_java_path() or "java"
        self.run_process([j, "-jar", server_jar, "--auth-mode", "unauthenticated", "--port", "25565"], os.path.dirname(server_jar), "SERVER")

    def run_process(self, args, cwd, prefix):
        try:
            p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            while True:
                line = p.stdout.readline()
                if not line and p.poll() is not None: break
                if line: self.log_message(line.strip(), prefix.lower())
        except Exception as e: self.log_message(f"Error: {str(e)}", "error")

    def check_files(self):
        game_root = self.data.get("game_root", "")
        client_exe = os.path.join(game_root, "Client", "HytaleClient.exe")
        if not os.path.exists(client_exe): 
            self.log_message("Warning: HytaleClient.exe not found at current path. Update in Settings.", "warn")
            
    def get_java_path(self):
        game_root = self.data.get("game_root", "")
        # Assuming standard structure: .../package/game/latest/
        # Check if we are inside a 'game/latest' folder
        p = os.path.dirname(os.path.dirname(os.path.dirname(game_root)))
        j = os.path.join(p, "jre", "latest", "bin", "java.exe")
        return j if os.path.exists(j) else None
    
    def setup_user_data(self):
        """Modified to store data in the user's Documents folder."""
        docs_path = os.path.join(os.path.expanduser("~"), "Documents", "HyLauncher")
        path = os.path.join(docs_path, "UserData")
        if not os.path.exists(path):
            os.makedirs(path)
        return path

if __name__ == "__main__":
    app = HyLauncherApp()
    app.mainloop()