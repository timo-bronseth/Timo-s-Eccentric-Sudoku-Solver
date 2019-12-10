# -------------------------------------------------------------------------------------
# The goal I had in mind for this code was to minimise the need for brute force search.
# For that, I use two main algorithms:
#    1) "possibility_eliminator()" for solving almost all determinate puzzles quickly,
#    2) and brute for search for indeterminate puzzles.
#
# Timo Brønseth, December 2019
# -------------------------------------------------------------------------------------
from math import floor
from SudokuBoards import *
from tkinter.scrolledtext import *
from tkinter import *

# TODO: Make it be 9x9.

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
def iterate_loop():
    global flip, unresolved_cells, insert_count, backtrack_count, iteration_count, output_board

    for i, cell in enumerate(working_board):
        if len(labels[i].get()) > 0:
            output_board[i].set(int(labels[i].get()))

    # Check if board is empty.
    if len(working_board) == 0:
        print("\nCould not iterate. Board completely empty.")
        say("\nCould not iterate. Board completely empty.")
        return None

    # Check if board is already full.
    if len([i for i in working_board if isinstance(i, int) and i > 0]) == 81:
        print("\nCould not iterate. Board already solved.")
        say("\nCould not iterate. Board already solved.")
        return None

    # Prepare for iteration
    iteration_count += 1
    recolour_all("white")  # Reset all cells to white, just in case they have colour.
    board_snapshot = working_board.copy()  # To compare with after, for colouring changed cells.
    print("\nIteration " + str(iteration_count) + ".")

    # Fit the lines properly into the textbox.
    if iteration_count > 9:
        say("\n--------------Iteration " + str(iteration_count) + "--------------")
    else:
        say("\n--------------Iteration " + str(iteration_count) + "---------------")

    if flip:
        # The following function searches through the board and, if no conflict is found,
        # returns a list of all the cells it could not find definite solutions for,
        # in the form of [(cell_value0, cell_index0), (cell_value1, cell_index1), ...]
        # If a conflict is found, it returns "conflicts".
        unresolved_cells = possibility_eliminator(working_board, output_board)

        # Tell the world
        say("\nUpdating possibility map.")

        # Which colour should changed cells be coloured in?
        update_colour = "green"

        # Flip the flip: True = False, and False = True
        flip = not flip

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

    elif not flip:
        # If there were any conflicts found by possibility_eliminator()...
        if unresolved_cells == "conflicts":
            update_colour = "red"

            print("\n    ___Found conflict:___")
            print_board(working_board)
            print("\nConflict found. Backtracking..." +
                  "\nBrute force insertion history (old_value, index, inserted_value):\n    ", manual_inserts)
            say("\nCONFLICTS FOUND.")
            say("Backtracking..." +
                "\nBrute force insertion history (old_value, index, inserted_value):\n    " + str(manual_inserts),
                'italic')
            backtrack_count += 1

            # Colour all the cells decided during the the conflicted iteration red.
            colour_updated_cells(working_board.copy(), board_snapshots[-1], update_colour)

            brute_force_backtrack(working_board, manual_inserts, board_snapshots)

            # Flip the flip: True = False, and False = True
            flip = not flip

            # We don't want the board to updated this iteration,
            # so that we have time to see which digits are red.
            return

        # If the board is unsolvable...
        elif unresolved_cells == "unsolvable":
            update_colour = "red"

            print("\nUNSOLVABLE PUZZLE.\n" +
                  "Please feed me a proper puzzle next time.")
            say("\nUNSOLVABLE PUZZLE.")
            say("\nPlease feed me a proper puzzle next time.", 'italic')

            # Reset global variables so that user can solve new puzzles.
            reset_globals()

            recolour_all(update_colour)
            return None

        # If there are any unresolved cells, and no conflicts have been found...
        else:
            update_colour = "yellow"

            print("\n    __Incomplete solution:__")
            print_board(working_board)
            print("\nBoard was not solved by possibility_eliminator algorithm." +
                  "\nProceeding with manually inserted value, and backtracking if that does not work.")
            say("\nCOULD NOT RESOLVE.")
            say("Board was not solved by possibility_eliminator algorithm." +
                "\nProceeding with manually inserted value, and backtracking if that does not work.",
                'italic')
            insert_count += 1

            # The following algorithm only searches through unresolved digits in unresolved cells,
            # so there's a greatly reduced need for brute force compared to a simple brute force search.
            brute_force_insert(working_board, unresolved_cells, manual_inserts, board_snapshots)

            # Flip the flip: True = False, and False = True
            flip = not flip

    # Formatting
    # format_board(working_board)  # TODO: Make format_board() work here.
    updated_board = working_board.copy()
    updated_board = [value if value in [1, 2, 3, 4, 5, 6, 7, 8, 9] else '' for i, value in enumerate(updated_board)]
    update_output_board(updated_board, output_board)

    # Colour all the cells that have been decided since last iteration.
    colour_updated_cells(updated_board, board_snapshot, update_colour)


