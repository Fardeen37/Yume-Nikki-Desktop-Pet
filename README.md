<div align="center">
  <img src="Images/MadotsukiDown1.png" alt="Madotsuki Sprite" width="64"/>

  # ✨ Yume Nikki AI Pet ✨

  **A nostalgic, intelligent, and interactive desktop companion**

  ![Python](https://img.shields.io/badge/Python-3.x-blue?logo=python&logoColor=white)
  ![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)
  ![AI](https://img.shields.io/badge/Powered%20by-Gemini%20%7C%20Groq-8A2BE2)
  ![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 🌟 About the Project

**Yume Nikki AI Pet** is a desktop companion built to bring the mysterious, dreamlike atmosphere of the cult classic *Yume Nikki* straight to your screen. It's not just a static sprite sitting in a corner — it's a living, reacting, AI-powered buddy that watches, talks, and wanders with you while you work.

Under the hood, it's driven by real conversational AI (Gemini & Groq), giving it the ability to actually understand and respond to you in character, rather than relying on canned scripted lines.

**Created by Data Fardeen & Amina Asghar — July 2026**

---

## 🎮 Features

| Feature | Description |
|---|---|
| 🧠 **True AI Conversations** | Chat with your pet directly on your desktop through a retro-pixelated chat bubble, styled to match the game's aesthetic |
| 👁️ **Screen Awareness** | After 5 minutes of idle time, your pet gets curious and takes a peek at your screen, reacting to whatever you have open |
| 🎭 **Dynamic Moods & Animations** | Happy, sleepy, angry, musical, and more — moods shift the pet's animations and wandering behavior in real time |
| 🔊 **Immersive Sound Effects** | Poking, switching characters, pulling out the flute, getting angry — every interaction has its own nostalgic sound cue |
| 👥 **Multiple Characters** | Swap between Madotsuki, Urotsuki, Sabitsuki, and Fluorette via the right-click menu |
| 🖱️ **Physics & Interaction** | Drag it around, double-click to play, feed it from the context menu — fully interactive |

---

## 🚀 Getting Started

### 🔑 Getting Your API Keys

To power the AI conversations and vision capabilities, you will need a free API key from either Google Gemini or Groq (or both!):

- **[Get a Gemini API Key](https://aistudio.google.com/app/apikey)** (Google AI Studio) - *Great for both chat and screen-reading vision!*
- **[Get a Groq API Key](https://console.groq.com/keys)** (Groq Console) - *Lightning-fast chat responses!*

### 📦 Option 1 — Just Play (Recommended)

No setup, no dependencies — just run it.

1. Download this repository.
2. Double-click **`Yume Nikki Pet.exe`**.
3. On first launch, you'll be asked for a free **Gemini** or **Groq** API key. Paste ONE of your keys in the prompt and you're good to go!

> **Adding Both Keys Later:** 
> The initial popup only lets you enter one API key to get started quickly. If you want to add the second key later (for example, to use Groq for fast chat and Gemini for vision), simply open the folder where the pet is located. You will find a file named `.env` that was automatically created. Open it with Notepad and add both of your keys like this:
> 
> ```env
> GEMINI_API_KEY=your_gemini_key_here
> GROQ_API_KEY=your_groq_key_here
> ```

### 💻 Option 2 — Run from Source

For developers who want to tinker with the code:

```bash
# 1. Clone the repo
git clone https://github.com/Fardeen37/Yume-Nikki-Desktop-Pet.git
cd Yume-Nikki-Desktop-Pet

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
# Create a file named `.env` in the root folder and add your keys:
# GEMINI_API_KEY=your_gemini_key_here
# GROQ_API_KEY=your_groq_key_here

# 4. Run it
python main.py
```

Want to build your own `.exe`?

```bash
python build_and_package.py
```

---

## 🎨 Design Philosophy

Every visual and audio choice was made to nail a **cute, retro, pixelated** feel — terminal-style fonts, hot-pink borders, soft pink chat backgrounds, all channeling the look of classic 2000s RPG Maker horror games.

From the soft notes of the flute to the pet's aimless wandering across your open windows, the goal was simple: make something small that feels alive.

---

## 🛠️ Tech Stack

- **Python** — core application logic
- **Gemini / Groq API** — conversational AI engine
- **PyInstaller** — packaging into a standalone `.exe`

---

## 👥 Authors

- **Data Fardeen** — [GitHub](https://github.com/Fardeen37) · [LinkedIn](https://linkedin.com/in/data-fardeen-234619289) · [Portfolio](https://datafardeenportfolio.netlify.app/)
- **Amina Asghar** — [GitHub](https://github.com/Amina-Asghar) · [LinkedIn](https://linkedin.com/in/amina-asghar14nb) · [Portfolio](https://amina-asghar-portfolio.netlify.app/)

---

<div align="center">
  <i>Enjoy your new desktop friend 💖</i>
</div>
