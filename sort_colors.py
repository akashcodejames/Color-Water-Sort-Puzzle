import time
import pyautogui
import numpy as np
from collections import deque


class TestTubeSolver:
    def __init__(self):
        self.tube_positions = []
        self.tubes = []
        self.max_capacity = 4  # Standard capacity for most tube sorting games
        self.animation_delay = 1.5  # Increased animation delay in seconds

    def get_tube_positions(self):
        """
        Let the user hover over each tube position and record it
        """
        print("Let's record the tube positions:")
        print("Hover your mouse over each tube and press Enter. Type 'done' when finished.")

        tube_index = 0
        while True:
            tube_index += 1
            input(f"Hover over tube {tube_index} and press Enter...")
            x, y = pyautogui.position()
            print(f"Recorded position for tube {tube_index}: ({x}, {y})")
            self.tube_positions.append((x, y))

            if input("Continue? (press Enter or type 'done'): ").lower() == 'done':
                break

        print(f"Recorded {len(self.tube_positions)} tube positions")
        return len(self.tube_positions) > 0

    def get_tube_contents(self):
        """
        Let the user input the colors in each tube
        """
        print("\nNow let's input the colors in each tube.")
        print("For each tube, enter colors from BOTTOM to TOP, separated by commas.")
        print("Leave blank for empty tubes. Type 'done' when finished.")

        self.tubes = []

        for i in range(len(self.tube_positions)):
            while True:
                colors = input(f"Tube {i + 1} contents (bottom to top, comma-separated): ").strip()

                if colors.lower() == 'done':
                    return True

                if not colors:  # Empty tube
                    self.tubes.append([])
                    break

                tube_colors = [color.strip().lower() for color in colors.split(',')]

                if len(tube_colors) > self.max_capacity:
                    print(f"Error: Too many colors. Maximum is {self.max_capacity}")
                    continue

                self.tubes.append(tube_colors)
                break

        print("Recorded tube contents:")
        for i, tube in enumerate(self.tubes):
            print(f"Tube {i + 1}: {tube}")

        return True

    def execute_move(self, from_tube, to_tube):
        """
        Execute a move by clicking on tubes
        """
        if from_tube >= len(self.tube_positions) or to_tube >= len(self.tube_positions):
            print(f"Error: Tube index out of range")
            return False

        # Get positions (0-indexed)
        from_pos = self.tube_positions[from_tube]
        to_pos = self.tube_positions[to_tube]

        # Click source tube
        pyautogui.click(from_pos[0], from_pos[1])
        time.sleep(0.5)  # Wait for animation - increased from 0.3

        # Click destination tube
        pyautogui.click(to_pos[0], to_pos[1])
        time.sleep(self.animation_delay)  # Wait for animation - increased from 0.8

        print(f"Moved: Tube {from_tube + 1} → Tube {to_tube + 1}")
        return True


class TestTubePuzzleSolver:
    def __init__(self, tubes, max_capacity=4):
        self.tubes = [list(tube) for tube in tubes]  # Create a deep copy
        self.max_capacity = max_capacity
        self.moves = []
        self.solution_found = False
        self.solution_moves = []
        self.max_depth = 800  # Limit recursion depth to prevent stack overflow

    def is_solved(self):
        """
        Check if the puzzle is solved - a puzzle is solved when each tube
        either contains liquids of the same color or is empty
        """
        for tube in self.tubes:
            # Empty tube is fine
            if len(tube) == 0:
                continue
                
            # If tube has liquids, they must all be same color and tube must be either full or empty
            if len(tube) == self.max_capacity or len(tube) == 0:
                if len(tube) > 0:
                    first_color = tube[0]
                    if any(color != first_color for color in tube):
                        return False  # Not all same color
            else:
                return False  # Not full or empty
                
        return True

    def is_valid_move(self, from_idx, to_idx):
        """
        Check if a move is valid based on the implemented_sort.py logic
        """
        # Invalid indices
        if from_idx >= len(self.tubes) or to_idx >= len(self.tubes) or from_idx < 0 or to_idx < 0:
            return False

        from_tube = self.tubes[from_idx]
        to_tube = self.tubes[to_idx]

        # Can't move from empty tube
        if not from_tube:
            return False

        # Can't move to full tube
        if len(to_tube) >= self.max_capacity:
            return False

        # Can only move to empty tube or if top colors match
        if to_tube and to_tube[-1] != from_tube[-1]:
            return False

        # Don't move from a tube to itself
        if from_idx == to_idx:
            return False
            
        # Don't move a complete set (all same color) to an empty tube
        if not to_tube and len(from_tube) > 0:
            if all(color == from_tube[0] for color in from_tube):
                return False

        return True

    def make_move(self, from_idx, to_idx):
        """
        Make a move and update the state
        """
        if not self.is_valid_move(from_idx, to_idx):
            return False

        from_tube = self.tubes[from_idx]
        to_tube = self.tubes[to_idx]

        # Determine how many units to move (all of same color from top)
        color = from_tube[-1]
        count = 0

        for i in range(len(from_tube) - 1, -1, -1):
            if from_tube[i] == color:
                count += 1
            else:
                break

        # Limit by space in destination
        count = min(count, self.max_capacity - len(to_tube))

        # Move the units
        for _ in range(count):
            to_tube.append(from_tube.pop())

        self.moves.append((from_idx, to_idx))
        return True

    def solve_recursive(self, depth=0, visited=None):
        """
        Recursive approach to solving the puzzle, similar to implemented_sort.py
        """
        if visited is None:
            visited = set()
            
        # Check if we've reached the maximum recursion depth
        if depth > self.max_depth:
            return False
            
        # Check if the puzzle is already solved
        if self.is_solved():
            self.solution_found = True
            return True
            
        # Convert current state to a hashable format for visited set
        current_state = tuple(tuple(tube) for tube in self.tubes)
        if current_state in visited:
            return False
            
        visited.add(current_state)
        
        # Try all possible moves
        for from_idx in range(len(self.tubes)):
            for to_idx in range(len(self.tubes)):
                if from_idx == to_idx:
                    continue
                    
                if not self.is_valid_move(from_idx, to_idx):
                    continue
                    
                # Make a copy of the current state
                tubes_backup = [tube.copy() for tube in self.tubes]
                moves_backup = self.moves.copy()
                
                # Try this move
                self.make_move(from_idx, to_idx)
                
                # Recursively try to solve from this new state
                if self.solve_recursive(depth + 1, visited):
                    self.solution_moves.append((from_idx, to_idx))
                    return True
                    
                # If this path doesn't lead to a solution, backtrack
                self.tubes = tubes_backup
                self.moves = moves_backup
                
        return False

    def solve(self):
        """
        Find a solution using the recursive approach
        """
        import time
        start_time = time.time()
        
        print("Solving puzzle...")
        
        # Reset solution state
        self.solution_found = False
        self.solution_moves = []
        
        # Start recursive solving
        result = self.solve_recursive()
        
        if result:
            end_time = time.time()
            print(f"Solution found in {end_time - start_time:.2f} seconds!")
            
            # Reverse the solution moves since we built it backwards
            self.solution_moves.reverse()
            return self.solution_moves
        else:
            print(f"No solution found after {time.time() - start_time:.2f} seconds!")
            
            # Debug information
            print("\nDebug information:")
            print("Current tube state:")
            for i, tube in enumerate(self.tubes):
                print(f"Tube {i + 1}: {tube}")
                
            return None


