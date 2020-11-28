# -------------------------------------------------------------------------------------
# The goal I had in mind for this code was to minimise the need for brute force search.
# For that, I use two main algorithms:
#    1) "possibility_eliminator()" for solving almost all determinate puzzles quickly,
#    2) and brute search for indeterminate puzzles.
#
# I made this while learning Python from scratch, which should be evident from my utterly
# abhorrent code. I haven't had time to tidy it up yet, and due to Yule vacation
# approaching, I didn't have time to code the last bits proper either. But it works!
#
# Timo Brønseth, December 2019
# -------------------------------------------------------------------------------------
from math import floor
from random import randint, choice, sample

from tkinter.scrolledtext import ScrolledText
from tkinter import Tk, Button, Canvas, Entry, Label
from tkinter import RAISED, W, E, N, NW, WORD, StringVar, END

# DONE: Make it be 9x9.
# DONE: Center the digits in the cells.
# DONE: Make borders around 9-boxes.
# DONE: Rename "labels".
# DONE: Remove superfluous buttons.
# DONE: Fix the "SOLVE" button.
# DONE: Fix user insertion during non-elimination phase of "flip".
# DONE: Fix bug where detection of unsolvable puzzle fails after refresh.
# DONE: Fix "unsolvable"-bug with solve_board after user edits cells.
# DONE: Fix backtracking
# DONE: Fix colouring
# DONE: Implement "Help" button to display text in console.
# DONE: Write a "generate_puzzle" function.
# DONE: BUG - Sometimes solver runs into "EMPTY CELL POSSIBLES"
#       where an unresolved cell has an empty set of possible digits.
#       (See image EMPTY CELL POSSIBLES on desktop)
# DONE: BUG - If solver finds a conflict on the iteration that fills the board
#       completely, it interprets the board as solved, rather than backtracking
#       find a solution without conflict. (easy)
# TODO: Allow user to change animation speed via the GUI.
# TODO: Allow user to return to last generated puzzle at any time.
# TODO: Allow user to SAVE board.
# TODO: CLEAN UP YOUR UTTERLY ABHORRENT CODE.

# GLOBAL_VARIABLES
# Saving snapshots before brute force inserts, so can backtrack to them if need.
manual_inserts = []
board_snapshots = []
unresolved_cells = []

# Checks how many manual inserts and backtracks the solver has to make before a solution is found.
insert_count = 0
backtrack_count = 0
iteration_count = 0

# Flip algorithm used each iteration: brute force search and possibility_eliminator().
flip = True


