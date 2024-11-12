# Memory Game

A simple multiplayer memory game built with Python, Flet, and Fletrt, designed for two players over a network, using low-level communications: sockets.

## Details

This project implements a memory card game where two players, a host (server) and a client, compete to find matching pairs of Pokemon images.  The game board is dynamically generated using scraped images, ensuring a different experience each time. Players take turns revealing two cards at a time, earning points for each match. The player with the most points at the end wins.

## Technologies Used

* **Python:** The core programming language.
* **Flet:**  A framework for building real-time web, desktop, and mobile apps in Python. It provides a Flutter-like experience for creating user interfaces.
* **Fletrt:**  A routing library for Flet, simplifying navigation between different pages or views within the application.
* **Requests:** A library for making HTTP requests, used for scraping Pokemon images.
* **Beautiful Soup 4:** A library for parsing HTML and XML, used to extract image URLs from the scraped web page.
* **random-username:** A library to generate random usernames, used if the client doesn't provide one.


## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/PedroG022/ds-memory-game.git # Replace with your repo URL
cd ds-memory-game
```

2. **Create a virtual environment (recommended):**

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies:**

```bash
poetry install
```

## Running the Game

### Web Mode

To run the game in web mode, accessible through a browser:

```bash
poetry run python main.py --web
```

This will start a web server on port 40444 (default).  Open your browser and navigate to `http://localhost:40444` to play.

### Desktop Mode

You can try running the game directly on your desktop (note: this feature is experimental and might not be fully functional):

```bash
poetry run python main.py
```


## Gameplay

1. **Hosting a game:**
    * Run the application with the `--web` or without any arguments.
    * Choose the "Host" option.
    * Enter a port number (e.g., 37001). You may keep the default port 37001.
    * Click "Host".

2. **Joining a game:**
    * Run the application with the `--web` or without any arguments.
    * Choose the "Join" option.
    * Enter the host's IP address and port number (e.g., `127.0.0.1:37001` for a local game).
    * Enter your desired username.
    * Click "Connect".

3. **Playing the game:**
    * The client is the first one to play.
    * Players take turns revealing two cards.
    * If the cards match, the player earns points and the cards remain revealed.
    * If the cards don't match, they are flipped back over.
    * The game continues until all matching pairs are found.
    * The player with the most points wins.