def main():
    print("===== Test Tube Sorting Puzzle Solver =====")
    print("This program will solve your test tube sorting puzzle")
    print("You'll need to provide the tube positions and contents manually")

    solver = TestTubeSolver()

    # Step 1: Get tube positions
    if not solver.get_tube_positions():
        print("Failed to get tube positions.")
        return

    # Step 2: Get tube contents
    if not solver.get_tube_contents():
        print("Failed to get tube contents.")
        return

    # Step 3: Solve the puzzle
    puzzle_solver = TestTubePuzzleSolver(solver.tubes)

    # Check if already solved
    if puzzle_solver.is_solved():
        print("Puzzle is already solved!")
        return

    # Solve
    solution = puzzle_solver.solve()

    if not solution:
        print("Could not find a solution. Please check the tube contents.")

        # Debug information
        print("\nDebug information:")
        print("Current tube state:")
        for i, tube in enumerate(solver.tubes):
            print(f"Tube {i + 1}: {tube}")

        print("\nColor counts:")
        all_colors = []
        for tube in solver.tubes:
            all_colors.extend(tube)

        color_counts = {}
        for color in all_colors:
            if color in color_counts:
                color_counts[color] += 1
            else:
                color_counts[color] = 1

        for color, count in color_counts.items():
            print(f"{color}: {count}")

        # Check if the puzzle is solvable
        print("\nChecking if puzzle is solvable:")
        is_solvable = True
        
        # Check 1: Each color should appear exactly max_capacity times or be a multiple of max_capacity
        for color, count in color_counts.items():
            if count % puzzle_solver.max_capacity != 0:
                print(f"Problem: Color '{color}' appears {count} times, which is not a multiple of {puzzle_solver.max_capacity}")
                is_solvable = False
        
        # Check 2: We need enough empty tubes for temporary storage
        filled_tubes = sum(1 for tube in solver.tubes if tube)
        empty_tubes = len(solver.tubes) - filled_tubes
        min_empty_needed = 1  # Usually need at least 1 empty tube
        
        if empty_tubes < min_empty_needed:
            print(f"Warning: Only {empty_tubes} empty tubes. Most puzzles need at least {min_empty_needed} empty tubes.")
            is_solvable = False
        
        if is_solvable:
            print("The puzzle appears to be solvable based on color counts.")
            print("Try increasing the max_depth parameter in the TestTubePuzzleSolver class.")
        else:
            print("The puzzle may not be solvable with the current configuration.")

        return

    # Step 4: Execute solution
    print(f"\nFound solution with {len(solution)} moves.")
    print("Ready to execute the solution.")
    start = input("Press Enter to start solving or type 'show' to just see the moves: ")

    if start.lower() == 'show':
        # Just show the moves without executing
        for i, (from_tube, to_tube) in enumerate(solution):
            print(f"Move {i + 1}: Tube {from_tube + 1} → Tube {to_tube + 1}")
    else:
        # Execute the moves
        print("Executing solution...")
        
        # Ask user for animation delay
        try:
            custom_delay = float(input("Enter animation delay in seconds (default is 1.5): "))
            if custom_delay > 0:
                solver.animation_delay = custom_delay
        except ValueError:
            print("Using default animation delay.")
        
        print(f"Using animation delay of {solver.animation_delay} seconds.")
        
        for i, (from_tube, to_tube) in enumerate(solution):
            print(f"Move {i + 1}/{len(solution)}: Tube {from_tube + 1} → Tube {to_tube + 1}")

            if not solver.execute_move(from_tube, to_tube):
                print("Failed to execute move.")
                retry = input("Press Enter to retry or type 'skip' to continue: ")
                if retry.lower() != 'skip':
                    i -= 1  # Retry this move

            # Wait between moves
            time.sleep(1.0)  # Increased from 0.5

        print("Solution executed!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram stopped by user.")
    except Exception as e:
        print(f"Error occurred: {e}")