# Run this when user clicks "ITERATE"
def iterate_algorithm():
    global flip, unresolved_cells, insert_count, backtrack_count, iteration_count, output_board

    # Replace board with 81 0's if board is empty.
    if len(working_board) == 0:
        working_board.extend([0 for i in range(81)])

    # Check for integers entered into cells by user.
    check_user_input()

    # Check if board is already full.
    # if len([i for i in working_board if isinstance(i, int) and i > 0]) == 81:
    #     print("\nCould not iterate. Board already solved.")
    #     say("\nCould not iterate. Board already solved.")
    #     return True

    # Prepare for iteration
    iteration_count += 1
    recolour_all("white")  # Reset all cells to white, just in case they have colour.
    board_snapshot = working_board.copy()  # To compare with after, for colouring changed cells.
    print("\nIteration " + str(iteration_count) + ".")
    update_colour = None

    # Fit the lines properly into the textbox.
    print_iteration_line(iteration_count)

    if flip:
        # The following function searches through the board and, if no conflict is found,
        # returns a list of all the cells it could not find definite solutions for,
        # in the form of [(cell_value0, cell_index0), (cell_value1, cell_index1), ...]
        # If conflicts are found, it returns "conflicts".

        # If this returns an empty set, we know the puzzle has been solved.
        unresolved_cells = possibility_eliminator(working_board, output_board)

        # Tell the world
        say("\nUpdating possibility map.")

        # Flip the flip: True = False, and False = True
        flip = not flip

    elif not flip:
        # If there were any conflicts found by possibility_eliminator()...
        if unresolved_cells == "conflicts":

            print("\n    ___Found conflict:___")
            print_board(working_board)
            print("\nConflict found. Backtracking..." +
                  "\nBrute force insertion history (old_value, index, inserted_value):\n    ",
                  manual_inserts)
            say("\nCONFLICTS FOUND.")
            say("Backtracking..." +
                "\nBrute force insertion history\n" +
                "\nINSERT\tINDEX\tINITIAL POSSIBILITIES",
                'italic')
            for insert in manual_inserts:
                say(str(insert[2]) + "\t" + str(insert[1]) + "\t" + str(insert[0]))
                # say(str(list(reversed(insert))))
            backtrack_count += 1

            brute_force_backtrack(working_board, manual_inserts, board_snapshots)

            # Flip the flip: True = False, and False = True
            flip = not flip

        # If the board is unsolvable...
        elif unresolved_cells == "unsolvable":

            print("\nUNSOLVABLE PUZZLE.\n" +
                  "Please feed me a proper puzzle next time.")
            say("\nUNSOLVABLE PUZZLE.")
            say("\nPlease feed me a proper puzzle next time.", 'italic')

            recolour_all("red")
            return True

        # If there are any unresolved cells, and no conflicts have been found...
        else:
            update_colour = "yellow"

            print("\n    __Incomplete solution:__")
            print_board(working_board)
            print("\nBoard was not solved by possibility_eliminator algorithm." +
                  "\nProceeding with manually inserted value, and backtracking if that does not work.")
            say("\nNOT SOLVED YET.")
            say("Board was not solved by the Possibility Eliminator algorithm." +
                "\nProceeding with manually inserted value, and backtracking if that does not work.",
                'italic')
            insert_count += 1

            # The following algorithm only searches through unresolved digits in unresolved cells,
            # so there's a greatly reduced need for brute force compared to a simple brute force search.
            brute_force_insert(working_board, unresolved_cells, manual_inserts, board_snapshots, hidden=False)

            # Flip the flip: True = False, and False = True
            flip = not flip

    # Formatting
    # format_board(working_board)  # TODO: Make format_board() work here. Ugly code.
    updated_board = working_board.copy()
    updated_board = [value if value in [1, 2, 3, 4, 5, 6, 7, 8, 9]
                     else '' for i, value in enumerate(updated_board)]
    update_output_board(updated_board, output_board)

    # Colour all the cells that have been decided since last iteration.
    colour_updated_cells(updated_board, board_snapshot, update_colour)

    # If there are 0 unresolved cells...
    if len(unresolved_cells) == 0:
        # Telling the world
        print("\n    ___Found solution:___")
        print_board(working_board)
        print("\nNumber of manual inserts needed:", str(insert_count) + "." +
              "\nNumber of backtracks needed:", str(backtrack_count) + ".")
        say("\nSOLUTION FOUND.")
        say("\nNumber of manual inserts needed: " + str(insert_count) + "." +
            "\nNumber of backtracks needed: " + str(backtrack_count) + ".",
            'italic')
        say("\n----------------------------------------")

        # Reset global variables so that user can solve new puzzles.
        reset_globals()

        return True


# Iterates the algorithm in a loop until puzzle is solved or declared unsolvable.
def solve_puzzle(num_givens=29, fast=False):
    solved = False
    if fast:
        while not solved:
            solved = quick_iterate_algorithm(num_givens)  # Returns True if solved or proved unsolvable.
    else:
        while not solved:
            # TODO: Enable user to change speed of animation via the GUI.
            window.after(0)  # Increase this to make animation slower.
            window.update()
            solved = iterate_algorithm()  # Returns True if solved or proved unsolvable.


def quick_iterate_algorithm(num_givens):
    global flip, unresolved_cells, output_board

    # Check if board is already full.
    if len([i for i in working_board if isinstance(i, int) and i > 0]) == 81:
        return True

    if flip:
        # The following function searches through the board and, if no conflict is found,
        # returns a list of all the cells it could not find definite solutions for,
        # in the form of [(cell_value0, cell_index0), (cell_value1, cell_index1), ...]
        # If a conflict is found, it returns "conflicts".

        unresolved_cells = possibility_eliminator(working_board, output_board)

        # Flip the flip: True = False, and False = True
        flip = not flip

        # If there are 0 unresolved cells...
        if len(unresolved_cells) == 0:
            # Reset global variables so that user can solve new puzzles.
            reset_globals()

    elif not flip:
        # If there were any conflicts found by possibility_eliminator()...
        if unresolved_cells == "conflicts":
            brute_force_backtrack(working_board, manual_inserts, board_snapshots)

            # Flip the flip: True = False, and False = True
            flip = not flip

        # If the board is unsolvable...
        elif unresolved_cells == "unsolvable":
            generate_puzzle(num_givens)

        # If there are any unresolved cells, and no conflicts have been found...
        else:

            # The following algorithm only searches through unresolved digits in unresolved cells,
            # so there's a greatly reduced need for brute force compared to a simple brute force search.
            brute_force_insert(working_board, unresolved_cells, manual_inserts, board_snapshots, hidden=True)

            # Flip the flip: True = False, and False = True
            flip = not flip


