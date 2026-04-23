# Practice 09: Game Development with Pygame (Part 1)

This repository contains the first part of Practice 09, focusing on the fundamentals of game development using the **Pygame** library. The project consists of three distinct applications: a synchronized clock, a music player, and an interactive moving ball game.

## 🚀 Projects Overview

### 1. Mickey's Clock Application
A digital-style analog clock that synchronizes with the system time.
* **Features:** Uses custom graphics for clock hands (Mickey Mouse hands).
* **Logic:** The right hand represents minutes, and the left hand represents seconds. 
* **Math:** Angles are calculated in real-time based on system seconds and minutes using `pygame.transform.rotate()`.

### 2. Music Player
A keyboard-controlled audio player for managing playlists.
* **Controls:**
    * `P`: Play / Resume
    * `S`: Stop
    * `N`: Next Track
    * `B`: Previous Track (Back)
* **Features:** Displays track information and handles multiple audio files using `pygame.mixer`.

### 3. Moving Ball
A simple interactive game testing coordinate handling and boundary logic.
* **Controls:** Arrow keys (Up, Down, Left, Right).
* **Mechanics:** The ball moves in increments of 20 pixels.
* **Constraints:** Includes strict boundary checking to prevent the ball from moving off-screen.

---

## 🛠 Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    ```
2.  **Navigate to the project folder:**
    ```bash
    cd Practice7
    ```
3.  **Install dependencies:**
    Make sure you have Python installed, then run:
    ```bash
    pip install -r requirements.txt
    ```

---

## 📂 Repository Structure

```text
Practice7/
├── mickeys_clock/
│   ├── main.py          # Application entry point
│   ├── clock.py         # Logic for time calculation & rotation
│   └── images/          # Assets for the clock
├── music_player/
│   ├── main.py          # Keyboard event handling
│   ├── player.py        # Mixer logic & playlist management
│   └── music/           # Audio files (MP3/WAV)
├── moving_ball/
│   ├── main.py          # Game loop and drawing
│   └── ball.py          # Boundary logic
├── requirements.txt     # Project dependencies
└── README.md            # Project documentation
