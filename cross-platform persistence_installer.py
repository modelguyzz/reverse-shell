import os
import sys
import platform

def install_persistence(script_path: str, service_name: str):
    """
    Installs a Python script to run automatically at startup for the current user.

    Args:
        script_path (str): Full path to the Python script.
        service_name (str): Name of the service/entry.
    """
    system = platform.system()
    script_path = os.path.abspath(script_path)

    if system == "Windows":
        try:
            import winreg
        except ImportError:
            raise RuntimeError("winreg module required on Windows")

        # Open the registry key for current user auto-run programs
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE
        )

        # Use pythonw.exe to avoid opening a console window. made by modelguyzz
        python_exe = sys.executable
        if python_exe.lower().endswith("python.exe"):
            python_exe = python_exe.replace("python.exe", "pythonw.exe")

        command = f'"{python_exe}" "{script_path}"'
        winreg.SetValueEx(key, service_name, 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)
        print(f"[Windows] Persistence installed: {command}")

    elif system == "Darwin":  # macOS
        plist_dir = os.path.expanduser("~/Library/LaunchAgents")
        os.makedirs(plist_dir, exist_ok=True)
        plist_path = os.path.join(plist_dir, f"{service_name}.plist")
        plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple Computer//DTD PLIST 1.0//EN" 
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
  <dict>
    <key>Label</key>
    <string>{service_name}</string>
    <key>ProgramArguments</key>
    <array>
      <string>{sys.executable}</string>
      <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
  </dict>
</plist>
"""
        with open(plist_path, "w") as f:
            f.write(plist_content)
        print(f"[macOS] Persistence installed at {plist_path}")

    elif system == "Linux":
        autostart_dir = os.path.expanduser("~/.config/autostart")
        os.makedirs(autostart_dir, exist_ok=True)
        desktop_file_path = os.path.join(autostart_dir, f"{service_name}.desktop")
        desktop_content = f"""[Desktop Entry]
Type=Application
Exec={sys.executable} {script_path}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
Name={service_name}
Comment=Autostart Python script
"""
        with open(desktop_file_path, "w") as f:
            f.write(desktop_content)
        print(f"[Linux] Persistence installed at {desktop_file_path}")
#made by modelguyzz
    else:
        raise NotImplementedError(f"OS '{system}' is not supported")
