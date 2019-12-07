# -------------------------------------------------------------------------------------
# The goal I had in mind for this code was to minimise the need for brute search.
# For that, I use two main algorithms...
#    1) possibility_eliminator() for solving almost all determinate puzzles quickly,
#    2) and brute_force_insert() and brute_force_backtrack() for indeterminate puzzles
#    where you have to try values to see if they work.
# -------------------------------------------------------------------------------------
from math import floor
from SudokuBoards import *
import time

# TODO: Exception handling. working on it!
# TODO: Raise exceptions, 'finally' end with an animation of
#       the window turning red and flickering until it's dead.

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

        # Check if puzzle is unsolvable.
        print(unresolved_cells)
        if unresolved_cells == "unsolvable":
            initiate_traumatic_shutdown()

        if len(unresolved_cells) == 0:  # If there are 0 unresolved cells...
            # Check if puzzle is wrong.
            if len([i for i in working_board if isinstance(i, int) and i > 0]) < 36:
                say("PUZZLE IS WRONG WHAT ARE YOU FEEDING ME")
            initiate_traumatic_shutdown()


            # Telling the world
            print("\n    ___Found solution:___")
            print_board(working_board)
            print("\nNumber of manual inserts needed:", str(inserts) + ".")
            print("Number of backtracks needed:", str(backtracks) + ".")
            say("\nSOLUTION FOUND.")
            say("\nNumber of manual inserts needed: " + str(inserts) + ".")
            say("Number of backtracks needed: " + str(backtracks) + ".")
            inserts = 0  # Resets count in case user wants to solve another puzzle.
            backtracks = 0
            return True

        # If there were any conflicts found by possibility_eliminator()...
        elif unresolved_cells == "conflicts":
            print("\n    ___Found conflict:___")
            print_board(working_board)
            print("\nConflict found. Backtracking...")
            print("Brute force insertion history (old_value, index, inserted_value):\n    ", manual_inserts)
            say("\nCONFLICTS FOUND.")
            say("\nBacktracking...")
            say("Brute force insertion history (old_value, index, inserted_value):\n    " + str(manual_inserts))
            backtracks += 1

            working_board = brute_force_backtrack(working_board, manual_inserts, board_snapshots)

        # If there are any unresolved cells, and no conflicts have been found...
        else:
            print("\n    __Incomplete solution:__")
            print_board(working_board)
            print("\nBoard was not solved by possibility_eliminator algorithm." +
                  "\nProceeding with manually inserted value, and backtracking if that does not work.")
            say("\nCOULD NOT RESOLVE.")
            say("\nBoard was not solved by possibility_eliminator algorithm." +
                "\nProceeding with manually inserted value, and backtracking if that does not work.")
            inserts += 1

            # The following algorithm only searches through unresolved digits in unresolved cells,
            # so there's a greatly reduced need for brute force compared to a simple brute force search.
            working_board = brute_force_insert(working_board, unresolved_cells, manual_inserts, board_snapshots)
        cycles += 1


# -------------------------------------------------------------------------------------
# This is from SudokuFunctions
# -------------------------------------------------------------------------------------

solution_set = {1, 2, 3, 4, 5, 6}  # What needs to be filled into all horizontal lines, vertical lines and squares.
top_left = [0, 1, 2, 6, 7, 8]  # Indices of the 6 top left cells.
top_right = [3, 4, 5, 9, 10, 11]
left = [12, 13, 14, 18, 19, 20]
right = [15, 16, 17, 21, 22, 23]
bottom_left = [24, 25, 26, 30, 31, 32]
bottom_right = [27, 28, 29, 33, 34, 35]


def initiate_traumatic_shutdown():
    say("AAraaarahghhhh!")
    recolour_all("red")


def print_board(board):
    board = ['•' if n == 0 else n for n in board]
    for i in range(0, len(board), 6):
        print("\t" + str(board[0 + i]) +
              "\t" + str(board[1 + i]) +
              "\t" + str(board[2 + i]) +
              "\t" + str(board[3 + i]) +
              "\t" + str(board[4 + i]) +
              "\t" + str(board[5 + i]))


