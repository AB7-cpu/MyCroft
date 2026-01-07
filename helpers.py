# helpers.py
import pygetwindow as gw
import pyautogui
from typing import Optional

def list_windows() -> list[str]:
    return [w.title for w in gw.getAllWindows() if w.title.strip()]

def find_window(title_keyword: str):
    for w in gw.getAllWindows():
        if title_keyword.lower() in w.title.lower():
            return w
    return None

def focus_window(title_keyword: str) -> str:
    w = find_window(title_keyword)
    if not w:
        return f"Window containing '{title_keyword}' not found."
    w.activate()
    return f"Focused window: '{w.title}'"

def minimize_window(title_keyword: str) -> str:
    w = find_window(title_keyword)
    if not w:
        return f"Window containing '{title_keyword}' not found."
    w.minimize()
    return f"Minimized window: '{w.title}'"

def maximize_window(title_keyword: str) -> str:
    w = find_window(title_keyword)
    if not w:
        return f"Window containing '{title_keyword}' not found."
    w.maximize()
    return f"Maximized window: '{w.title}'"

def close_window(title_keyword: str) -> str:
    w = find_window(title_keyword)
    if not w:
        return f"Window containing '{title_keyword}' not found."
    try:
        w.close()
        return f"Closed window: '{w.title}'"
    except Exception:
        return f"Failed to close window '{w.title}'. Try manually."

def screenshot_window(title_keyword: str, save_path: Optional[str] = None) -> str:
    w = find_window(title_keyword)
    if not w:
        return f"Window containing '{title_keyword}' not found."
    bbox = (w.left, w.top, w.left + w.width, w.top + w.height)
    img = pyautogui.screenshot(region=bbox)
    if not save_path:
        save_path = f"{title_keyword.replace(' ', '_')}.png"
    img.save(save_path)
    return f"Screenshot saved: {save_path}"
