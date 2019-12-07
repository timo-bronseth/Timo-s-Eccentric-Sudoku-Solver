#  The following board is determinate given the starting clues (i.e. it has a single solution).
#  This is a one-dimensional list, but I slice it up into 6-digit rows during execution.
determinate_board_0 = ["Determinate board 0",  # Board name
                     [0, 6, 0, 0, 0, 0,  # Row 0
                      0, 0, 0, 6, 2, 4,  # Row 1
                      3, 0, 4, 0, 1, 0,  # Row 2
                      0, 0, 0, 2, 0, 0,  # Row 3
                      0, 0, 0, 4, 5, 0,  # Row 4
                      0, 0, 1, 0, 0, 2]  # Row 5
                     ]  # Concatenated: 060000000624304010000200000450001002

determinate_board_1 = ["Determinate board 1",  # Board name
                     [3, 0, 1, 0, 4, 0,
                      0, 5, 6, 0, 0, 3,
                      0, 0, 0, 0, 0, 0,
                      0, 0, 4, 2, 0, 0,
                      1, 0, 0, 0, 6, 0,
                      0, 4, 0, 3, 1, 2]
                     ]  # Concatenated: 301040056003000000004200100060040312

#  The following board has multiple solutions given the starting clues.
indeterminate_board_0 = ["Indeterminate board 0",
                       [0, 6, 0, 0, 0, 0,
                        0, 0, 0, 6, 0, 4,
                        3, 0, 4, 0, 1, 0,
                        0, 0, 0, 2, 0, 0,
                        0, 0, 0, 4, 0, 0,
                        0, 0, 0, 0, 0, 2]
                       ]  # Concatenated: 060000000004304010000200000400000002


indeterminate_board_1 = ["Indeterminate board 1",
                       [1, 0, 3, 0, 5, 0,
                        0, 5, 0, 1, 0, 3,
                        2, 0, 1, 0, 6, 0,
                        0, 6, 0, 2, 0, 1,
                        3, 0, 2, 0, 4, 0,
                        0, 4, 0, 3, 0, 2]
                       ]  # Concatenated: 103050050103201060060201302040040302

maximum_entropy_board = ["Maximum entropy board",
                         [0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0,
                          0, 0, 0, 0, 0, 0]
                         ]  # Concatenated: 000000000000000000000000000000000000

determinate_boards = list()  # TODO: Call a random board from this list maybe.
indeterminate_boards = list()