def check_board():
    # Replace board with 81 0's if board is empty.
    if len(working_board) == 0:
        working_board.extend([0 for i in range(81)])

    # Check for integers entered into cells by user.
    check_user_input()

    conflicts = False

    # Run the loop for every row.
    for i in range(0, 9):

        # Fetches the row to be analysed.
        row_values = slice_row(working_board, i)

        # Analyses each cell in the row, and writes in
        # a set with all the digits that do not conflict
        # with other cells in the row. Returns the duplicate
        # digit if any are found, otherwise None.
        conflict = compare_group(row_values)

        # Colour duplicates red, if found any.
        if isinstance(conflict, int) or conflict == set():
            conflicts = True
            cell_indices = [j + 9 * i for j in range(9)]  # Indices of cells on current row.
            colour_conflicts(conflict, cell_indices)

    # And then for every column.
    for i in range(0, 9):
        column_values = slice_column(working_board, i)

        conflict = compare_group(column_values)

        if isinstance(conflict, int) or conflict == set():
            conflicts = True
            cell_indices = list(range(i, 81, 9))  # Indices of cells on current column.
            colour_conflicts(conflict, cell_indices)

    # Loop for every square group.
    for i in range(0, 9):
        square = slice_square(working_board, i)
        # This returns a tuple with: (set of cell values, set of cell indices).

        conflict = compare_group(square[0])

        if isinstance(conflict, int) or conflict == set():
            conflicts = True
            cell_indices = square[1]  # Indices of cells on current square.
            colour_conflicts(conflict, cell_indices)

    say("\nChecking board...")
    window.update()
    window.after(500)

    if conflicts:
        # Wait for one second before refreshing screen again.
        say("\nConflicts found.")
        recolour_all("white")

    else:
        say("\nNo conflicts found.")


# -------------------------------------------------------------------------------------
# Sudoku Functions
# -------------------------------------------------------------------------------------

# What needs to be filled into all horizontal lines, vertical lines and squares.
solution_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}

top_left = [0, 1, 2, 9, 10, 11, 18, 19, 20]  # Indices of the 9 top left cells.
top = [3, 4, 5, 12, 13, 14, 21, 22, 23]
top_right = [6, 7, 8, 15, 16, 17, 24, 25, 26]
left = [27, 28, 29, 36, 37, 38, 45, 46, 47]
middle = [30, 31, 32, 39, 40, 41, 48, 49, 50]
right = [33, 34, 35, 42, 43, 44, 51, 52, 53]
bottom_left = [54, 55, 56, 63, 64, 65, 72, 73, 74]
bottom = [57, 58, 59, 66, 67, 68, 75, 76, 77]
bottom_right = [60, 61, 62, 69, 70, 71, 78, 79, 80]


# Colour all the cells that have been decided since last iteration.
def colour_updated_cells(updated_board, snapshot_board, update_colour):
    for i, value in enumerate(updated_board):
        if updated_board[i] != snapshot_board[i] and isinstance(updated_board[i], int):
            recolour(cells[i], update_colour)
    return


def reset_globals():
    global insert_count, backtrack_count, iteration_count, manual_inserts, board_snapshots, unresolved_cells, flip
    insert_count, backtrack_count, iteration_count = 0, 0, 0
    manual_inserts.clear()
    board_snapshots.clear()
    list(unresolved_cells).clear()
    flip = True


# Prints the board to console (not to the window).
def print_board(board):
    board = ['•' if n == 0 else n for n in board]
    for i in range(0, len(board), 9):
        print("\t" + str(board[0 + i]) +
              "\t" + str(board[1 + i]) +
              "\t" + str(board[2 + i]) +
              "\t" + str(board[3 + i]) +
              "\t" + str(board[4 + i]) +
              "\t" + str(board[5 + i]))


def slice_row(board, row_index):
    row_values = board[0 + 9 * row_index:9 + 9 * row_index]
    return row_values


def place_row(board, index, row):
    for i, value in enumerate(row):
        board[i + 9 * index] = value