def slice_row(board, index):
    row = board[0 + 6 * index:6 + 6 * index]
    return row


def place_row(board, index, row):
    for i, n in enumerate(row):
        board[i + 6 * index] = n


def slice_column(board, index):
    column = board[index::6]
    return column


def place_column(board, index, column):
    for i, n in enumerate(column):
        board[index + i * 6] = n


def slice_square(board, index):
    if index == 0:  # This is the first square, i.e. the top left corner.
        square = [n for i, n in enumerate(board) if i in set(top_left)]
        return square, top_left  # Returns a tuple
    elif index == 1:
        square = [n for i, n in enumerate(board) if i in set(top_right)]
        return square, top_right
    elif index == 2:
        square = [n for i, n in enumerate(board) if i in set(left)]
        return square, left
    elif index == 3:
        square = [n for i, n in enumerate(board) if i in set(right)]
        return square, right
    elif index == 4:
        square = [n for i, n in enumerate(board) if i in set(bottom_left)]
        return square, bottom_left
    elif index == 5:
        square = [n for i, n in enumerate(board) if i in set(bottom_right)]
        return square, bottom_right


def place_square(board, square_values, square_indices):
    for i, n in enumerate(square_values):
        board[square_indices[i]] = n


def contains_duplicates(list_):
    set_compare = set()
    list_ = [i for i in list_ if isinstance(i, int) and i > 0]  # Only search for digit duplicates.

    for i in list_:
        if i in set_compare:
            return True
        else:
            set_compare.add(i)
    return False


# Find any unresolved cells and store them in a list with both cell values and cell indices.
def find_unresolved(board):
    unresolved_cells = [(n, index) for index, n in enumerate(board) if type(n) == set]
    return unresolved_cells


# This goes through the list of all cells given to it,
# and returns the list with fewest remaining possible digits.
# Input must be a list of the form [(cell_value, cell_index), ...]
def find_cell_with_fewest_possibles(cells):
    for i in cells:
        if i == cells[0] or len(i[0]) < len(cell_fewest[0]):
            cell_fewest = i
    return cell_fewest


# output_board takes all the values from working_board,
# which will immediately be displayed in the tkinter window.
def update_output_board(working_board, output_board):
    for i, cell in enumerate(working_board):
        output_board[i].set(working_board[i])
    return working_board, output_board


def compare_group(group):  # A "group" is a collection of 6 items like a row, column or a square.
    definite_digits_group = [i for i in group if type(i) == int]  # Digits that are already in the group.
    possible_digits_group = solution_set - set(definite_digits_group)  # Digits that still need to be placed.

    if contains_duplicates(definite_digits_group):
        # print("Group contains duplicate.")
        return "conflicts"

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
    conflicts = None

    while True:
        old_board = tuple(working_board)
        # I need to check if the board has changed at all since the last iteration of this while loop,
        # so I will compare old_board to the new board. But old_board needs to be stored as a tuple,
        # otherwise the function calls below would just simultaneously edit both.
        #     When you assign one list pointer to another list pointer (e.g. "list1 = list2),
        # they point to the same memory locations; but when you assign a tuple pointer to another
        # tuple pointer (e.g. "tuple1 = tuple2"), they point to different memory locations.

        for i in range(0, 6):  # Run the loop for every row.

            # Fetches the row to be analysed.
            row_values = slice_row(working_board, i)

            # Analyses each cell in the row, and writes in
            # a set with all the digits that do not conflict
            # with other cells in the row.
            # NOTE: This function returns a something other
            # than the list it takes as an argument.
            conflicts = compare_group(row_values)

            # Inserts the row back into the board.
            # Each cell in the row should now contain either
            # a digit, or a set with all the possible digits.
            place_row(working_board, i, row_values)

        if conflicts == "conflicts":
            break

        for i in range(0, 6):  # And then for every column.
            column_values = slice_column(working_board, i)

            conflicts = compare_group(column_values)
            if conflicts == "conflicts":
                return conflicts

            place_column(working_board, i, column_values)

        if conflicts == "conflicts":
            break

        for i in range(0, 6):  # Loop for every square group.
            square = slice_square(working_board, i)
            # This returns a tuple with: (set of cell values, set of cell indices).

            conflicts = compare_group(square[0])

            place_square(working_board, square[0], square[1])

        if conflicts == "conflicts":
            break

        # If the board has not changed since the last iteration,
        # then either it is solved or the loop cannot solve it
        # (e.g. because the board clues are indeterminate).
        if tuple(working_board) == old_board:
            unresolved_cells = find_unresolved(working_board)
            return unresolved_cells

    if conflicts == "conflicts" and len(manual_inserts) == 0:
        return "unsolvable"
    else:
        return "conflicts"


