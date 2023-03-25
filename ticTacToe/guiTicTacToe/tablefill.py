#!/usr/bin/env python3
import docx

# Define the table structure (number of rows and columns)
ROWS = 2
COLUMNS = 7

# Create a new Word document
doc = docx.Document()

# Add a table to the document with the specified number of rows and columns
table = doc.add_table(rows=ROWS, cols=COLUMNS)

# Define the header row
header = table.rows[0].cells
header[0].text = 'ID'
header[1].text = 'Description'
header[2].text = 'Steps'
header[3].text = 'Expected'
header[4].text = 'Actual'
header[5].text = 'Result'
header[6].text = 'Comment'

# Define the test data
tests = [{'id': 1,        'description': 'Test the init() method of TicTacToe class to ensure that it creates a game board with 9 buttons and a reset button in the Tkinter root window.',        'steps': ['Create an instance of TicTacToe class with a Tkinter root window.',            'Check that the board_frame attribute of the instance is a Tkinter Frame widget.',            'Check that the board_buttons attribute of the instance is a list of 9 Tkinter Button widgets.',            'Check that the reset_button attribute of the instance is a Tkinter Button widget.'],
          'expected': 'board_frame attribute is a Tkinter Frame widget, board_buttons attribute is a list of 9 Tkinter Button widgets, and reset_button attribute is a Tkinter Button widget.',
          'actual': 'board_frame attribute is a Tkinter Frame widget, board_buttons attribute is a list of 9 Tkinter Button widgets, and reset_button attribute is a Tkinter Button widget.',
                      'result': 'Pass',
                      'comment': 'init() method of TicTacToe class creates the game board as expected.'
          },
         # Add more tests here...
         ]

# Add the test data to the table
for test in tests:
    row_cells = table.add_row().cells
    row_cells[0].text = str(test['id'])
    row_cells[1].text = test['description']
    row_cells[2].text = test['steps']
    row_cells[3].text = test['expected']
    row_cells[4].text = test['actual']
    row_cells[5].text = test['result']
    row_cells[6].text = test['comment']

# Save the document
doc.save('test_results.docx')