def slice_column(board, index):
    column = board[index::9]
    return column


def place_column(board, index, column):
    for i, value in enumerate(column):
        board[index + i * 9] = value


def slice_square(board, index):
    if index == 0:  # This is the first square, i.e. the top left corner.
        square = [n for i, n in enumerate(board) if i in set(top_left)]
        return square, top_left  # Returns a tuple
    elif index == 1:
        square = [n for i, n in enumerate(board) if i in set(top)]
        return square, top
    elif index == 2:
        square = [n for i, n in enumerate(board) if i in set(top_right)]
        return square, top_right
    elif index == 3:
        square = [n for i, n in enumerate(board) if i in set(left)]
        return square, left
    elif index == 4:
        square = [n for i, n in enumerate(board) if i in set(middle)]
        return square, middle
    elif index == 5:
        square = [n for i, n in enumerate(board) if i in set(right)]
        return square, right
    elif index == 6:
        square = [n for i, n in enumerate(board) if i in set(bottom_left)]
        return square, bottom_left
    elif index == 7:
        square = [n for i, n in enumerate(board) if i in set(bottom)]
        return square, bottom
    elif index == 8:
        square = [n for i, n in enumerate(board) if i in set(bottom_right)]
        return square, bottom_right


def place_square(board, square_values, square_indices):
    for i, value in enumerate(square_values):
        board[square_indices[i]] = value


def find_duplicate(list_):
    set_compare = set()
    list_ = [i for i in list_ if isinstance(i, int) and i > 0]  # Only search for digit duplicates.

    for i in list_:
        if i in set_compare:
            return i
        else:
            set_compare.add(i)
    return None


# Colours the duplicates or the empty sets red.
def colour_conflicts(conflict, cell_indices):
    for i, cell_value in enumerate([working_board[i] for i in cell_indices]):
        if isinstance(cell_value, int) and cell_value == conflict:
            recolour(cells[cell_indices[i]], "red")
        if cell_value == set():
            recolour(cells[cell_indices[i]], "red")


# Find any unresolved cells and store them in a list with both cell values and cell indices.
def find_unresolved(board):
    unresolved_cells = [(n, index) for index, n in enumerate(board) if type(n) == set]
    return unresolved_cells


# This goes through the list of all cells given to it,
# and returns the list with fewest remaining possible digits.
# Input must be a list of the form [(cell_value, cell_index), ...]
def find_cell_with_fewest_possibles(cells):
    for cell in cells:
        if cell == cells[0] or len(cell[0]) < len(cell_fewest[0]):
            cell_fewest = cell
    return cell_fewest


# output_board takes all the values from working_board,
# which will immediately be displayed in the tkinter window.
def update_output_board(working_board, output_board):
    for i, cell in enumerate(working_board):
        output_board[i].set(working_board[i])
    # for i, cell in enumerate(working_board):
    #     if len(cells[i].get() > 0):
    #         output_board[i].set(int(4))
    return working_board, output_board


def compare_group(group):  # A "group" is a collection of 6 items like a row, column or a square.
    definite_digits_group = [i for i in group if type(i) == int]  # Digits that are already in the group.
    possible_digits_group = solution_set - set(definite_digits_group)  # Digits that still need to be placed.

    # If duplicate is found, return it
    duplicate = find_duplicate(definite_digits_group)
    if duplicate is not None:
        return duplicate

    # If a cell contains an empty set, it means there are no possible
    # values for it, hence need to backtrack or declare puzzle unsolvable
    for value in group:
        if value == set():
            return set()

    for index, cell_value in enumerate(group):
        if isinstance(cell_value, int) and cell_value > 0:  # Skip analysis if cell is already set with an integer.
            pass

        else:
            if len(possible_digits_group) == 1:  # If there is only one possible digit in the group...
                group[index] = min(possible_digits_group)  # Insert that digit into the cell.
                #  "group[index]" points to the cell we're working with from the group.
                break
            elif isinstance(cell_value, set):  # If the value in the cell is a set...
                # Eliminate possibles in the cell if they conflict with present digits in the group.
                possible_digits_cell = cell_value - set(definite_digits_group)
                if len(possible_digits_cell) == 1:  # If there is now only one possible digit left in the cell...
                    group[index] = min(possible_digits_cell)  # Insert that digit into the cell.
                else:
                    group[index] = possible_digits_cell
            else:
                #  If the cell does not contain an integer, or a set of integers, then it's empty
                #  and needs to be updated with a set of all the possibles in the group.
                group[index] = possible_digits_group