def brute_force_insert(board, unresolved_cells, manual_inserts, board_snapshots):
    cell_fewest_possibles = find_cell_with_fewest_possibles(unresolved_cells)  # Stored as (cell_value, cell_index)
    possibles = cell_fewest_possibles[0]  # Tuple with all the possible digits in the cell.
    insert = min(possibles)  # The smallest digit out of the ones possible.
    cell_index = cell_fewest_possibles[1]

    # Storing information about which inserted digits have been tried,
    # so that we can remove them from the list of digits left to try.
    manual_inserts.append([possibles, cell_index, insert])

    # Storing a snapshot of the board before the brute force insert,
    # so that I can safely restore it in case the insert fails.
    board_snapshots.append(board.copy())

    print("Setting cell at index", cell_index, "to", str(insert) +
          ", from possible digits", str(possibles) + ".")
    say("Setting cell at index (" + str(cell_index % 6) + ", " + str(floor(cell_index/6)) + ") to " + str(insert) +
        ", from possible digits " + str(possibles) + ".")
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

    possibles = manual_inserts[-1][0]  # Gets the possible digits for the most recently edited cell.
    cell_index = manual_inserts[-1][1]
    failed_insert = manual_inserts[-1][2]  # Gets the digit that was tried (and failed) in the brute force search.
    updated_possibles = possibles - {failed_insert}

    # if len(updated_possibles) == 1:  # If there's only one possible left in a cell, cast it as an integer.
    # updated_possibles = min(updated_possibles)
    board[cell_index] = updated_possibles
    manual_inserts.pop(-1)  # Remove the most recent addition to the brute force search history.
    board_snapshots.pop(-1)  # Remove the most recent snapshot, so that we don't return to it again.
    return board


# -------------------------------------------------------------------------------------
# This is from GUI
# -------------------------------------------------------------------------------------
# -------------------------------------------------
from tkinter.scrolledtext import *
from tkinter import *

# Global variables
working_board = []  # This one is used by the algorithms.
output_board = []  # When cells on this board are changed, it immediately shows up in the tk app.
labels = []  # All the cells ('labels') that need to be drawn into the tkinter window.


# Draw the Sudoku board onto the tk window.
def draw_board():
    numcells = 0  # Counter for the loop; tracks which number cell we're on (up to 36).

    # Draw all the cells in the 6x6 board.
    for i in range(0, 6):
        for j in range(0, 6):
            output_board.append(StringVar())
            # Values that go into the board need to be the unique StringVar data type.
            # Now, every time output_board[i] is changed (e.g. to a new digit),
            # it immediately updates the corresponding label in the tkinter window.

            labels.append(Label(window,
                                textvariable=output_board[numcells],
                                # StringVar digits need to go into 'textvariable' in order to be dynamically updatable.
                                # Later, you update them by setting 'output_board[i].set(new_value)', and then the
                                # labels on the window immediately changes.

                                font=("Courier", 30),
                                width=2,
                                height=1,
                                bg="white",
                                borderwidth=1,
                                relief="solid")
                          )
            labels[numcells].grid(row=i, column=j + 1)
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
        [int(value) if value in [1, 2, 3, 4, 5, 6, '1', '2', '3', '4', '5', '6']
         else '' for i, value in enumerate(board)])
    # Make all the zeros invisible.

    return working_board


