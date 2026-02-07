import pyautogui
import time 
import ctypes 

class KeyboardActions:
    def __init__(self, cooldown=0.5):
        """ cooldown -> minimum time between actions to prevent accidental spam"""
        self.cooldown = cooldown
        self.last_press_time = 0

    def _log_action(self, action_name):
        """prints a clean message for debugging in terminal"""
        print(f"[{time.strftime('%H:%M:%S')}] KEYBOARD: {action_name}")
    
    def _can_press(self):
        """checks if enough time has passed since the last action"""
        now = time.time()
        if now - self.last_press_time >= self.cooldown:
            self.last_press_time = now
            return True
        return False

    # ── GENERIC HELPERS ──────────────────────────────────────────────
    def press_key(self, key: str):
        """press a single key like 'enter', 'esc', 'f' , etc """
        if self._can_press():
            pyautogui.press(key)
            self._log_action(f"Pressed '{key}'")

    def press_hotkeys(self, keys: list):
        """press combo keys like ctrl + c, ctrl + v, etc"""
        if self._can_press():
            pyautogui.press(*keys)
            self._log_action(f"Hotkey {" + ".join(keys)}")

    # ── ESSENTIAL ACTIONS ────────────────────────────────────────────
    def copy(self):
        self.press_hotkeys(['ctrl','c'])
    
    def cut(self):
        self.press_hotkeys(['ctrl','x'])

    def paste(self):
        self.press_hotkeys(['ctrl','v'])
    
    def undo(self):
        self.press_hotkeys(['ctrl','z'])
    
    def redo(self):
        self.press_hotkeys(['ctrl','y'])
    
    def select_all(self):
        self.press_hotkeys(['ctrl','a'])

    def screenshot(self):
        self.press_hotkeys(['win','prtscr'])
    
    def switch_window(self):
        if self._can_press():
            self.press_hotkeys(['alt','tab'])
    
    def task_view(self):
        self.press_hotkeys(['win','tab'])
    
    # ── SCROLLING & NAVIGATION ───────────────────────────────────────
    def scroll_up(self, amount=300):
        """as scroll often needs no cooldown or faster one, so we bypass normal cooldown"""
        pyautogui.scroll(amount)
    
    def scroll_down(self, amount=-300):
        pyautogui.scroll(amount)
    
    def page_up(self):
        self.press_key('pgup')
    
    def page_down(self):
        self.press_key('pgdn')

    # ── MEDIA CONTROLS ───────────────────────────────────────────────
    def volume_up(self):
        pyautogui.press('volumeup')

    def volume_down(self):
        pyautogui.press('volumedown')
    
    def volume_mute(self):
        pyautogui.press('volumemute')
        self._log_action("Mute/Unmute")
    
    def play_pause(self):
        pyautogui.press('playpause')
        self._log_action('Media Play/Pause')
    
    # ── SYSTEM ───────────────────────────────────────────────────────
    def lock_windows(self):
        """we bypass delay here"""
        print(">>> Windows Locking Activated")
        ctypes.windll.user32.LockWorkStation()
        self.last_press_time = time.time() + 2.0 # Add extra delay after locking