# This is the main algorithm that can solve most determinate boards without a hitch.
# But it cannot deal with indeterminate boards (boards with multiple possible solutions),
# and there _may_ be some determinate boards it cannot solve. I don't really know,
# because I haven't proved this algorithm to be complete (and I don't even know how to
# do that).
def possibility_eliminator(working_board, output_board, slow_mode=True):
    conflicts = False

    while True:
        old_board = tuple(working_board)  # TODO: Make copy()
        # I need to check if the board has changed at all since the last iteration of this while loop,
        # so I will compare old_board to the new board. But old_board needs to be stored as a tuple,
        # otherwise the function calls below would just simultaneously edit both.
        #     When you assign one list pointer to another list pointer (e.g. "list1 = list2),
        # they point to the same memory locations; but when you assign a tuple pointer to another
        # tuple pointer (e.g. "tuple1 = tuple2"), they point to different memory locations.

        for i in range(0, 9):  # Run the loop for every row.

            # Fetches the row to be analysed.
            row_values = slice_row(working_board, i)

            # Analyses each cell in the row, and writes in
            # a set with all the digits that do not conflict
            # with other cells in the row. Returns the duplicate
            # digit if any are found, or an empty set if one is found,
            # otherwise it returns None.
            conflict = compare_group(row_values)

            # Inserts the row back into the board.
            # Each cell in the row should now contain either
            # a digit, or a set with all the possible digits.
            place_row(working_board, i, row_values)

            # Colour conflicts red, if found any
            if isinstance(conflict, int) or conflict == set():
                conflicts = True
                cell_indices = [j + 9 * i for j in range(9)]  # Indices of cells on current row.
                colour_conflicts(conflict, cell_indices)

        for i in range(0, 9):  # And then for every column.
            column_values = slice_column(working_board, i)

            conflict = compare_group(column_values)

            place_column(working_board, i, column_values)

            if isinstance(conflict, int):
                conflicts = True
                cell_indices = list(range(i, 81, 9))  # Indices of cells on current column.
                colour_conflicts(conflict, cell_indices)

        for i in range(0, 9):  # Loop for every square group.
            square = slice_square(working_board, i)
            # This returns a tuple with: (set of cell values, set of cell indices).

            conflict = compare_group(square[0])

            place_square(working_board, square[0], square[1])

            if isinstance(conflict, int):
                conflicts = True
                cell_indices = square[1]  # Indices of cells on current square.
                colour_conflicts(conflict, cell_indices)

        #  If conflicts have been found, then return as appropriate.
        if conflicts and len(manual_inserts) == 0:
            print("UNSOLVABLE!")
            return "unsolvable"
        elif conflicts:
            return "conflicts"

        # Colour updated cells.
        for i, value in enumerate(working_board):
            if working_board[i] != old_board[i] and isinstance(working_board[i], int):
                recolour(cells[i], "green")

        # If the board has not changed since the last iteration,
        # then either it is solved or the loop cannot solve it.
        if tuple(working_board) == old_board:
            unresolved_cells = find_unresolved(working_board)
            return unresolved_cells


def brute_force_insert(board, unresolved_cells, manual_inserts, board_snapshots, hidden):
    cell_fewest_possibles = find_cell_with_fewest_possibles(unresolved_cells)  # Stored as (cell_value, cell_index)
    possibles = cell_fewest_possibles[0]  # Tuple with all the possible digits in the cell.
    cell_index = cell_fewest_possibles[1]
    insert = min(possibles)  # The smallest digit out of the ones possible.

    # Storing information about which inserted digits have been tried,
    # so that we can remove them from the list of digits left to try.
    manual_inserts.append([possibles, cell_index, insert])

    # Storing a snapshot of the board before the brute force insert,
    # so that I can safely restore it in case the insert fails.
    board_snapshots.append(board.copy())

    # Tell the world.
    if not hidden:
        print(
            "\nSetting cell at index (" + str(cell_index % 9) + ", " + str(floor(cell_index / 9)) + ") to " + str(insert) +
            ", from possible digits " + str(possibles) + ".")
        say("\nSetting cell at index (" + str(cell_index % 9) + ", " + str(floor(cell_index / 9)) + ") to " + str(insert) +
            ", from possible digits " + str(possibles) + ".", 'italic')

    # Insert the new digit into the board.
    board[cell_index] = insert

    return board


