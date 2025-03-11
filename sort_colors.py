import time
import numpy as np
import pyautogui
import cv2
from PIL import Image, ImageGrab
import copy
from collections import deque


class ColorSortAutomation:
    def __init__(self):
        # Color recognition thresholds (RGB values)
        self.color_definitions = {
            'red': {'lower': np.array([150, 0, 0]), 'upper': np.array([255, 80, 80])},
            'blue': {'lower': np.array([0, 0, 150]), 'upper': np.array([80, 80, 255])},
            'green': {'lower': np.array([0, 150, 0]), 'upper': np.array([80, 255, 80])},
            'yellow': {'lower': np.array([150, 150, 0]), 'upper': np.array([255, 255, 80])},
            'purple': {'lower': np.array([150, 0, 150]), 'upper': np.array([255, 80, 255])},
            'orange': {'lower': np.array([200, 100, 0]), 'upper': np.array([255, 180, 80])},
            'cyan': {'lower': np.array([0, 150, 150]), 'upper': np.array([80, 255, 255])},
            'pink': {'lower': np.array([220, 100, 170]), 'upper': np.array([255, 180, 230])},
        }

        # Positions will be detected or set during calibration
        self.tube_positions = []
        self.max_capacity = 4  # Default, will be detected

    def calibrate(self):
        """
        Calibrate the system by detecting the tubes on screen.
        The user should show the game in its initial state.
        """
        print("Calibration starting. Please ensure the game is visible on screen.")
        print("Press Enter when ready...")
        input()

        # Take a screenshot
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)
        screenshot_rgb = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2RGB)

        # Save screenshot for debugging
        cv2.imwrite("calibration_screenshot.png", screenshot_np)

        # Find tube positions (simplified version - actual implementation would use more robust detection)
        # In a real implementation, this would use computer vision to detect the tubes
        print("Please click on the center of each tube from left to right.")
        print("Press Enter when ready to start clicking...")
        input()

        self.tube_positions = []
        print("Click on each tube and press Enter after each click. Press Esc when done.")

        while True:
            time.sleep(0.5)  # Wait for user to position mouse
            x, y = pyautogui.position()
            print(f"Position recorded: ({x}, {y})")
            self.tube_positions.append((x, y))

            key = input("Press Enter for next tube or type 'done' to finish: ")
            if key.lower() == 'done':
                break

        print(f"Detected {len(self.tube_positions)} tubes at positions: {self.tube_positions}")

        # Detect max capacity by analyzing the first tube
        # This is a simplified approach - real implementation would be more robust
        self.max_capacity = 4  # Most common in these games
        print(f"Max capacity set to {self.max_capacity}")

        return True

    def capture_game_state(self):
        """
        Capture the current state of the game by taking a screenshot
        and analyzing the colors in each tube.
        """
        if not self.tube_positions:
            print("Error: Please calibrate the system first.")
            return None

        # Take a screenshot
        screenshot = ImageGrab.grab()
        screenshot_np = np.array(screenshot)

        # Initialize tubes
        tubes = [[] for _ in range(len(self.tube_positions))]

        # Analysis radius (pixels around the center to check)
        radius = 15
        height_step = 30  # Vertical distance between color positions

        # For each tube position
        for tube_idx, (tube_x, tube_y) in enumerate(self.tube_positions):
            # Check positions from bottom to top
            for level in range(self.max_capacity):
                # Calculate the pixel position to check
                check_y = tube_y + (self.max_capacity - 1 - level) * height_step

                # Extract a small region around the position
                roi = screenshot_np[check_y - radius:check_y + radius, tube_x - radius:tube_x + radius]

                if roi.size == 0:
                    continue  # Skip if region is outside the screen

                # Calculate average color in the region
                avg_color = np.mean(roi, axis=(0, 1))

                # Skip if the average color is close to white/background (empty)
                if np.all(avg_color > 220):
                    continue

                # Match the color to our defined colors
                detected_color = self._match_color(avg_color)
                if detected_color:
                    tubes[tube_idx].append(detected_color)

        print("Detected game state:")
        for i, tube in enumerate(tubes):
            print(f"Tube {i}: {tube}")

        return tubes

    def _match_color(self, rgb_value):
        """
        Match an RGB value to the closest defined color.
        """
        min_distance = float('inf')
        best_match = None

        for color_name, thresholds in self.color_definitions.items():
            lower = thresholds['lower']
            upper = thresholds['upper']

            # Check if the color is within thresholds
            if np.all(rgb_value >= lower) and np.all(rgb_value <= upper):
                # Calculate distance to ideal color (center of range)
                ideal = (lower + upper) / 2
                distance = np.sum(np.square(rgb_value - ideal))

                if distance < min_distance:
                    min_distance = distance
                    best_match = color_name

        return best_match

    def execute_move(self, from_tube, to_tube):
        """
        Execute a move by clicking on the source tube and then the destination tube.
        """
        if not self.tube_positions:
            print("Error: Please calibrate the system first.")
            return False

        # Get tube positions
        from_pos = self.tube_positions[from_tube]
        to_pos = self.tube_positions[to_tube]

        # Click source tube
        pyautogui.click(from_pos[0], from_pos[1])
        time.sleep(0.5)  # Wait for animation

        # Click destination tube
        pyautogui.click(to_pos[0], to_pos[1])
        time.sleep(0.5)  # Wait for animation

        print(f"Executed move: Tube {from_tube} to Tube {to_tube}")
        return True


