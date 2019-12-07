solution_set = {1, 2, 3, 4, 5, 6}  # What needs to be filled into all horizontal lines, vertical lines and squares.
top_left = [0, 1, 2, 6, 7, 8]  # Indices of the 6 top left cells.
top_right = [3, 4, 5, 9, 10, 11]
left = [12, 13, 14, 18, 19, 20]
right = [15, 16, 17, 21, 22, 23]
bottom_left = [24, 25, 26, 30, 31, 32]
bottom_right = [27, 28, 29, 33, 34, 35]


def print_board(board):
    board = ['•' if n == 0 else n for n in board]
    for i in range(0, len(board), 6):
        print("\t" + str(board[0+i]) +
              "\t" + str(board[1+i]) +
              "\t" + str(board[2+i]) +
              "\t" + str(board[3+i]) +
              "\t" + str(board[4+i]) +
              "\t" + str(board[5+i]))


def slice_row(board, index):
    row = board[0+6*index:6+6*index]
    return row


def place_row(board, index, row):
    for i, n in enumerate(row):
        board[i+6*index] = n


def slice_column(board, index):
    column = board[index::6]
    return column


def place_column(board, index, column):
    for i, n in enumerate(column):
        board[index + i*6] = n


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
            conflicts = compare_group(row_values)
            if conflicts == "conflicts":
                return conflicts

            # Inserts the row back into the board.
            # Each cell in the row should now contain either
            # a digit, or a set with all the possible digits.
            place_row(working_board, i, row_values)

        for i in range(0, 6):  # And then for every column.
            column_values = slice_column(working_board, i)

            conflicts = compare_group(column_values)
            if conflicts == "conflicts":
                return conflicts

            place_column(working_board, i, column_values)

        for i in range(0, 6):  # Loop for every square group.
            square = slice_square(working_board, i)
            # This returns a tuple with: (set of cell values, set of cell indices).

            conflicts = compare_group(square[0])
            if conflicts == "conflicts":
                return conflicts

            place_square(working_board, square[0], square[1])

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

    print("Setting cell at index", cell_index, "to", str(insert) +
          ", from possible digits", str(possibles) + ".")
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