def brute_force_backtrack(board, manual_inserts, board_snapshots):
    # Can't do a simple reassignment of the board from the snapshot,
    # because then it would replace the StringVar() types on the board.
    # It's important that the board has digits of the StringVar() type,
    # because then they will always be updated in the tkinter window.mainloop().
    for i in range(0, len(board)):
        board[i] = board_snapshots[-1][i]
    # board = board_snapshots[-1]  # This will fail to update on the tkinter window.mainloop().

    # Gets the possible digits for the most recently edited cell,
    # and the digit that was tried (and failed) in the brute force search.
    possibles, cell_index, failed_insert = manual_inserts[-1]
    updated_possibles = possibles - {failed_insert}

    # Update the cell with the new possibles, displacing the failed insert.
    board[cell_index] = updated_possibles
    manual_inserts.pop(-1)  # Remove the most recent addition to the brute force search history.
    board_snapshots.pop(-1)  # Remove the most recent snapshot, so that we don't return to it again.
    return board


# -------------------------------------------------------------------------------------
# Generate puzzles
# -------------------------------------------------------------------------------------
def generate_puzzle(num_givens: int):
    global working_board, output_board, cells

    # TODO: Hide the board from user while it is generating a puzzle.

    # Check if num_givens falls inside valid range, and raise ValueError if not
    # valid_num_givens = range(8, 81)
    # if num_givens not in valid_num_givens:
    #     raise ValueError("num_givens was outside the range of valid_num_givens")

    # Clear board
    clear_board()

    # Insert digits 1 to 9 randomly across the board
    digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    for i in range(0, 9):

        # Pick a random digit between 0 and 10, without replacement
        digit = choice(digits)
        digits.remove(digit)

        # Pick a random cell on the board
        # (One random cell for each row, to ensure
        # selections don't overlap.)
        cell = randint(0, 8)+9*i

        # Insert digit into that cell
        working_board[cell] = digit

    # complete the board quickly, without updating GUI
    solve_puzzle(num_givens, fast=True)

    # # remove 81-num_givens number of digits in random cells
    indices = list(range(0, 81))
    for i in range(0, 81-num_givens):

        # Pick a random cell from the set of all 81 indices,
        # and then remove the cell reference from the set.
        # Set the chosen cell to empty. Repeat 81-num_givens times.
        digit = choice(indices)
        indices.remove(digit)
        working_board[digit] = 0

    # Formatting
    updated_board = working_board.copy()
    updated_board = [value if value in [1, 2, 3, 4, 5, 6, 7, 8, 9]
                     else '' for i, value in enumerate(updated_board)]
    update_output_board(updated_board, output_board)

    # Announce new puzzle
    say("Puzzle generated with {} givens.".format(num_givens))

    return


# -------------------------------------------------------------------------------------
# Tkinter GUI
# -------------------------------------------------------------------------------------


# Global variables
working_board = []  # This one is used by the algorithms.
output_board = []  # When cells on this board are changed, it immediately shows up in the tk app.
cells = []  # All the cells that need to be drawn into the tkinter window.


# Draw the Sudoku board onto the tk window.
def draw_board():
    numcells = 0  # Counter for the loop; tracks which number cell we're on (up to 81).
    grid_locations = [i + 1 for i in range(0, 12) if i % 4 != 0]  # 2, 3, 4, 6, 7, 8, ...

    # Draw all the cells in the  board.
    for y_coordinate in grid_locations:
        for x_coordinate in grid_locations:
            output_board.append(StringVar())
            # Values that go into the board need to be the unique StringVar data type.
            # Now, every time output_board[i] is changed (e.g. to a new digit),
            # it immediately updates the corresponding cell in the tkinter window.

            cells.append(Entry(window,
                               textvariable=output_board[numcells],
                               # StringVar digits need to go into 'textvariable' in order to be dynamically updatable.
                               # Later, you update them by setting 'output_board[i].set(new_value)', and then the
                               # cells on the window immediately changes.

                               font=('Courier', 31),
                               width=2,
                               bg='white',
                               borderwidth=1,
                               relief='solid',
                               justify='center')
                         )
            cells[numcells].grid(row=y_coordinate, column=x_coordinate)
            numcells += 1


