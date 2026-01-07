# tools.py
from langchain_core.tools import tool
from pydantic import Field
import pywhatkit as kt
import time
from serial import Serial
from langchain_tavily import TavilySearch
from datetime import datetime
import psutil
import subprocess
from typing import Optional
import requests
import json
from dotenv import load_dotenv

load_dotenv()


from helpers import (
    list_windows,
    focus_window,
    minimize_window,
    maximize_window,
    close_window,
    screenshot_window,
)

# ser = Serial('COM8', 9600, timeout=1)

@tool
def play_on_yt(query: str):
    """Play a video or song on YouTube based on the search query."""
    try:
        kt.playonyt(query)
        return f"Playing '{query}' on YouTube."
    except Exception as e:
        return f"Failed to play '{query}' on YouTube. Error: {str(e)}"

# @tool
# def color_changer(r: int = Field(range(0,255)), g: int = Field(range(0,255)), b: int = Field(range(0,255))) -> bool:
#     """Change studio light color using RGB values (0–255). Returns True if successful."""
#     try:
#         ser.write(bytes([r, g, b]))
#         time.sleep(0.1)
#         return True
#     except Exception as e:
#         return f"Failed to change color: {e}"

@tool
def window_tool(action: str, target: str = None) -> str:
    """
    Manage windows: list, focus, minimize, maximize, close, screenshot.
    - action: one of 'list', 'focus', 'minimize', 'maximize', 'close', 'screenshot'
    - target: window title keyword (not required for 'list')
    """
    action = action.lower()
    if action == "list":
        wins = list_windows()
        return "\n".join(wins) if wins else "No windows found."
    elif action == "focus":
        return focus_window(target)
    elif action == "minimize":
        return minimize_window(target)
    elif action == "maximize":
        return maximize_window(target)
    elif action == "close":
        return close_window(target)
    elif action == "screenshot":
        return screenshot_window(target)
    else:
        return f"Invalid action '{action}'."


search_tool = TavilySearch(
    max_results=5,
    search_depth="basic",
    country="india",
    topic="general",
)

@tool
def get_current_date_time():
    """Get the current date, day, and time with AM/PM format."""
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    day_str = now.strftime("%A")        # Full weekday name
    time_str = now.strftime("%I:%M %p") # 12-hour format with AM/PM
    return f"day: {day_str}, date: {date_str}, time: {time_str}"

@tool
def get_system_info(target: Optional[str] = None) -> str:
    """
    Get system information. You can specify a target to get selective info:
    'battery' -> battery status
    'wifi' -> Wi-Fi status
    If no target is specified, returns all available info.

    Args:
        target (str, optional): 'battery', 'wifi', or None

    Returns:
        str: Requested system info
    """
    info = {}

    # 🔋 Battery Info
    try:
        battery = psutil.sensors_battery()
        if battery:
            percent = battery.percent
            charging = "charging ⚡" if battery.power_plugged else "not charging 🔋"
            info["battery"] = f"Battery: {percent}% ({charging})"
        else:
            info["battery"] = "Battery: Not detected"
    except Exception as e:
        info["battery"] = f"Battery: Error - {str(e)}"

    # 📶 Wi-Fi Info
    try:
        output = subprocess.check_output(
            ["netsh", "wlan", "show", "interfaces"], text=True
        )
        ssid = None
        for line in output.splitlines():
            if "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
                break
        if ssid:
            info["wifi"] = f"Wi-Fi: Connected to {ssid}"
        else:
            info["wifi"] = "Wi-Fi: Not connected"
    except Exception as e:
        info["wifi"] = f"Wi-Fi: Error - {str(e)}"

    if target:
        target = target.lower()
        return info.get(target, f"No info available for '{target}'")
    else:
        # return all info concatenated if no target specified
        return " | ".join(info.values())


def control_wled_impl(
    power: Optional[bool] = None,
    brightness: Optional[int] = None,
    color: Optional[str] = None,
    preset: Optional[int] = None
) -> str:
    """
    Control WLED lights at IP 192.168.1.20.
    Args:
        power: True (On), False (Off)
        brightness: 0-255
        color: Name (e.g., 'red', 'warm white') or Hex (e.g., '#FF0000')
        preset: ID of the preset to apply
    """
    ip = "192.168.1.20"
    url = f"http://{ip}/json/state"
    
    # Color mapping
    COLORS = {
        "red": [255, 0, 0], "green": [0, 255, 0], "blue": [0, 0, 255],
        "white": [255, 255, 255], "warm white": [255, 244, 229], 
        "cool white": [212, 235, 255], "yellow": [255, 255, 0],
        "cyan": [0, 255, 255], "magenta": [255, 0, 255],
        "purple": [128, 0, 128], "orange": [255, 165, 0], 
        "pink": [255, 192, 203]
    }

    state = {}
    
    if power is not None:
        state["on"] = power
    
    if brightness is not None:
        state["bri"] = max(0, min(255, brightness))
        
    if preset is not None:
        state["ps"] = preset
        
    if color:
        rgb = None
        color_lower = color.lower().strip()
        if color_lower in COLORS:
            rgb = COLORS[color_lower]
        elif color_lower.startswith("#") and len(color_lower) == 7:
            try:
                # Hex to RGB
                h = color_lower.lstrip('#')
                rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
            except:
                pass
        
        if rgb:
            # Set primary color for all segments
            state["seg"] = [{"col": [rgb]}]
    
    if not state:
        return "No valid actions provided for WLED."

    try:
        response = requests.post(url, json=state, timeout=2)
        if response.status_code == 200:
            return f"Success: WLED state updated to {json.dumps(state)}"
        else:
            return f"Error: WLED returned status {response.status_code}"
    except Exception as e:
        return f"Failed to connect to WLED at {ip}: {str(e)}"

@tool
def control_wled(
    power: Optional[bool] = None,
    brightness: Optional[int] = None,
    color: Optional[str] = None,
    preset: Optional[int] = None
) -> str:
    """
    Control WLED lights at IP 192.168.1.20.
    Args:
        power: True (On), False (Off)
        brightness: 0-255
        color: Name (e.g., 'red', 'warm white') or Hex (e.g., '#FF0000')
        preset: ID of the preset to apply
    """
    return control_wled_impl(power, brightness, color, preset)

ALL_TOOLS = [play_on_yt, search_tool, window_tool, get_current_date_time, get_system_info, control_wled]