def recolour(label_num, colour):
    labels[label_num]["bg"] = colour


def recolour_all(colour):
    for i in range(len(labels)):
        recolour(i, colour)


def flash_labels(ms):
    for i in range(len(labels)):
        window.after(0, recolour, i, "black")
        window.after(ms, recolour, i, "white")


# Run this upon user clicking "ENTER"
def entry_click():
    flash_labels(100)  # Just for looks.
    entry_clear()  # Clear board before inserting new one.
    entered_board = []  # The Sudoku puzzle entered by the user. A list of strings.
    entered_board.clear()  # Clear old entry before inserting new one.
    entered_board.extend(puzzle_entry.get())
    format_board(entered_board)  # Updates global list working_board
    update_output_board(working_board, output_board)
    # TODO: Exception handling


# Clear the board. Run this when user clicks "CLEAR"
def entry_clear():
    flash_labels(100)
    board = [0 for i in range(0, 36)]
    format_board(board)
    update_output_board(working_board, output_board)
    # TODO: Exception handling


# Run this when user clicks "ITERATE"
def iterate_loop():

    # Check if board is already full.
    if len([i for i in working_board if isinstance(i, int) and i > 0]) == 36:
        say("\nCould not iterate. Board already solved.")
        return None

    # Prepare for iteration
    print("\nIterating loop once.")
    say("\n\n\n\n\nIterating loop once...\n")
    recolour_all("white")  # Reset all cells to white, just in case they have colour.
    board_snapshot = working_board.copy()  # To compare with after, for colouring changed cells.

    # Run loop
    result = solve_board(working_board, output_board, cycles=0, single_cycle=True)

    # Formatting
    # format_board(working_board)  # TODO: Make format_board() work here.
    updated_board = working_board.copy()
    updated_board = [value if value in [1, 2, 3, 4, 5, 6] else '' for i, value in enumerate(updated_board)]
    update_output_board(updated_board, output_board)

    # Colour all the cells that have been decided since last iteration.
    for i, value in enumerate(updated_board):
        if updated_board[i] != board_snapshot[i] and isinstance(updated_board[i], int):
            recolour(i, "green")


# Run this when user clicks "RUN".
# This will cycle through the loop until the puzzle has been solved.
def run_loop():  # TODO: Make this have flashy animations.
    # Check if board is already full.
    if len([i for i in working_board if isinstance(i, int) and i > 0]) == 36:
        say("\nCould not run. Board already solved.")
        return None

    print("\n\nRunning the solver.")
    say("\n\nRunning the solver.")
    recolour_all("white")  # Reset all cells to white, just in case they have colour.
    board_snapshot = working_board.copy()  # To compare with after, for colouring changed cells.

    # Run loop
    solve_board(working_board, output_board)

    # Update the window.
    update_output_board(working_board, output_board)

    # Colour all the cells that have been decided since last iteration.
    for i, value in enumerate(working_board):
        if working_board[i] != board_snapshot[i] and isinstance(working_board[i], int):
            recolour(i, "green")


# Display text into the textbox.
def say(text):
    textbox.insert(END, text + '\n')
    textbox.see(END)  # Scrolls down if text exceeds bottom of textbox.


def textbox_bg(colour):
    textbox['bg'] = colour


def flicker_textbox(ms, colour):
    window.after(ms, textbox_bg, colour)
    window.after(ms + 50, textbox_bg, 'black')


def set_determinate_board():
    flash_labels(100)
    working_board.clear()
    format_board(determinate_board_0[1])
    update_output_board(working_board, output_board)
    print("\nActive board:", determinate_board_0[0])
    say("\nActive board: " + str(determinate_board_0[0]))


def set_indeterminate_board():
    flash_labels(100)
    working_board.clear()
    format_board(indeterminate_board_0[1])
    update_output_board(working_board, output_board)
    print("\nActive board:", indeterminate_board_0[0])
    say("\nActive board: " + str(indeterminate_board_0[0]))


