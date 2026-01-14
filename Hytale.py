import subprocess
import uuid
import sys
import os
import threading
import time
import base64
import json
import ctypes
import urllib.request
import re
import webbrowser
import socket
import ssl
import customtkinter as ctk
from tkinter import filedialog, messagebox



# Global reference to app for logging and profile data
_app_instance = None

def is_admin():
    """Checks if the script is running with administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False



class HyLauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        global _app_instance
        _app_instance = self

        # Data initialization
        self.data = self.load_all_data()

        # Window Setup
        self.title("HyLauncher")
        self.geometry("1100x900")
        ctk.set_appearance_mode("dark")
        
        # Color Palette
        self.theme_teal = "#1abc9c"
        self.theme_dark = "#121212"
        self.theme_card = "#1e1e1e"
        self.theme_accent = "#3498db"
        self.theme_danger = "#e74c3c"
        self.theme_success = "#2ecc71"

        # State Variables
        self.launch_mode = ctk.StringVar(value="simulated")
        self._is_shutting_down = False

        # 1. Initialize Essential Layout & Console First
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # 2. Main Container Setup
        self.main_container = ctk.CTkFrame(self, fg_color="#151515", corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        # 3. Create Shared Console at the bottom
        self.console_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.console_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        self.console_frame.grid_columnconfigure(0, weight=1)
        self.console = ctk.CTkTextbox(self.console_frame, font=("Consolas", 11), fg_color=self.theme_card, height=180)
        self.console.pack(padx=10, pady=10, fill="both", expand=True)
        self.console.configure(state="disabled")


        # 4. Sidebar (Left)
        self.sidebar = ctk.CTkFrame(self, width=220, corner_radius=0, fg_color=self.theme_dark)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(10, weight=1) # Adjusted for new button

        self.brand_label = ctk.CTkLabel(self.sidebar, text="HYLAUNCHER", font=ctk.CTkFont(size=28, weight="bold", family="Impact"))
        self.brand_label.grid(row=0, column=0, padx=20, pady=(40, 30))

        # Profile Quick-View
        self.profile_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.profile_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        
        active_p = self.get_active_profile()
        self.username_label = ctk.CTkLabel(self.profile_frame, text=active_p["username"], font=ctk.CTkFont(weight="bold"))
        self.username_label.pack(pady=5)

        # Navigation Buttons
        self.nav_dash_btn = ctk.CTkButton(self.sidebar, text="  Dashboard", anchor="w", fg_color=self.theme_teal, command=lambda: self.switch_tab("dashboard"))
        self.nav_dash_btn.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        self.nav_acc_btn = ctk.CTkButton(self.sidebar, text="  Account & Profile", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("account"))
        self.nav_acc_btn.grid(row=3, column=0, padx=20, pady=5, sticky="ew")

        self.nav_mods_btn = ctk.CTkButton(self.sidebar, text="  Mods", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("mods"))
        self.nav_mods_btn.grid(row=4, column=0, padx=20, pady=5, sticky="ew")
        
        # New Friends P2P Button
        self.nav_friends_btn = ctk.CTkButton(self.sidebar, text="  Friends (P2P)", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("friends"))
        self.nav_friends_btn.grid(row=5, column=0, padx=20, pady=5, sticky="ew")

        self.nav_multi_btn = ctk.CTkButton(self.sidebar, text="  Multiplayer", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("multiplayer"))
        self.nav_multi_btn.grid(row=6, column=0, padx=20, pady=5, sticky="ew")

        self.nav_server_btn = ctk.CTkButton(self.sidebar, text="  Server Manager", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("server"))
        self.nav_server_btn.grid(row=7, column=0, padx=20, pady=5, sticky="ew")

        self.nav_settings_btn = ctk.CTkButton(self.sidebar, text="  Launcher Settings", anchor="w", fg_color="transparent", border_width=1, command=lambda: self.switch_tab("settings"))
        self.nav_settings_btn.grid(row=8, column=0, padx=20, pady=5, sticky="ew")

        status_color = self.theme_teal if is_admin() else "#e67e22"
        status_text = f"● Mode: {'ADMIN' if is_admin() else 'USER'}"
        self.emu_status_label = ctk.CTkLabel(self.sidebar, text=status_text, text_color=status_color, font=ctk.CTkFont(size=10))
        self.emu_status_label.grid(row=10, column=0, pady=(0, 15))

        # 5. UI Tab Frames
        self.dashboard_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.account_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.mods_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.friends_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.multiplayer_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.server_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.settings_tab = ctk.CTkFrame(self.main_container, fg_color="transparent")

        self.setup_ui_dashboard()
        self.setup_ui_account()
        self.setup_ui_mods()
        self.setup_ui_friends()
        self.setup_ui_multiplayer()
        self.setup_ui_server()
        self.setup_ui_settings()

        

        self.log_message(f"System: HyLauncher initialized. Mod path: {self.get_hytale_mods_dir()}")
        
        self.check_files()
        self.switch_tab("dashboard")
        
        # Protocol for clean shutdown
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def log_message(self, message, type="info"):
        """Logs a message to the internal console."""
        if any(f in message for f in ["Telemetry", "at HytaleClient!", "System.Net.Http"]): return
        try:
            self.console.configure(state="normal")
            self.console.insert("end", f"[{type.upper()}] {message}\n")
            self.console.see("end")
            self.console.configure(state="disabled")
        except:
            pass

    # --- DISCORD RPC (removed) ---
    def update_rpc(self, state, details=None):
        # Discord RPC removed — kept as a no-op for compatibility with existing calls
        return

    # --- MOD MANAGEMENT ---

    def get_hytale_mods_dir(self):
        path = os.path.join(os.environ['APPDATA'], "Hytale", "UserData", "Mods")
        if not os.path.exists(path):
            try: os.makedirs(path)
            except: pass
        return path

    def open_mods_folder(self):
        path = self.get_hytale_mods_dir()
        if os.path.exists(path): os.startfile(path)

    # --- DATA PERSISTENCE ---

    def load_all_data(self):
        root_data = os.path.join(os.path.expanduser("~"), "Documents", "HyLauncher")
        if not os.path.exists(root_data): os.makedirs(root_data)
        
        path = os.path.join(root_data, "launcher_config.json")
        default_data = {
            "game_root": r"E:\dl\install\release\package\game\latest",
            "profile": {"username": "ReiAyanami", "uuid": str(uuid.uuid4()), "avatar_data": {}},
            "servers": [],
            "friends": [] # Added friends list
        }
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    if "friends" not in data: data["friends"] = [] # Migration
                    return data
            except: return default_data
        return default_data

    def save_all_data(self):
        path = os.path.join(os.path.expanduser("~"), "Documents", "HyLauncher", "launcher_config.json")
        with open(path, "w") as f: json.dump(self.data, f, indent=4)

    def get_active_profile(self):
        return self.data.get("profile", {"username": "ReiAyanami", "uuid": str(uuid.uuid4()), "avatar_data": {}})

    # --- UI TABS ---

    def setup_ui_dashboard(self):
        self.dashboard_tab.grid_columnconfigure(0, weight=1)
        hero = ctk.CTkFrame(self.dashboard_tab, height=250, fg_color=self.theme_card, corner_radius=15)
        hero.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(hero, text="HYLAUNCHER", font=ctk.CTkFont(size=32, weight="bold")).place(relx=0.5, rely=0.3, anchor="center")
        
        self.play_btn = ctk.CTkButton(hero, text="PLAY HYTALE", width=300, height=60, font=ctk.CTkFont(size=20, weight="bold"), 
                                      fg_color=self.theme_teal, command=self.start_client_thread)
        self.play_btn.place(relx=0.5, rely=0.5, anchor="center")
        
        mode_frame = ctk.CTkFrame(hero, fg_color="transparent")
        mode_frame.place(relx=0.5, rely=0.8, anchor="center")
        ctk.CTkRadioButton(mode_frame, text="Simulated Auth", variable=self.launch_mode, value="simulated").pack(side="left", padx=10)
        ctk.CTkRadioButton(mode_frame, text="Pure Offline", variable=self.launch_mode, value="offline").pack(side="left", padx=10)

    def setup_ui_account(self):
        self.account_tab.grid_columnconfigure(0, weight=1)
        acc_frame = ctk.CTkScrollableFrame(self.account_tab, fg_color=self.theme_card, corner_radius=15)
        acc_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(acc_frame, text="USER PROFILE MANAGEMENT", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=10)

        ctk.CTkFrame(acc_frame, height=2, fg_color="gray30").pack(fill="x", padx=20, pady=10)

        # Profile Details
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
        
        ctk.CTkButton(acc_frame, text="SAVE PROFILE CHANGES", width=250, height=40, fg_color=self.theme_teal, command=self.save_profile_event).pack(pady=20)

        self.refresh_account_ui()

    def setup_ui_mods(self):
        self.mods_tab.grid_columnconfigure(0, weight=1)
        self.mods_tab.grid_rowconfigure(0, weight=1)
        
        nav_frame = ctk.CTkFrame(self.mods_tab, fg_color="transparent")
        nav_frame.grid(row=0, column=0, padx=20, pady=10, sticky="ew")
        
        ctk.CTkButton(nav_frame, text="Open Mods Folder", width=140, fg_color="gray30", command=self.open_mods_folder).pack(side="left", padx=5)

        self.mods_content_container = ctk.CTkFrame(self.mods_tab, fg_color=self.theme_card, corner_radius=15)
        self.mods_content_container.grid(row=0, column=0, padx=20, pady=10, sticky="nsew")
        self.mods_content_container.grid_columnconfigure(0, weight=1)
        self.mods_content_container.grid_rowconfigure(0, weight=1)

        self.mods_view_mode = ctk.StringVar(value="installed")
        self.refresh_mods_ui()


    def search_mods_event(self):
        pass

    def show_mods_status(self, text):
        for widget in self.mods_content_container.winfo_children(): widget.destroy()
        ctk.CTkLabel(self.mods_content_container, text=text, text_color="gray").pack(pady=40)

    def refresh_mods_ui(self):
        for widget in self.mods_content_container.winfo_children(): widget.destroy()
        
        scroll_frame = ctk.CTkScrollableFrame(self.mods_content_container, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)
        mods_dir = self.get_hytale_mods_dir()
        try:
            files = [f for f in os.listdir(mods_dir) if f.endswith(".zip") or f.endswith(".jar")]
        except: files = []
        
        if not files:
            ctk.CTkLabel(scroll_frame, text="No mods installed\n\nDownload .zip or .jar files to:\n" + mods_dir, text_color="gray", justify="center").pack(pady=40)
            return
        
        for filename in files:
            mod_info = {"name": filename, "author": "Local File", "desc": f"Location: {mods_dir}", "filename": filename}
            self.create_mod_card(scroll_frame, mod_info, is_installed=True)

    def create_mod_card(self, master, mod, is_installed):
        card = ctk.CTkFrame(master, fg_color="gray20", corner_radius=10)
        card.pack(fill="x", padx=10, pady=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=15, pady=10)
        
        ctk.CTkLabel(info_frame, text=mod["name"], font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=f"By {mod.get('author', 'Unknown')}", font=ctk.CTkFont(size=11), text_color=self.theme_teal).pack(anchor="w")
        ctk.CTkLabel(info_frame, text=mod.get("desc", ""), font=ctk.CTkFont(size=12), text_color="gray", wraplength=500).pack(anchor="w", pady=(5, 0))
        
        if is_installed:
            ctk.CTkButton(card, text="REMOVE", width=100, fg_color="#c0392b", command=lambda f=mod['filename']: self.remove_mod_event(f)).pack(side="right", padx=15)

    def remove_mod_event(self, filename):
        path = os.path.join(self.get_hytale_mods_dir(), filename)
        try:
            if os.path.exists(path):
                os.remove(path)
                self.log_message(f"Cleaned up mod file: {filename}", "sys")
                self.refresh_mods_ui()
        except Exception as e:
            self.log_message(f"Error removing file: {e}", "error")
            
    # --- FRIENDS P2P SYSTEM ---

    def setup_ui_friends(self):
        self.friends_tab.grid_columnconfigure(0, weight=1)
        self.friends_tab.grid_rowconfigure(0, weight=1)

        ctk.CTkLabel(self.friends_tab, text="COMING SOON", font=ctk.CTkFont(size=48, weight="bold"), text_color="gray50").grid(row=0, column=0)

    # --- MULTIPLAYER & SERVER ---

    def setup_ui_multiplayer(self):
        self.multiplayer_tab.grid_columnconfigure(0, weight=1)
        self.multiplayer_tab.grid_rowconfigure(1, weight=1)

        hero = ctk.CTkFrame(self.multiplayer_tab, fg_color=self.theme_card, corner_radius=15)
        hero.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        ctk.CTkLabel(hero, text="MULTI-SERVER MANAGER", font=ctk.CTkFont(size=20, weight="bold"), text_color="orange").pack(pady=10)
        
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
        ctk.CTkButton(hero, text="START DEDICATED SERVER", width=250, height=45, command=self.start_server_thread, fg_color=self.theme_accent).pack(pady=10)
        ctk.CTkLabel(hero, text="Launches in Offline mode with 15m Backups.", text_color="gray", font=ctk.CTkFont(size=11)).pack()

    def setup_ui_settings(self):
        self.settings_tab.grid_columnconfigure(0, weight=1)
        container = ctk.CTkFrame(self.settings_tab, fg_color=self.theme_card, corner_radius=15)
        container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        ctk.CTkLabel(container, text="GLOBAL LAUNCHER SETTINGS", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=20)
        
        ctk.CTkLabel(container, text="Hytale Game Binaries Root:").pack(padx=20, anchor="w")
        path_frame = ctk.CTkFrame(container, fg_color="transparent")
        path_frame.pack(fill="x", padx=20, pady=(0, 10))
        
        self.settings_path_entry = ctk.CTkEntry(path_frame, width=450)
        self.settings_path_entry.insert(0, self.data.get("game_root", ""))
        self.settings_path_entry.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(path_frame, text="Browse", width=80, command=self.browse_game_path).pack(side="left", padx=5)
        ctk.CTkButton(path_frame, text="Auto Detect", width=100, fg_color=self.theme_teal, command=self.auto_detect_game).pack(side="left", padx=5)
        
        ctk.CTkButton(container, text="SAVE GLOBAL SETTINGS", width=250, height=40, fg_color=self.theme_accent, command=self.save_settings_event).pack(pady=10)

    # --- SHARED UTILS ---

    def switch_tab(self, tab_name):
        """Switches between the main UI frames (tabs)."""
        tabs = [self.dashboard_tab, self.account_tab, self.mods_tab, 
                self.multiplayer_tab, self.server_tab, self.settings_tab, self.friends_tab]
        for tab in tabs: tab.grid_forget()

        # Reset button colors
        btns = [self.nav_dash_btn, self.nav_acc_btn, self.nav_mods_btn, 
                self.nav_multi_btn, self.nav_server_btn, self.nav_settings_btn, self.nav_friends_btn]
        for btn in btns: btn.configure(fg_color="transparent")

        # Update RPC
        rpc_map = {
            "dashboard": "Browsing Dashboard",
            "account": "Managing Profile",
            "mods": "Managing Mods",
            "friends": "Managing P2P Friends",
            "multiplayer": "Browsing Servers",
            "server": "Managing Dedicated Server",
            "settings": "Adjusting Settings"
        }
        self.update_rpc("In Launcher", rpc_map.get(tab_name, "Main Menu"))

        if tab_name == "dashboard":
            self.dashboard_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_dash_btn.configure(fg_color=self.theme_teal)
        elif tab_name == "account":
            self.account_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_acc_btn.configure(fg_color=self.theme_accent)
        elif tab_name == "mods":
            self.mods_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_mods_btn.configure(fg_color=self.theme_accent)
        elif tab_name == "friends":
            self.friends_tab.grid(row=0, column=0, sticky="nsew")
            self.nav_friends_btn.configure(fg_color=self.theme_accent)
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
        self.acc_user_entry.delete(0, "end")
        self.acc_user_entry.insert(0, p["username"])
        self.acc_uuid_entry.delete(0, "end")
        self.acc_uuid_entry.insert(0, p["uuid"])
        self.acc_avatar_text.delete("1.0", "end")
        self.acc_avatar_text.insert("1.0", json.dumps(p.get("avatar_data", {}), indent=2))
        self.username_label.configure(text=p["username"])

    # --- PROCESS MANAGEMENT ---

    def start_client_thread(self): threading.Thread(target=self.launch_client, daemon=True).start()
    def start_server_thread(self): threading.Thread(target=self.launch_server, daemon=True).start()

    def launch_client(self, server_address=None):
        p = self.get_active_profile()
        game_root = self.data.get("game_root", "")
        client_exe = os.path.join(game_root, "Client", "HytaleClient.exe")
        if not os.path.exists(client_exe):
            self.log_message(f"Error: Game binaries missing. Check settings.", "error")
            return
            
        self.update_rpc("Playing Hytale", f"User: {p['username']}")
        
        user_dir = os.path.join(os.environ['APPDATA'], "Hytale")
        
        # Core arguments
        args = [
            client_exe, 
            "--name", p["username"], 
            "--uuid", p["uuid"],
            "--app-dir", game_root,
            "--user-dir", user_dir,
            "--tcp"
        ]

        if self.launch_mode.get() == "simulated":
            # Generate a payload that satisfies internal client verification
            token_body = {
                "sub": p["uuid"], 
                "name": p["username"], 
                "roles": ["player", "admin"],
                "scope": "hytale:client",
                "iat": int(time.time())
            }
            token = base64.urlsafe_b64encode(json.dumps(token_body).encode()).decode().rstrip('=')
            
            # Use authenticated mode to unlock the UI
            args.extend(["--identity-token", f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{token}.signature"])
            args.extend(["--session-token", f"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.{token}.signature"])
            args.extend(["--auth-mode", "authenticated"])
            
            self.log_message("Multiplayer: Simulated Authentication enabled. (Ensure hosts file points api.hytale.com to 127.0.0.1)", "sys")
        else:
            args.extend(["--auth-mode", "offline"])

        if server_address:
            args.extend(["--connect", server_address])
            
        j = self.get_java_path()
        if j: args.extend(["--java-exec", j])
        
        self.run_process(args, os.path.dirname(client_exe), "CLIENT")
        
        self.update_rpc("In Launcher", "Dashboard")

    def launch_server(self):
        game_root = self.data.get("game_root", "")
        server_jar = os.path.join(game_root, "Server", "HytaleServer.jar")
        assets_zip = os.path.join(game_root, "Assets.zip")
        java_exe = self.get_java_path() or "java"
        if not os.path.exists(server_jar):
            self.log_message(f"Error: HytaleServer.jar not found at {server_jar}", "error")
            return
        
        self.update_rpc("Hosting Hytale Server", "Dedicated Instance")
        
        server_data_dir = os.path.join(os.path.expanduser("~"), "Documents", "HyLauncher", "ServerData")
        backup_dir = os.path.join(server_data_dir, "Backup")
        if not os.path.exists(backup_dir): os.makedirs(backup_dir)
        
        args = [
            java_exe, "-jar", server_jar, 
            "--assets", assets_zip, 
            "--auth-mode", "offline", 
            "--backup", 
            "--backup-dir", backup_dir, 
            "--backup-frequency", "15"
        ]
        self.run_process(args, server_data_dir, "SERVER")
        
        self.update_rpc("In Launcher", "Server Manager")

    def run_process(self, args, cwd, prefix):
        try:
            p = subprocess.Popen(args, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            while True:
                line = p.stdout.readline()
                if not line and p.poll() is not None: break
                if line: self.log_message(line.strip(), prefix.lower())
        except Exception as e: self.log_message(f"Process failed: {str(e)}", "error")

    def check_files(self):
        game_root = self.data.get("game_root", "")
        if not os.path.exists(os.path.join(game_root, "Client", "HytaleClient.exe")):
            self.log_message("Warning: Hytale binaries not found. Please browse to game folder.", "warn")
            
    def get_java_path(self):
        game_root = self.data.get("game_root", "")
        p = os.path.dirname(os.path.dirname(os.path.dirname(game_root)))
        j = os.path.join(p, "jre", "latest", "bin", "java.exe")
        return j if os.path.exists(j) else None

    # --- PROFILE MGMT ---

    def save_profile_event(self):
        try:
            self.data["profile"].update({
                "username": self.acc_user_entry.get(),
                "uuid": self.acc_uuid_entry.get(),
                "avatar_data": json.loads(self.acc_avatar_text.get("1.0", "end-1c")) if self.acc_avatar_text.get("1.0", "end-1c").strip() else {}
            })
            self.save_all_data()
            self.username_label.configure(text=self.data["profile"]["username"])
            self.log_message("Profile updated.", "sys")
        except Exception as e: self.log_message(f"Update error: {e}", "error")

    # --- SERVER MGMT ---

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
        name, addr = self.srv_name_entry.get(), self.srv_addr_entry.get()
        if name and addr:
            self.data["servers"].append({"name": name, "address": addr})
            self.save_all_data(); self.refresh_server_list()
            self.srv_name_entry.delete(0, "end"); self.srv_addr_entry.delete(0, "end")

    def delete_server_event(self, idx):
        self.data["servers"].pop(idx); self.save_all_data(); self.refresh_server_list()

    def join_server_direct(self, address): threading.Thread(target=lambda: self.launch_client(server_address=address), daemon=True).start()
    def regen_uuid(self): self.acc_uuid_entry.delete(0, "end"); self.acc_uuid_entry.insert(0, str(uuid.uuid4()))

    # --- SETTINGS MGMT ---

    def browse_game_path(self):
        folder = filedialog.askdirectory()
        if folder: self.settings_path_entry.delete(0, "end"); self.settings_path_entry.insert(0, folder)

    def auto_detect_game(self):
        self.log_message("Automated scanner active...", "sys")
        found_path = None
        for drive in ['C', 'D', 'E', 'F']:
            for sub in [r"Hytale\game\latest", r"dl\install\release\package\game\latest"]:
                tp = f"{drive}:\\{sub}"
                if os.path.exists(os.path.join(tp, "Client", "HytaleClient.exe")): found_path = tp; break
            if found_path: break
        if found_path: self.settings_path_entry.delete(0, "end"); self.settings_path_entry.insert(0, found_path)

    def save_settings_event(self):
        np = self.settings_path_entry.get().strip()
        if os.path.exists(os.path.join(np, "Client", "HytaleClient.exe")): self.data["game_root"] = np; self.save_all_data(); self.log_message("Global settings synced.", "sys")
        else: self.log_message("Invalid path.", "error")

    def on_closing(self):
        """Clean up resources before closing."""
        self._is_shutting_down = True
        self.log_message("System: Shutting down gracefully...", "sys")
        self.destroy()
        sys.exit(0)

if __name__ == "__main__":
    app = HyLauncherApp()
    app.mainloop()