# Make a board ready for being displayed on the output_board in the tkinter window.
# Cast all elements as ints, and replace zeros with invisible strings.
def format_board(board):
    board = board.copy()
    # This is to prevent problems that occur when you pass the global working_board to this
    # function. If board==working_board, then when I clear() working_board, I also clear() board,
    # which means that enumerate(board) below is also empty.

    # TODO: Check out how to do '{}'.format() method

    working_board.clear()
    working_board.extend(
        [int(value) if value in [1, 2, 3, 4, 5, 6, 7, 8, 9, '1', '2', '3', '4', '5', '6', '7', '8', '9']
         else '' for i, value in enumerate(board)])
    # Make all the zeros invisible.

    return working_board


# Recolour specific cell
def recolour(cell, colour):
    cell["bg"] = colour


# Recolour all cells to 'colour'
def recolour_all(colour):
    for cell in cells:
        recolour(cell, colour)


# Flash all cells black for 'ms' milliseconds
def flash_cells(ms):
    for cell in cells:
        window.after(0, recolour, cell, "black")
        window.after(ms, recolour, cell, "white")


# Clear the board. Runs when user clicks "CLEAR".
def clear_board():
    flash_cells(50)
    reset_globals()
    board = [0 for i in range(0, 81)]
    format_board(board)
    update_output_board(working_board, output_board)
    say("\n-------------BOARD UPDATED--------------")


# Check for integers entered into cells by user.
def check_user_input():
    global working_board

    for i, cell in enumerate(cells):
        cell_value = cell.get()

        # Exception handling
        if len(cell_value) > 0 and \
                is_int(cell_value) and \
                0 < int(cell_value) < 10:
            working_board[i] = int(cell_value)


def is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False


def print_iteration_line(count):
    if 10 > count >= 0:
        say("\n--------------Iteration " + str(count) + "---------------")
    elif 99 >= count >= 10:
        say("\n--------------Iteration " + str(count) + "--------------")
    elif 999 >= count >= 100:
        say("\n--------------Iteration " + str(count) + "-------------")


# Display text into the textbox.
def say(text, style=None):
    if style == 'italic':
        textbox.insert(END, text + '\n', 'italic')
    else:
        textbox.insert(END, text + '\n')
    textbox.see(END)  # Scrolls down if text exceeds bottom of textbox.


def textbox_bg(colour):
    textbox['bg'] = colour


def flicker_textbox(ms, colour):
    window.after(ms, textbox_bg, colour)
    window.after(ms + 50, textbox_bg, 'black')


def help_text():
    text = "Hello!\n\nNice of you to try my Sudoku solver!\n\n" + \
           "This program was written by Timo Brønseth in December 2019, " \
           "as a project for learning how to write Python (hence the bad " \
           "code!).\n\n" \
           "It currently features:\n\n" \
           " • An algorithm for solving all possible Sudoku puzzles, " \
           "using a combination of possibility elimination and brute-" \
           "force search with backtrack when necessary.\n\n" \
           "'ITERATE' goes through the solving algorithm one step at a" \
           " time, and 'SOLVE' loops over it.\n\n" \
           " • 'CHECK' searches for conflicts on the board and colours " \
           "them red.\n\n" \
           " • 'EASY PUZZLE' and the other buttons presents you with puzzles" \
           " of varying difficulty.\n\n" \
           " • You can edit the board by inserting your own digits. (Fun " \
           "tip: try to hit 'SOLVE' with an empty board and then edit " \
           "the empty cells to see if you can break the algorithm!)\n\n" \
           "GitHub link:" \
           "https://github.com/timo-bronseth/Timo-s-Eccentric-Sudoku-Solver\n\n"

    say("\n.")
    window.update()
    window.after(300)
    say(".")
    window.update()
    window.after(300)
    say(".\n")
    window.update()
    window.after(1000)
    say(text)
    window.update()


