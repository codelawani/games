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

# Read the test data from a file
with open('test_data.txt', 'r') as f:
    test_lines = f.read().splitlines()

# Split the test data into individual tests
tests = []
current_test = {}
for line in test_lines:
    cols = ['Id', 'Description', 'Steps',
            'Expected', 'Actual', 'Result', 'Comment']
    if line in cols:

    if line.startswith('Id'):
        if current_test:
            tests.append(current_test)
        current_test = {'id': int(line.split()[1])}
    elif line.startswith('Description'):
        current_test['description'] = line.split('Description ')[1]
    elif line.startswith('Steps'):
        current_test['steps'] = []
        current_test['steps'].append(line.split('Steps\n\n')[1])
    elif line.startswith('Expected'):
        current_test['expected'] = line.split('Expected\n\n')[1]
    elif line.startswith('Actual'):
        current_test['actual'] = line.split('Actual\n\n')[1]
    elif line.startswith('Result'):
        current_test['result'] = line.split('Result\n\n')[1]
    elif line.startswith('Comment'):
        current_test['comment'] = line.split('Comment\n\n')[1]
tests.append(current_test)  # Add the last test to the list

# Add the test data to the table
for test in tests:
    row_cells = table.add_row().cells
    row_cells[0].text = str(test['id'])
    row_cells[1].text = test['description']
    # Combine multiple steps into one cell
    row_cells[2].text = '\n'.join(test['steps'])
    row_cells[3].text = test['expected']
    row_cells[4].text = test['actual']
    row_cells[5].text = test['result']
    row_cells[6].text = test['comment']

# Save the document
doc.save('test_results.docx')
