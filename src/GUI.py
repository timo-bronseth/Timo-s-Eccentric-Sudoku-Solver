# -------------------------------------------------
# Timo's wonderfwl multi-line code commenting area!
#                              C
# muuullttiiii                      O  O
#                  liiiiiineeee            L  !
# -------------------------------------------------
from tkinter.scrolledtext import *
from tkinter import *
from SudokuSolver import *

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
    print("\nIterating loop once.")
    say("\nIterating loop once.")
    recolour_all("white")  # Reset all cells to white, just in case they have colour.
    board_snapshot = working_board.copy()  # To compare with after, for colouring changed cells.

    # Run loop
    result = solve_board(working_board, output_board, cycles=0, single_cycle=True)

    # Messages
    # say(broadcast)  # TODO: Say more interesting and relevant stuff in the textbox.

    # if result == 'backtrack':
    #     say("\nConflict found. Backtracking...")
    #     say("Brute force insertion history (old_value, index, inserted_value):\n    " + str(manual_inserts))
    # elif result == 'insert':
    #     say("\nBoard was not solved by possibility_eliminator algorithm." +
    #         "\nProceeding with manually inserted value, and backtracking if that does not work.")

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
    print("\n\nRunning the solver.")
    say("\n\nRunning the solver.")
    recolour_all("white")  # Reset all cells to white, just in case they have colour.

    # Run loop
    start_exec = time.time()  # Measure execution time.
    solve_board(working_board, output_board)
    end_exec = time.time()

    # Victory message and results
    say("\nFound solution!")
    say("\nNumber of manual inserts needed: " + str(inserts) + ".")
    say("Number of backtracks needed:" + str(backtracks) + ".")
    print("Execution time:", end_exec - start_exec)
    say("Execution time: " + str(end_exec - start_exec))

    # Update the window.
    update_output_board(working_board, output_board)


# Display text into the textbox.
def say(text):
    textbox.insert(END, text + '\n')
    textbox.see(END)  # Scrolls down if text exceeds bottom of textbox.
# TODO: Make this into a class, and then import it elsewhere, so can use this everywhere?


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

    # Output text box for prints.
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
