"""
urmode - Windows Theme Switcher
System tray application for managing Windows Light/Dark themes
"""

import winreg
import pystray
from PIL import Image
import sys
import threading
import time
from datetime import datetime, timedelta
import requests
import json

class UrMode:
    def __init__(self):
        self.registry_path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
        self.startup_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        self.config_path = r"Software\urmode"
        self.app_name = "urmode"
        self.icon = None
        self.auto_switch_enabled = False
        self.auto_thread = None
        self.running = True
        
    def load_icon(self):
        """Load icon from file or create default"""
        try:
            # Try to load icon.png from the same directory
            icon_path = "icon.png"
            if sys._MEIPASS:
                icon_path = os.path.join(sys._MEIPASS, "icon.png")
            return Image.open(icon_path)
        except:
            # Create default icon if file not found
            width = 64
            height = 64
            image = Image.new('RGBA', (width, height), color=(0, 0, 0, 0))
            from PIL import ImageDraw
            dc = ImageDraw.Draw(image)
            dc.pieslice([8, 8, 56, 56], 90, 270, fill='#FFD700', outline='#FFA500')
            dc.pieslice([8, 8, 56, 56], 270, 90, fill='#4A90E2', outline='#2E5C8A')
            return image
    
    def get_current_theme(self):
        """Get the current theme setting"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
            winreg.CloseKey(key)
            return "Light" if value == 1 else "Dark"
        except:
            return "Unknown"
    
    def set_theme(self, theme_mode, silent=False):
        """Set Windows theme"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.registry_path, 0, winreg.KEY_SET_VALUE)
            
            if theme_mode == "Light":
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 1)
            elif theme_mode == "Dark":
                winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, 0)
                winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, 0)
            
            winreg.CloseKey(key)
            
            if self.icon and not silent:
                self.icon.notify(f"Theme switched to {theme_mode}", "urmode")
                
        except Exception as e:
            if self.icon and not silent:
                self.icon.notify(f"Error: Could not change theme", "urmode")
    
    def is_startup_enabled(self):
        """Check if app runs at startup"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.startup_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, self.app_name)
            winreg.CloseKey(key)
            return True
        except:
            return False
    
    def toggle_startup(self):
        """Toggle startup on/off"""
        try:
            if self.is_startup_enabled():
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.startup_path, 0, winreg.KEY_SET_VALUE)
                winreg.DeleteValue(key, self.app_name)
                winreg.CloseKey(key)
                if self.icon:
                    self.icon.notify("Removed from startup", "urmode")
            else:
                exe_path = sys.executable
                key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.startup_path, 0, winreg.KEY_SET_VALUE)
                winreg.SetValueEx(key, self.app_name, 0, winreg.REG_SZ, f'"{exe_path}"')
                winreg.CloseKey(key)
                if self.icon:
                    self.icon.notify("Added to startup", "urmode")
        except Exception as e:
            if self.icon:
                self.icon.notify(f"Error: {str(e)}", "urmode")
    
    def get_auto_switch_setting(self):
        """Get auto-switch setting from registry"""
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.config_path, 0, winreg.KEY_READ)
            value, _ = winreg.QueryValueEx(key, "AutoSwitch")
            winreg.CloseKey(key)
            return value == 1
        except:
            return False
    
    def set_auto_switch_setting(self, enabled):
        """Save auto-switch setting to registry"""
        try:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, self.config_path)
            winreg.SetValueEx(key, "AutoSwitch", 0, winreg.REG_DWORD, 1 if enabled else 0)
            winreg.CloseKey(key)
        except:
            pass
    
    def get_location(self):
        """Get approximate location based on IP"""
        try:
            response = requests.get('http://ip-api.com/json/', timeout=5)
            data = response.json()
            if data['status'] == 'success':
                return data['lat'], data['lon']
        except:
            pass
        return 42.4084, -71.0648  # Default to Everett, MA
    
    def get_sun_times(self, lat, lon):
        """Get sunrise and sunset times"""
        try:
            url = f'https://api.sunrise-sunset.org/json?lat={lat}&lng={lon}&formatted=0'
            response = requests.get(url, timeout=5)
            data = response.json()
            
            if data['status'] == 'OK':
                sunrise = datetime.fromisoformat(data['results']['sunrise'].replace('Z', '+00:00'))
                sunset = datetime.fromisoformat(data['results']['sunset'].replace('Z', '+00:00'))
                
                # Convert to local time
                from datetime import timezone
                local_tz = datetime.now(timezone.utc).astimezone().tzinfo
                sunrise = sunrise.astimezone(local_tz)
                sunset = sunset.astimezone(local_tz)
                
                return sunrise, sunset
        except:
            pass
        
        # Default times if API fails
        now = datetime.now()
        sunrise = now.replace(hour=6, minute=30, second=0, microsecond=0)
        sunset = now.replace(hour=18, minute=30, second=0, microsecond=0)
        return sunrise, sunset
    
    def auto_switch_worker(self):
        """Background worker for automatic theme switching"""
        lat, lon = self.get_location()
        last_check = None
        
        while self.running and self.auto_switch_enabled:
            now = datetime.now()
            
            # Get sun times once per day
            if last_check is None or now.date() > last_check.date():
                sunrise, sunset = self.get_sun_times(lat, lon)
                last_check = now
            
            # Determine theme based on time
            if sunrise.time() <= now.time() < sunset.time():
                target_theme = "Light"
            else:
                target_theme = "Dark"
            
            # Switch if needed
            current_theme = self.get_current_theme()
            if current_theme != target_theme:
                self.set_theme(target_theme, silent=True)
            
            # Check every 5 minutes
            time.sleep(300)
    
    def toggle_auto_switch(self):
        """Toggle automatic theme switching"""
        self.auto_switch_enabled = not self.auto_switch_enabled
        self.set_auto_switch_setting(self.auto_switch_enabled)
        
        if self.auto_switch_enabled:
            if self.icon:
                self.icon.notify("Auto-switch enabled (sunrise/sunset)", "urmode")
            # Start background thread
            self.auto_thread = threading.Thread(target=self.auto_switch_worker, daemon=True)
            self.auto_thread.start()
        else:
            if self.icon:
                self.icon.notify("Auto-switch disabled", "urmode")
    
    def on_light_clicked(self, icon, item):
        """Handle Light theme selection"""
        self.set_theme("Light")
    
    def on_dark_clicked(self, icon, item):
        """Handle Dark theme selection"""
        self.set_theme("Dark")
    
    def on_startup_clicked(self, icon, item):
        """Toggle startup setting"""
        self.toggle_startup()
    
    def on_auto_switch_clicked(self, icon, item):
        """Toggle auto-switch"""
        self.toggle_auto_switch()
    
    def on_quit(self, icon, item):
        """Exit the application"""
        self.running = False
        icon.stop()
    
    def get_menu_item_state(self, theme):
        """Return checked state for menu items"""
        current = self.get_current_theme()
        return current == theme
    
    def run(self):
        """Start the system tray application"""
        # Load saved auto-switch setting
        self.auto_switch_enabled = self.get_auto_switch_setting()
        if self.auto_switch_enabled:
            self.auto_thread = threading.Thread(target=self.auto_switch_worker, daemon=True)
            self.auto_thread.start()
        
        # Create menu
        menu = pystray.Menu(
            pystray.MenuItem(
                "Light Theme",
                self.on_light_clicked,
                checked=lambda item: self.get_menu_item_state("Light"),
                radio=True
            ),
            pystray.MenuItem(
                "Dark Theme",
                self.on_dark_clicked,
                checked=lambda item: self.get_menu_item_state("Dark"),
                radio=True
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Auto-switch (Sunrise/Sunset)",
                self.on_auto_switch_clicked,
                checked=lambda item: self.auto_switch_enabled
            ),
            pystray.MenuItem(
                "Run at Startup",
                self.on_startup_clicked,
                checked=lambda item: self.is_startup_enabled()
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_quit)
        )
        
        # Create and run icon
        self.icon = pystray.Icon(
            "urmode",
            self.load_icon(),
            "urmode",
            menu
        )
        
        self.icon.run()


if __name__ == "__main__":
    try:
        app = UrMode()
        app.run()
    except Exception as e:
        import traceback
        with open("urmode_error.log", "w") as f:
            f.write(f"Error: {str(e)}\n")
            f.write(traceback.format_exc())
        sys.exit(1)