def set_maxent_board():
    flash_labels(100)
    working_board.clear()
    format_board(maximum_entropy_board[1])
    update_output_board(working_board, output_board)
    print("\nActive board:", maximum_entropy_board[0])
    say("\nActive board: " + str(maximum_entropy_board[0]))


# Loading the application...
# This code only runs if GUI is main entry point.
if __name__ == "__main__":
    # Tkinter app window
    window = Tk()
    window.title("Timo's Eccentric Sudoku Solver!")

    # Button for updating the board.
    button_iterate = Button(window,
                            width=4,
                            height=7,
                            text="I\nT\nE\nR\nA\nT\nE",
                            font=("Arial black", 8),
                            borderwidth=3,
                            relief=RAISED,
                            command=iterate_loop
                            # command=lambda: update_board(board)  # Command cannot take arguments unless it uses "lambda"
                            )
    button_iterate.grid(row=0, column=0, rowspan=3, padx=7, pady=2)

    # Button for looping automatically.
    button_run = Button(window,
                        width=4,
                        height=3,
                        text="R\nU\nN",
                        font=("Arial black", 8),
                        borderwidth=3,
                        relief=RAISED,
                        command=run_loop
                        # command=lambda: update_board(board)  # Command cannot take arguments unless it uses "lambda"
                        )
    button_run.grid(row=4, column=0, rowspan=2, padx=7, pady=2)

    # Button to get puzzles entered by user.
    button_entry = Button(window,
                          text="ENTER",
                          width=7,
                          font=("Arial black", 8),
                          borderwidth=2,
                          relief=RAISED,
                          command=entry_click)
    button_entry.grid(row=7, column=2, columnspan=2, sticky=E)
    button_entry_clear = Button(window,
                                text="CLEAR",
                                width=7,
                                font=("Arial black", 8),
                                borderwidth=2,
                                relief=RAISED,
                                command=entry_clear)
    button_entry_clear.grid(row=7, column=4, columnspan=2, sticky=W)
    puzzle_info = Label(window,
                        text="Enter puzzle here.\n" +
                             "(Must be a string of 36 digits, with\n" +
                             "0 for empty cells, e.g. 001402...)",
                        font=("Courier", 10),
                        width=35)
    puzzle_info.grid(row=8, column=1, columnspan=6)
    puzzle_entry = Entry(window, font=("Courier", 10), width=35)
    puzzle_entry.grid(row=6, column=1, columnspan=6, pady=5)

    # Button for trying determinate_board
    button_determinate_board = Button(window,
                                      text="determinate board",
                                      width=16,
                                      font=("Arial black", 8),
                                      borderwidth=2,
                                      relief=RAISED,
                                      command=set_determinate_board)
    button_determinate_board.grid(row=9, column=1, columnspan=3, pady=5)

    # Button for trying indeterminate_board
    button_indeterminate_board = Button(window,
                                        text="indeterminate board",
                                        width=16,
                                        font=("Arial black", 8),
                                        borderwidth=2,
                                        relief=RAISED,
                                        command=set_indeterminate_board)
    button_indeterminate_board.grid(row=9, column=4, columnspan=3, pady=5)

    # Button for trying maximum_entropy_board
    button_maximum_entropy_board = Button(window,
                                          text="maximum entropy board",
                                          width=20,
                                          font=("Arial black", 8),
                                          borderwidth=2,
                                          relief=RAISED,
                                          command=set_maxent_board)
    button_maximum_entropy_board.grid(row=10, column=1, columnspan=6, pady=5)

    textbox = ScrolledText(window, width=40, height=24, wrap=WORD, fg='white', bg='black')
    textbox.grid(row=0, column=7, rowspan=11, padx=5, sticky=N)

    # Frame
    # TODO: Arrange borders around square groups. Probably with tkinter.Frame?

    # Display the app
    draw_board()

    # This animation right here is literally the best part of the program.
    flicker_textbox(900, 'grey')
    flicker_textbox(1000, 'grey')
    window.after(1000, say, "Initialising speech module...")
    window.after(2200, say, "\nhello world")

    window.mainloop()
