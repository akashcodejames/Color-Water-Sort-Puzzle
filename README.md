# Color Water Sort Puzzle Solver

An automated solver for the popular Color Water Sort Puzzle game. This Python script uses computer vision and automation to solve color sorting puzzles by identifying tube positions and colors, then calculating and executing the optimal solution.

## Features

- Interactive tube position recording
- Manual color input for each tube
- Automated puzzle solving using recursive algorithm
- Move execution with customizable animation delay
- Robust error handling and validation
- Debug information for unsolvable puzzles

## Requirements

- Python 3.x
- PyAutoGUI
- NumPy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/akashcodejames/Color-Water-Sort-Puzzle.git
```

2. Install required packages:
```bash
pip install pyautogui numpy
```

## Usage

1. Run the script:
```bash
python sort_colors.py
```

2. Follow the on-screen instructions to:
   - Record tube positions by hovering over each tube
   - Input the colors in each tube from bottom to top
   - Let the program calculate and execute the solution

## How It Works

1. The program first records the positions of each tube through user input
2. User inputs the current state of colors in each tube
3. A recursive algorithm finds the optimal solution
4. The solution is executed using PyAutoGUI to simulate clicks

## Screenshot

![Screenshot of the Color Water Sort Puzzle Solver](Screenshot%202025-03-11%20193301.png)