# tkinter .after method in a loop freezes animations somehow.
# def run_loop():
#     while True:
#         window.after(300)
#         iterate_loop()
#         i = +1


# -------------------------------------------------------------------------------------
# Sudoku Functions
# -------------------------------------------------------------------------------------

solution_set = {1, 2, 3, 4, 5, 6, 7, 8, 9}  # What needs to be filled into all horizontal lines, vertical lines and squares.
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
            recolour(i, update_colour)
    return


def reset_globals():
    global insert_count, backtrack_count, iteration_count, manual_inserts, board_snapshots, unresolved_cells, flip
    insert_count, backtrack_count, iteration_count = 0, 0, 0
    manual_inserts.clear()
    board_snapshots.clear()
    list(unresolved_cells).clear()
    flip = True


def print_board(board):
    board = ['•' if n == 0 else n for n in board]
    for i in range(0, len(board), 9):
        print("\t" + str(board[0 + i]) +
              "\t" + str(board[1 + i]) +
              "\t" + str(board[2 + i]) +
              "\t" + str(board[3 + i]) +
              "\t" + str(board[4 + i]) +
              "\t" + str(board[5 + i]))


def slice_row(board, index):
    row = board[0 + 9 * index:9 + 9 * index]
    return row


def place_row(board, index, row):
    for i, n in enumerate(row):
        board[i + 9 * index] = n


def slice_column(board, index):
    column = board[index::9]
    return column


def place_column(board, index, column):
    for i, n in enumerate(column):
        board[index + i * 9] = n


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
    # for i, cell in enumerate(working_board):
    #     if len(labels[i].get() > 0):
    #         output_board[i].set(int(4))
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
    conflicts = False

    while True:
        old_board = tuple(working_board)
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
            # with other cells in the row.
            # NOTE: This function returns a something other
            # than the list it takes as an argument.
            if compare_group(row_values) == "conflicts":
                conflicts = True

            # Inserts the row back into the board.
            # Each cell in the row should now contain either
            # a digit, or a set with all the possible digits.
            place_row(working_board, i, row_values)

        for i in range(0, 9):  # And then for every column.
            column_values = slice_column(working_board, i)

            if compare_group(column_values) == "conflicts":
                conflicts = True

            place_column(working_board, i, column_values)

        for i in range(0, 9):  # Loop for every square group.
            square = slice_square(working_board, i)
            # This returns a tuple with: (set of cell values, set of cell indices).

            if compare_group(square[0]) == "conflicts":
                conflicts = True

            place_square(working_board, square[0], square[1])

        #  If conflicts have been found, then return as appropriate.
        if conflicts and len(manual_inserts) == 0:
            return "unsolvable"
        elif conflicts:
            return "conflicts"

        # If the board has not changed since the last iteration,
        # then either it is solved or the loop cannot solve it
        # (e.g. because the board clues are indeterminate).
        if tuple(working_board) == old_board:
            unresolved_cells = find_unresolved(working_board)
            return unresolved_cells


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

    # Tell the world.
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
# Tkinter GUI
# -------------------------------------------------------------------------------------


# Global variables
working_board = []  # This one is used by the algorithms.
output_board = []  # When cells on this board are changed, it immediately shows up in the tk app.
labels = []  # All the cells ('labels') that need to be drawn into the tkinter window.


