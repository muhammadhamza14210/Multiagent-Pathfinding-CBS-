import numpy as np
from copy import deepcopy
import random

class PuzzleState:
    def __init__(self, puzzle):
        if len(puzzle) != 3 or any(len(row) != 3 for row in puzzle):
            raise ValueError("Invalid puzzle. Must be a 3x3 grid.")

        self.puzzle = np.array(puzzle)
        self.blank_position = tuple(np.argwhere(self.puzzle == 0)[0])

    def __eq__(self, other):
        return np.array_equal(self.puzzle, other.puzzle)

    def __hash__(self):
        return hash(tuple(map(tuple, self.puzzle)))

    def __str__(self):
        return str(self.puzzle)

def h_manhattan(state, goal_state, memo):
    distance = 0
    for i in range(3):
        for j in range(3):
            if state.puzzle[i, j] != 0:
                goal_position = np.argwhere(goal_state.puzzle == state.puzzle[i, j])
                if goal_position.size > 0:
                    goal_position = goal_position[0]
                    distance += abs(i - goal_position[0]) + abs(j - goal_position[1])
    return distance

def successors(state):
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Up, Down, Left, Right
    for direction in directions:
        new_position = state.blank_position + np.array(direction)
        if 0 <= new_position[0] < 3 and 0 <= new_position[1] < 3:
            new_state = PuzzleState(state.puzzle.copy())
            new_state.puzzle[state.blank_position[0], state.blank_position[1]] = new_state.puzzle[new_position[0], new_position[1]]
            new_state.puzzle[new_position[0], new_position[1]] = 0
            new_state.blank_position = tuple(new_position)
            moves.append(new_state)
    return moves

def is_solvable(puzzle):
    inversion_count = 0
    puzzle_flat = puzzle.flatten()
    for i in range(len(puzzle_flat)):
        for j in range(i + 1, len(puzzle_flat)):
            if puzzle_flat[i] and puzzle_flat[j] and puzzle_flat[i] > puzzle_flat[j]:
                inversion_count += 1
    return inversion_count % 2 == 0

def generate_random_puzzle():
    numbers = random.sample(range(1, 9), 8) + [0]
    random.shuffle(numbers)
    random_puzzle = [numbers[i:i + 3] for i in range(0, len(numbers), 3)]
    return random_puzzle

def user_input_puzzle():
    print("Enter the initial puzzle configuration (3x3 grid, use 0 for the empty space):")
    puzzle = []
    for _ in range(3):
        row = [int(x) for x in input().split()]
        if len(row) != 3:
            print("Invalid input. Please enter exactly 3 numbers for each row.")
            return None
        puzzle.append(row)
    return puzzle

def print_puzzle(puzzle):
    for row in puzzle:
        print(" ".join(map(str, row)))

def ida_star(initial_state, goal_state, heuristic, cost_limit):
    def search(state, g, f_limit, path, memo):
        h = heuristic(state, goal_state, memo)
        f = g + h

        if f > f_limit:
            return f, path

        if state == goal_state:
            return "FOUND", path

        next_f_limit = float('inf')
        successors_list = successors(state)
        for successor in successors_list:
            next_cost = g + 1
            result, new_path = search(successor, next_cost, f_limit, path + [successor], memo)
            if result == "FOUND":
                return "FOUND", new_path
            if result < next_f_limit:
                next_f_limit = result

        return next_f_limit, path

    if not is_solvable(initial_state.puzzle) or not is_solvable(goal_state.puzzle):
        return "Unsolvable puzzle.", None

    f_limit = heuristic(initial_state, goal_state, {})
    path = [initial_state]
    while True:
        result, new_path = search(initial_state, 0, f_limit, path, {})
        if result == "FOUND":
            return "Solution found!", new_path
        if result == float('inf'):
            return "No solution exists.", None
        f_limit = result

def main():
    print("Welcome to the 8-Puzzle Solver!")
    print("Choose an option:")
    print("1. Generate a random initial puzzle and goal state.")
    print("2. Input your own initial puzzle and generate a random goal state.")
    choice = input("Enter 1 or 2: ")

    if choice == "1":
        initial_puzzle = generate_random_puzzle()
        goal_puzzle = generate_random_puzzle()
    elif choice == "2":
        initial_puzzle = user_input_puzzle()
        if initial_puzzle is None:
            print("Exiting due to invalid input.")
            return
        goal_puzzle = generate_random_puzzle()
    else:
        print("Invalid choice. Exiting.")
        return

    initial_state = PuzzleState(initial_puzzle)
    goal_state = PuzzleState(goal_puzzle)

    print("\nInitial Puzzle:")
    print_puzzle(initial_puzzle)
    print("\nGoal Puzzle:")
    print_puzzle(goal_puzzle)

    # Solve the puzzle
    solution_status, solution_path = ida_star(initial_state, goal_state, h_manhattan, cost_limit=30)

    print("\nSolution:")
    print(solution_status)
    if solution_path:
        for step in solution_path:
            print_puzzle(step.puzzle)

if __name__ == "__main__":
    main()