# Loading the application...
if __name__ == "__main__":
    # Tkinter app window
    window = Tk()
    window.title("Timo's Neat Little Sudoku Solver!")

    line_width = 1
    line_thickness = 5
    span = 14

    w = Canvas(window, width=0, height=0)
    w.grid(row=5, column=5, pady=line_width, padx=line_width)

    w = Canvas(window, width=0, height=0)
    w.grid(row=9, column=9, pady=line_width, padx=line_width)

    w = Canvas(window, width=0, height=0)
    w.grid(row=0, column=0, pady=line_width, padx=line_width)

    w = Canvas(window, width=0, height=0)
    w.grid(row=0, column=13, pady=line_width, padx=line_width)

    # Button to iterate the solving algorithm.
    button_iterate = Button(window,
                            width=11,
                            text="ITERATE",
                            font=("Arial black", 9),
                            borderwidth=3,
                            relief=RAISED,
                            command=iterate_algorithm)
    button_iterate.grid(row=14, column=14, pady=5, sticky=W)

    # Button to solve the board.
    button_solve = Button(window,
                          text="SOLVE",
                          width=11,
                          font=("Arial black", 9),
                          borderwidth=3,
                          relief=RAISED,
                          command=solve_puzzle)
    button_solve.grid(row=14, column=16, pady=5, sticky=W)

    # Button to display help text on console.
    button_help_text = Button(window,
                              width=11,
                              text="HELP",
                              font=("Arial black", 9),
                              borderwidth=3,
                              relief=RAISED,
                              command=help_text)
    button_help_text.grid(row=14, column=17, pady=5)

    # Button to clear the board.
    button_entry_clear = Button(window,
                                text="C\nL\nE\nA\nR",
                                width=4,
                                height=7,
                                font=("Arial black", 9),
                                borderwidth=3,
                                relief=RAISED,
                                command=clear_board)
    button_entry_clear.grid(row=10, column=0, rowspan=3, pady=5)

    # Green the AI in Czech
    button_czech = Button(window,
                          width=4,
                          height=7,
                          text="C\nZ\nE\nC\nH",
                          font=("Arial black", 9),
                          borderwidth=3,
                          relief=RAISED,
                          command=lambda: say("\nahoj světe!"))
    # 'lambda' should really be called 'make-function'.
    button_czech.grid(row=6, column=0, rowspan=3, padx=7, pady=2)

    # Check for conflicts and colour them red.
    button_check_board = Button(window,
                                width=4,
                                height=7,
                                text="C\nH\nE\nC\nK",
                                font=("Arial black", 9),
                                borderwidth=3,
                                relief=RAISED,
                                command=check_board)
    button_check_board.grid(row=2, column=0, rowspan=3, padx=7, pady=2)

    # Button for trying determinate_board
    button_easy_board = Button(window,
                               text="Easy Puzzle",
                               width=17,
                               font=("Arial black", 10),
                               borderwidth=2,
                               relief=RAISED,
                               #command=lambda: say("\nThis functionality has not been implemented yet."))
                               command=lambda: generate_puzzle(29)) # 29 givens for easy puzzle.
                                # If I just write "command=generate_puzzle(29)" here, it runs when first
                                # opening the program. If I wrap it in a lambda expression, it only runs
                                # when I click the button.
    button_easy_board.grid(row=13, column=1, columnspan=12, pady=5, sticky=W)

    # Button for trying indeterminate_board
    button_medium_board = Button(window,
                                 text="Medium Puzzle",
                                 width=17,
                                 font=("Arial black", 10),
                                 borderwidth=2,
                                 relief=RAISED,
                                 command=lambda: generate_puzzle(23))
    button_medium_board.grid(row=13, column=1, columnspan=12, pady=5)

    # Button for trying maximum_entropy_board
    button_hard_board = Button(window,
                               text="Hard Puzzle",
                               width=17,
                               font=("Arial black", 10),
                               borderwidth=2,
                               relief=RAISED,
                               command=lambda: generate_puzzle(17))
    button_hard_board.grid(row=13, column=1, columnspan=12, pady=5, sticky=E)

    # Infobox
    info = "These buttons generate random boards with 17, 23 or 29 givens.\n" + \
           "Timo Brønseth, December 2019."
    infobox = Label(window,
                    text=info,
                    font='Courier 10 italic')
    infobox.grid(row=14, column=2, columnspan=13, sticky=NW)

    #  Console
    textbox = ScrolledText(window,
                           width=40,
                           height=30,
                           wrap=WORD,
                           font='Courier 10',
                           fg='white',
                           bg='black')
    textbox.tag_config('italic', font='Courier 8 italic')  # Defining 'italic' option
    textbox.grid(row=1, column=14, columnspan=6, rowspan=14, padx=0, sticky=N)

    # Display the app
    draw_board()

    # This animation right here is literally the best part of the program.
    flicker_textbox(900, 'grey')
    flicker_textbox(1000, 'grey')
    window.after(1000, say, "Initialising speech module...")
    window.after(2000, say, "\nhello world")

    window.mainloop()