# Draw the Sudoku board onto the tk window.
def draw_board():
    numcells = 0  # Counter for the loop; tracks which number cell we're on (up to 36).

    # Draw all the cells in the 6x6 board.
    for i in range(0, 9):
        for j in range(0, 9):
            output_board.append(StringVar())
            # Values that go into the board need to be the unique StringVar data type.
            # Now, every time output_board[i] is changed (e.g. to a new digit),
            # it immediately updates the corresponding label in the tkinter window.

            labels.append(Entry(window,
                                textvariable=output_board[numcells],
                                # StringVar digits need to go into 'textvariable' in order to be dynamically updatable.
                                # Later, you update them by setting 'output_board[i].set(new_value)', and then the
                                # labels on the window immediately changes.

                                font=("Courier", 32),
                                width=2,
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
        [int(value) if value in [1, 2, 3, 4, 5, 6, 7, 8, 9, '1', '2', '3', '4', '5', '6', '7', '8', '9']
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

    # If user entered a board not with 36 digits...
    if len(entered_board) != 81:
        # Correct list to 36 digits by cutting it,
        # or adding missing 0's.
        entered_board = entered_board[:81] + [0] * (81 - len(entered_board))

    format_board(entered_board)  # Updates global list working_board
    update_output_board(working_board, output_board)


# Clear the board. Run this when user clicks "CLEAR"
def entry_clear():
    flash_labels(100)
    reset_globals()
    board = [0 for i in range(0, 81)]
    format_board(board)
    update_output_board(working_board, output_board)
    say("-------------BOARD UPDATED--------------")


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


def set_determinate_board():
    board = determinate_board_0
    flash_labels(100)
    entry_click()
    format_board(board[1])
    update_output_board(working_board, output_board)
    print("\nActive board:", board[0])
    say("\nActive board: " + str(board[0]))


def set_indeterminate_board():
    board = indeterminate_board_0
    flash_labels(100)
    entry_click()
    format_board(board[1])
    update_output_board(working_board, output_board)
    print("\nActive board:", board[0])
    say("\nActive board: " + str(board[0]))


def set_maxent_board():
    board = maximum_entropy_board
    flash_labels(100)
    entry_click()
    format_board(board[1])
    update_output_board(working_board, output_board)
    print("\nActive board:", board[0])
    say("\nActive board: " + str(board[0]))


# Loading the application...
if __name__ == "__main__":
    # Tkinter app window
    window = Tk()
    window.title("Timo's Eccentric Sudoku Solver!")

    # Button for updating the board.
    button_iterate = Button(window,
                            width=4,
                            height=7,
                            text="I\nT\nE\nR\nA\nT\nE",
                            font=("Arial black", 10),
                            borderwidth=3,
                            relief=RAISED,
                            command=iterate_loop
                            # command=lambda: update_board(board)  # Command cannot take arguments unless it uses "lambda"
                            )
    button_iterate.grid(row=0, column=0, rowspan=4, padx=7, pady=2)

    # tkinter .after method in a loop freezes animations somehow.
    # # Button for looping automatically.
    # button_run = Button(window,
    #                     width=4,
    #                     height=3,
    #                     text="R\nU\nN",
    #                     font=("Arial black", 8),
    #                     borderwidth=3,
    #                     relief=RAISED,
    #                     command=run_loop
    #                     # command=lambda: update_board(board)  # Command cannot take arguments unless it uses "lambda"
    #                     )
    # button_run.grid(row=4, column=0, rowspan=2, padx=7, pady=2)

    # Button to get puzzles entered by user.
    button_entry = Button(window,
                          text="ENTER",
                          width=7,
                          font=("Arial black", 10),
                          borderwidth=2,
                          relief=RAISED,
                          command=entry_click)
    button_entry.grid(row=10, column=4, columnspan=3, sticky=E)
    button_entry_clear = Button(window,
                                text="CLEAR",
                                width=7,
                                font=("Arial black", 10),
                                borderwidth=2,
                                relief=RAISED,
                                command=entry_clear)
    button_entry_clear.grid(row=10, column=4, columnspan=3, sticky=W)
    puzzle_info = Label(window,
                        text="Enter puzzle here.\n" +
                             "(Must be a string of 36 digits, with\n" +
                             "0 for empty cells, e.g. 001402...)",
                        font=("Courier", 12),
                        width=35)
    puzzle_info.grid(row=11, column=1, columnspan=9, rowspan=3)
    puzzle_entry = Entry(window, font=("Courier", 12), width=35)
    puzzle_entry.grid(row=9, column=1, columnspan=9, pady=5)

    # Button for trying determinate_board
    button_determinate_board = Button(window,
                                      text="determinate board",
                                      width=18,
                                      font=("Arial black", 10),
                                      borderwidth=2,
                                      relief=RAISED,
                                      command=set_determinate_board)
    button_determinate_board.grid(row=9, column=9, columnspan=4, pady=10)

    # Button for trying indeterminate_board
    button_indeterminate_board = Button(window,
                                        text="indeterminate board",
                                        width=18,
                                        font=("Arial black", 10),
                                        borderwidth=2,
                                        relief=RAISED,
                                        command=set_indeterminate_board)
    button_indeterminate_board.grid(row=10, column=9, columnspan=4, pady=2)

    # Button for trying maximum_entropy_board
    button_maximum_entropy_board = Button(window,
                                          text="maximum entropy board",
                                          width=22,
                                          font=("Arial black", 10),
                                          borderwidth=2,
                                          relief=RAISED,
                                          command=set_maxent_board)
    button_maximum_entropy_board.grid(row=11, column=9, columnspan=6, pady=2)

    textbox = ScrolledText(window, width=40, height=28, wrap=WORD, font='Courier 10', fg='white', bg='black')
    textbox.tag_config('italic', font='Courier 9 italic')
    textbox.grid(row=0, column=10, rowspan=11, padx=20, sticky=N)

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
