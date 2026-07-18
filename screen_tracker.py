import ctypes
import time
import threading
import mss
import os

class ScreenTracker:
    def __init__(self, idle_threshold=300):
        self.idle_threshold = idle_threshold # Default 5 minutes = 300 seconds
        self.last_window_title = ""
        self.last_switch_time = time.time()
        self.running = False
        self.callback = None
        
    def start(self, callback):
        self.callback = callback
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()
        
    def stop(self):
        self.running = False
        
    def _loop(self):
        while self.running:
            title = self.get_active_window_title()
            current_time = time.time()
            
            # Don't trigger if there is no active window
            if not title:
                time.sleep(5)
                continue
            
            if title != self.last_window_title:
                self.last_window_title = title
                self.last_switch_time = current_time
            elif current_time - self.last_switch_time >= self.idle_threshold:
                # Idle time met, take screenshot
                screenshot_path = os.path.abspath("temp_screenshot.png")
                try:
                    with mss.mss() as sct:
                        # Capture the primary monitor
                        monitor = sct.monitors[1]
                        sct_img = sct.grab(monitor)
                        mss.tools.to_png(sct_img.rgb, sct_img.size, output=screenshot_path)
                    
                    if self.callback:
                        self.callback(screenshot_path)
                except Exception as e:
                    print("Screenshot error:", e)
                
                # Reset timer so it doesn't spam
                self.last_switch_time = current_time
                
            time.sleep(5)
            
    def get_active_window_title(self):
        if os.name == 'nt':
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value
        return "Unknown Window"
