# -------------------------------------------------------------------------------------
# The goal I had in mind for this code was to minimise the need for brute search.
# For that, I use two main algorithms...
#    1) possibility_eliminator() for solving almost all determinate puzzles quickly,
#    2) and brute_force_insert() and brute_force_backtrack() for indeterminate puzzles
#    where you have to try values to see if they work.
# -------------------------------------------------------------------------------------
from SudokuFunctions import *
from SudokuBoards import *
import time

# TODO: Exception handling.
# TODO: Raise exceptions, 'finally' end with an animation of
#       the window turning red and flickering until it's dead.
# TODO: Do green tile animation for "RUN" button as well

manual_inserts = []  # Saving snapshots before brute force inserts, so can backtrack to them if need.
board_snapshots = []
inserts = 0  # Checks how many manual inserts the solver has to make before a solution is found.
backtracks = 0  # Checks how many backtracks were needed.


def solve_board(working_board, output_board=None, single_cycle=False, cycles=0):
    # These variables need to be global because I'm using solve_board() in a loop from the GUI.
    global inserts, backtracks

    while single_cycle is False or cycles < 1:
        # The following function searches through the board and, if no conflict is found,
        # returns a list of all the cells it could not find definite solutions for,
        # in the form of [(cell_value0, cell_index0), (cell_value1, cell_index1), ...]
        # If a conflict is found, it returns "conflicts".
        unresolved_cells = possibility_eliminator(working_board, output_board)

        if len(unresolved_cells) == 0:  # If there are 0 unresolved cells...

            # Telling the world
            print("\n    ___Found solution:___")
            print_board(working_board)
            print("\nNumber of manual inserts needed:", str(inserts) + ".")
            print("Number of backtracks needed:", str(backtracks) + ".")
            inserts = 0  # Resets count in case user wants to solve another puzzle.
            backtracks = 0
            return True

        elif unresolved_cells == "conflicts":  # If there were any conflicts found by possibility_eliminator()...
            print("\n    ___Found conflict:___")
            print_board(working_board)
            print("\nConflict found. Backtracking...")
            print("Brute force insertion history (old_value, index, inserted_value):\n    ", manual_inserts)
            backtracks += 1

            working_board = brute_force_backtrack(working_board, manual_inserts, board_snapshots)

        else:  # If there are any unresolved cells, and no conflicts have been found...
            print("\n    __Incomplete solution:__")
            print_board(working_board)
            print("\nBoard was not solved by possibility_eliminator algorithm." +
                  "\nProceeding with manually inserted value, and backtracking if that does not work.")
            inserts += 1

            # The following algorithm only searches through unresolved digits in unresolved cells,
            # so there's a greatly reduced need for brute force compared to a simple brute force search.
            working_board = brute_force_insert(working_board, unresolved_cells, manual_inserts, board_snapshots)
        cycles += 1


if __name__ == '__main__':
    board_choice = indeterminate_board_0  # Other options: determinate_board, maximum_entropy_board
    print("Solving board:", board_choice[0])
    print_board(board_choice[1])
    start_execution = time.time()
    solve_board(board_choice[1])
    end_execution = time.time()
    print("Execution time:", end_execution - start_execution)