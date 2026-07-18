import sys
import os
import random
import re
from dotenv import load_dotenv
from PyQt5.QtCore import Qt, QTimer, QPoint, QUrl, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QPixmap, QFont, QPainter, QColor, QPen, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QMenu, QAction, QInputDialog, QLabel, QVBoxLayout
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QSound

from ai_brain import AIBrain
from screen_tracker import ScreenTracker

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the PyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app 
    # path into variable _MEIPASS'. But we want the path of the .exe to load external Images.
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def global_exception_handler(exctype, value, tb):
    import traceback
    with open(os.path.join(BASE_DIR, "crash.txt"), "w") as f:
        traceback.print_exception(exctype, value, tb, file=f)
    sys.__excepthook__(exctype, value, tb)
sys.excepthook = global_exception_handler

class ChatBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet("background-color: #ffb6c1; border: 4px solid #ff1493;")
        
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 25) # Extra bottom margin for the tail
        
        self.label = QLabel("...", self)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            QLabel {
                color: #ff1493;
                font-family: 'Terminal', 'Fixedsys', 'Courier New', monospace;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        self.layout.addWidget(self.label)
        self.hide()
        
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def show_message(self, text, duration=5000):
        # We enforce a maximum width so the bubble doesn't stretch across the entire screen
        self.label.setMaximumWidth(250)
        self.label.setText(text)
        self.label.adjustSize()
        self.adjustSize()
        self.show()
        self.raise_()
        if duration > 0:
            self.timer.start(duration)

    def paintEvent(self, event):
        # We removed the custom paintEvent because it uses a translucent background
        # which fails on this Windows environment. The style sheet handles the border.
        pass


class Pet(QWidget):
    ai_response_signal = pyqtSignal(str)
    ai_vision_response_signal = pyqtSignal(str)
    tts_ready_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        
        self.characters = ["Madotsuki", "Urotsuki", "Sabitsuki", "Fluorette"]
        self.current_character = "Madotsuki"
        self.direction = "Down"
        self.frame = 1
        self.state = "walk"
        self.speed = 3
        
        self.image_path = os.path.join(BASE_DIR, "Images")
        
        self.initUI()
        
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.animate)
        self.anim_timer.start(250)
        
        self.move_timer = QTimer(self)
        self.move_timer.timeout.connect(self.move_pet)
        self.move_timer.start(50)
        
        self.state_timer = QTimer(self)
        self.state_timer.timeout.connect(self.change_state)
        self.state_timer.start(5000)

        self.dragging = False
        self.offset = QPoint()
        
        self.chat_bubble = ChatBubble(None)
        
        self.ai_response_signal.connect(self.handle_ai_response)
        self.ai_vision_response_signal.connect(self.handle_vision_response)
        self.tts_ready_signal.connect(self.handle_tts_ready)
        
        self.media_player = QMediaPlayer()
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

        # Initialize AI
        load_dotenv()
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not gemini_api_key and not groq_api_key:
            api_key, ok = QInputDialog.getText(None, "API Key Required", 
                                               "Please enter your free Gemini or Groq API Key:")
            if not ok or not api_key:
                sys.exit(0)
            
            if api_key.startswith("gsk_"):
                groq_api_key = api_key
                with open(".env", "a") as f:
                    f.write(f"GROQ_API_KEY={api_key}\\n")
            else:
                gemini_api_key = api_key
                with open(".env", "a") as f:
                    f.write(f"GEMINI_API_KEY={api_key}\\n")
                
        self.brain = AIBrain(gemini_api_key, groq_api_key)
        
        # Initialize Screen Tracker
        self.screen_tracker = ScreenTracker(idle_threshold=300) # 5 minutes
        self.screen_tracker.start(self.on_screen_idle)

    def initUI(self):
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
        self.current_pixmap = None
        self.update_image()
        
        screen = QApplication.primaryScreen().geometry()
        self.move(screen.width() // 2, screen.height() // 2)
        
        self.show()

    def paintEvent(self, event):
        if getattr(self, 'current_pixmap', None) and not self.current_pixmap.isNull():
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.current_pixmap)

    def update_image(self):
        if self.state == "sleep":
            filename = f"{self.current_character}Sleep.png"
        elif self.state == "sit":
            filename = f"{self.current_character}Sit{self.frame}.png"
            if not os.path.exists(os.path.join(self.image_path, filename)):
                filename = f"{self.current_character}Sit1.png"
        elif self.state == "pinch":
            filename = f"{self.current_character}Pinch{self.frame}.png"
        elif self.state in ["bicycle", "knife", "flute", "umbrella", "snowwoman", "crick"]:
            state_cap = self.state.capitalize()
            filename = f"{self.current_character}{state_cap}{self.direction}{self.frame}.png"
            if not os.path.exists(os.path.join(self.image_path, filename)):
                filename = f"{self.current_character}{self.direction}{self.frame}.png"
        else:
            filename = f"{self.current_character}{self.direction}{self.frame}.png"
            
        filepath = os.path.join(self.image_path, filename)
        
        if os.path.exists(filepath):
            pixmap = QPixmap(filepath)
            self.current_pixmap = pixmap.scaled(pixmap.width() * 2, pixmap.height() * 2, Qt.KeepAspectRatio, Qt.FastTransformation)
            self.setMask(self.current_pixmap.mask())
            self.resize(self.current_pixmap.size())
            self.update()

    def animate(self):
        if self.state in ["walk", "idle", "bicycle", "knife", "flute", "umbrella", "snowwoman", "crick"]:
            self.frame += 1
            if self.frame > 3:
                self.frame = 1
        elif self.state == "sit":
            self.frame += 1
            if self.frame > 4:
                self.frame = 1
        elif self.state == "pinch":
            self.frame += 1
            if self.frame > 3:
                self.frame = 1
        
        self.update_image()
        self.update_bubble_position()

    def update_bubble_position(self):
        if self.chat_bubble.isVisible():
            x = self.x() + (self.width() // 2) - (self.chat_bubble.width() // 2)
            y = self.y() - self.chat_bubble.height()
            self.chat_bubble.move(x, y)

    def play_sound(self, filename):
        sound_path = os.path.join(BASE_DIR, "Sounds", filename)
        if os.path.exists(sound_path):
            QSound.play(sound_path)

    def change_state(self):
        if self.dragging:
            return
            
        actions = ["walk", "idle", "sleep", "sit"]
        weights = [0.6, 0.2, 0.1, 0.1]
        self.state = random.choices(actions, weights)[0]
        self.frame = 1
        
        if self.state == "walk":
            directions = ["Up", "Down", "Left", "Right"]
            self.direction = random.choice(directions)
            
        self.state_timer.start(random.randint(3000, 8000))

    def move_pet(self):
        if self.state == "walk" and not self.dragging:
            pos = self.pos()
            screen = QApplication.primaryScreen().geometry()
            
            if self.direction == "Up":
                pos.setY(pos.y() - self.speed)
                if pos.y() < 0: self.direction = "Down"
            elif self.direction == "Down":
                pos.setY(pos.y() + self.speed)
                if pos.y() > screen.height() - self.height(): self.direction = "Up"
            elif self.direction == "Left":
                pos.setX(pos.x() - self.speed)
                if pos.x() < 0: self.direction = "Right"
            elif self.direction == "Right":
                pos.setX(pos.x() + self.speed)
                if pos.x() > screen.width() - self.width(): self.direction = "Left"
                
            self.move(pos)
            self.update_bubble_position()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.globalPos() - self.pos()
            self.state = "pinch"
            self.frame = 1
            self.update_image()
            self.play_sound("PinchCheek.wav")
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.play_sound("Effect Use.wav")
            self.interact_with_pet("*The user just poked you playfully with their mouse cursor!*")

    def mouseMoveEvent(self, event):
        if self.dragging:
            self.move(event.globalPos() - self.offset)
            self.update_bubble_position()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.change_state()

    def show_context_menu(self, pos):
        self.play_sound("Menu Open.wav")
        menu = QMenu(self)
        
        chat_action = QAction("Chat with Pet", self)
        chat_action.triggered.connect(self.open_chat)
        menu.addAction(chat_action)
        
        feed_action = QAction("Feed Pet", self)
        feed_action.triggered.connect(lambda: self.interact_with_pet("*The user just gave you a yummy snack!*"))
        menu.addAction(feed_action)
        
        pet_action = QAction("Pet the Pet", self)
        pet_action.triggered.connect(lambda: self.interact_with_pet("*The user is gently petting your head.*"))
        menu.addAction(pet_action)
        
        char_menu = menu.addMenu("Change Character")
        for char in self.characters:
            action = QAction(char, self)
            action.triggered.connect(lambda checked, c=char: self.change_character(c))
            char_menu.addAction(action)
            
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(QApplication.instance().quit)
        menu.addAction(quit_action)
        
        menu.exec_(pos)

    def change_character(self, name):
        self.current_character = name
        self.update_image()
        self.play_sound("Spawn NPC.wav")

    def open_chat(self):
        text, ok = QInputDialog.getText(None, "Chat", f"Say something to {self.current_character}:")
        if ok and text:
            self.interact_with_pet(text)
            
    def interact_with_pet(self, text):
        self.chat_bubble.show_message("...", 0) # Loading
        self.brain.generate_chat_response(text, self.current_character, self.ai_response_signal.emit)

    def on_screen_idle(self, image_path):
        self.ai_vision_response_signal.emit("...")
        self.brain.generate_vision_response(image_path, self.current_character, self.ai_vision_response_signal.emit)

    def _apply_mood(self, mood_tag):
        if mood_tag == "SLEEPY":
            self.state = "sleep"
        elif mood_tag == "HAPPY":
            self.state = "walk"
        elif mood_tag == "SAD":
            self.state = "sit"
        elif mood_tag == "SURPRISED":
            self.state = "idle"
            self.direction = "Down"
        elif mood_tag == "ANGRY":
            self.state = "knife"
            self.play_sound("Scream.wav")
        elif mood_tag == "PLAYFUL":
            self.state = "bicycle"
            self.play_sound("Takofuusen.wav")
        elif mood_tag == "SCARED":
            self.state = "crick"
        elif mood_tag == "MUSICAL":
            self.state = "flute"
            self.play_sound(f"flute{random.randint(1, 4)}.wav")
        elif mood_tag == "RELAXED":
            self.state = "umbrella"
        elif mood_tag == "COLD":
            self.state = "snowwoman"
        else:
            self.state = "idle"
            
        self.frame = 1
        self.update_image()

    @pyqtSlot(str)
    def handle_ai_response(self, text):
        if text == "...":
            self.chat_bubble.show_message("...", 0)
            return
            
        mood_tag = "NEUTRAL"
        match = re.match(r"^\[([A-Z]+)\]", text)
        if match:
            mood_tag = match.group(1)
            text = text[match.end():].strip()
            
        self._apply_mood(mood_tag)
        self.chat_bubble.show_message(text, 8000) # Show for 8 seconds
        # No TTS for manual chat

    @pyqtSlot(str)
    def handle_vision_response(self, text):
        if text == "...":
            self.chat_bubble.show_message("...", 0)
            return
            
        mood_tag = "NEUTRAL"
        match = re.match(r"^\[([A-Z]+)\]", text)
        if match:
            mood_tag = match.group(1)
            text = text[match.end():].strip()
            
        self._apply_mood(mood_tag)
        self.chat_bubble.show_message(text, 8000) # Show for 8 seconds
        self.brain.generate_tts(text, self.tts_ready_signal.emit)

    @pyqtSlot(str)
    def handle_tts_ready(self, audio_path):
        self.current_audio_path = audio_path
        url = QUrl.fromLocalFile(audio_path)
        content = QMediaContent(url)
        self.media_player.setMedia(content)
        self.media_player.play()

    def on_media_status_changed(self, status):
        if status == QMediaPlayer.EndOfMedia:
            # Delete the file shortly after playing
            if hasattr(self, 'current_audio_path') and os.path.exists(self.current_audio_path):
                QTimer.singleShot(1000, lambda: self._cleanup_audio())
                
    def _cleanup_audio(self):
        if hasattr(self, 'current_audio_path') and os.path.exists(self.current_audio_path):
            try:
                os.remove(self.current_audio_path)
            except:
                pass

    def closeEvent(self, event):
        self._cleanup_audio()
        super().closeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    pet = Pet()
    sys.exit(app.exec_())