class ColorSortPuzzle:
    def __init__(self, tubes):
        """
        Initialize the puzzle with a list of tubes.
        Each tube is represented as a list of colors.
        """
        self.tubes = tubes
        self.max_capacity = max(len(tube) for tube in tubes) if tubes else 4
        self.moves_history = []

    def is_solved(self):
        """
        Check if the puzzle is solved.
        A puzzle is solved when each tube either:
        1. Is empty, or
        2. Is full with the same color
        """
        for tube in self.tubes:
            if len(tube) == 0:
                continue
            if len(tube) != self.max_capacity:
                return False
            if any(tube[0] != color for color in tube):
                return False
        return True

    def is_valid_move(self, from_tube, to_tube):
        """
        Check if pouring from one tube to another is valid.
        """
        # Can't pour from empty tube
        if not self.tubes[from_tube]:
            return False

        # Can't pour into a full tube
        if len(self.tubes[to_tube]) >= self.max_capacity:
            return False

        # Can't pour if source and destination are the same
        if from_tube == to_tube:
            return False

        # Can only pour if colors match or destination is empty
        from_color = self.tubes[from_tube][-1]
        if self.tubes[to_tube] and self.tubes[to_tube][-1] != from_color:
            return False

        # No need to pour from a tube to an identical tube
        if from_tube < to_tube and not self.tubes[to_tube] and all(
                color == from_color for color in self.tubes[from_tube]):
            return False

        return True

    def make_move(self, from_tube, to_tube):
        """
        Make a move by pouring from one tube to another.
        Will pour all consecutive matching colors.
        """
        if not self.is_valid_move(from_tube, to_tube):
            return False

        from_color = self.tubes[from_tube][-1]
        transfer_amount = 0

        # Count how many of the same color we can transfer
        for i in range(len(self.tubes[from_tube]) - 1, -1, -1):
            if self.tubes[from_tube][i] == from_color:
                transfer_amount += 1
            else:
                break

        # Limit transfer by available space in destination
        available_space = self.max_capacity - len(self.tubes[to_tube])
        transfer_amount = min(transfer_amount, available_space)

        # Transfer the colors
        for _ in range(transfer_amount):
            self.tubes[to_tube].append(self.tubes[from_tube].pop())

        self.moves_history.append((from_tube, to_tube))
        return True

    def get_state_hash(self):
        """
        Create a unique hash representing the current state.
        """
        return tuple(tuple(tube) for tube in self.tubes)

    def solve(self):
        """
        Solve the puzzle using Breadth-First Search.
        Returns a list of moves (from_tube, to_tube) that solve the puzzle.
        """
        start_time = time.time()
        queue = deque([(copy.deepcopy(self.tubes), [])])
        visited = set()
        visited.add(self.get_state_hash())

        while queue:
            current_tubes, moves = queue.popleft()

            # Load the current state
            self.tubes = current_tubes

            # Check if solved
            if self.is_solved():
                end_time = time.time()
                print(f"Solution found in {len(moves)} moves")
                print(f"Time taken: {end_time - start_time:.2f} seconds")
                return moves

            # Try all possible moves
            for from_tube in range(len(self.tubes)):
                for to_tube in range(len(self.tubes)):
                    if self.is_valid_move(from_tube, to_tube):
                        # Make a copy of the current state
                        new_tubes = copy.deepcopy(self.tubes)

                        # Apply the move
                        self.tubes = copy.deepcopy(new_tubes)
                        self.make_move(from_tube, to_tube)

                        # Check if we've seen this state before
                        state_hash = self.get_state_hash()
                        if state_hash not in visited:
                            visited.add(state_hash)
                            new_moves = moves + [(from_tube, to_tube)]
                            queue.append((copy.deepcopy(self.tubes), new_moves))

                        # Restore the original state
                        self.tubes = new_tubes

        print("No solution found!")
        return None


def main():
    print("=== Automated Color Sort Puzzle Solver ===")
    print("This program will solve a color sort puzzle game automatically.")
    print("Requirements:")
    print("1. Python 3.6+")
    print("2. Installed libraries: numpy, pyautogui, opencv-python (cv2), pillow")
    print("3. The game should be visible on screen")
    print("\nMake sure the game is visible before proceeding.\n")

    # Initialize the automation system
    automation = ColorSortAutomation()

    # Calibrate
    print("Starting calibration...")
    if not automation.calibrate():
        print("Calibration failed. Exiting.")
        return

    while True:
        # Capture current game state
        print("Capturing game state...")
        tubes = automation.capture_game_state()
        if not tubes:
            print("Failed to capture game state. Exiting.")
            return

        # Create puzzle solver
        puzzle = ColorSortPuzzle(tubes)

        # Check if already solved
        if puzzle.is_solved():
            print("Puzzle is already solved!")
            break

        # Solve the puzzle
        print("Solving puzzle...")
        solution = puzzle.solve()

        if not solution:
            print("Could not find a solution. The puzzle might be impossible or there was an error in detection.")
            break

        # Execute the solution
        print(f"Executing solution ({len(solution)} moves)...")
        for i, (from_tube, to_tube) in enumerate(solution):
            print(f"Move {i + 1}/{len(solution)}: Tube {from_tube} to Tube {to_tube}")
            if not automation.execute_move(from_tube, to_tube):
                print("Failed to execute move. Stopping.")
                break
            time.sleep(1)  # Wait between moves

            # Re-capture state after each move to handle any animations or game events
            new_tubes = automation.capture_game_state()
            if new_tubes:
                puzzle.tubes = new_tubes
                if puzzle.is_solved():
                    print("Puzzle solved!")
                    break

        # Check if solved
        final_tubes = automation.capture_game_state()
        final_puzzle = ColorSortPuzzle(final_tubes)
        if final_puzzle.is_solved():
            print("Puzzle successfully solved!")
            break
        else:
            print("Puzzle not solved yet. Starting another round of solving...")
            time.sleep(2)  # Wait before starting again

    print("Automation complete.")


if __name__ == "__main__":
    main()