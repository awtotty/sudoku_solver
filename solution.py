assignments = []

# Moved for initialization
def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [a+b for a in A for b in B]

### Initialize game board structure and units
rows = 'ABCDEFGHI'
cols = '123456789'
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
# Add diagonal units
diag_units = [ [r+c for r,c in zip(rows,cols)], [r+c for r,c in zip(list(reversed(rows)),cols)] ]
unitlist = row_units + column_units + square_units + diag_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """
    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}
    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    # Find all instances of naked twins
    # Naked twins if: 1. both have length == 2, 2. both in same unit

    # Focus on one unit at a time
    for unit in unitlist:
        # Find boxes with 2 digits:
        doubles = [ box for box in unit if len(values[box]) == 2 ]
        for double in doubles:
            # Find ntwins
            ntwins = [ box for box in doubles if box != double and values[box] == values[double] ]
            if ntwins:
                # Found a pair of naked twins, so remove those digits from non-twin peers in this unit
                ntwins.append(double)
                for non_twin_peer in set(unit)-set(ntwins):
                    # Remove each digit from peers
                    for digit in values[double]:
                        assign_value(values, non_twin_peer, values[non_twin_peer].replace(digit,''))
    return values

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    chars = []
    digits = '123456789'
    for c in grid:
        if c in digits:
            chars.append(c)
        if c == '.':
            chars.append(digits)
    assert len(chars) == 81
    return dict(zip(boxes, chars))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """
    Go through all the boxes, and whenever there is a box with a value, eliminate this value from the values of all its peers.
    Args:
        values(dict): The dictionary representing possible values at location on the board
    Returns:
        The dictionary representing possible values at location on the board.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    """
    Go through all the units, and whenever there is a unit with a value that only fits in one box, assign the value to this box.
    Args:
        values(dict): The dictionary representing possible values at location on the board
    Returns:
        The dictionary representing possible values at location on the board.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values, dplaces[0], digit) # Update function
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Args:
        values(dict): The dictionary representing possible values at location on the board
    Returns:
        The dictionary representing possible values at location on the board.
        The dictionary representation of the final sudoku grid if solution found.
        False if no solution.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Cycle through reduction techniques
        values = eliminate(values)
        values = only_choice(values)
        # Add naked_twins
        values = naked_twins(values)
            # Note: Adding naked_twins to the reduction increased computation time by about 0.007 seconds. It is likely that it is not efficient for simple sudokus that can be solved easily with elimination and only_choice alone. Perhaps more challenging sudokus warrent using it.

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Use DFS and propogation to create a search tree and return solution.
    Args:
        values(dict): the dictionary representing possible values at location on the board
        values(boolean): False if no solution exists
    Returns:
        The dictionary representing possible values at location on the board.
        The dictionary representation of the final sudoku grid if solution found.
        False if no solution.
    """
    values = reduce_puzzle(values)

    # Base case
    if values is False:
        return False
    if all(len(values[s]) == 1 for s in values):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    unsolved_boxes = dict( (s, len(values[s]) ) for s in values if len(values[s]) > 1 )
    box = min(unsolved_boxes, key=unsolved_boxes.get)

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for digit in values[box]:
        new_values = values.copy()
        assign_value(new_values, box, digit)    # update function
        attempt = search(new_values)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        grid(dict): The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    # Initialize grid as dict
    values = grid_values(grid)
    # Solve
    return search(values)

# Add visual
if __name__ == '__main__':
    # Included for timing
    from timeit import default_timer as timer

    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    # Start condition
    # display(grid_values(diag_sudoku_grid))

    # End condition
    display(solve(diag_sudoku_grid))

    # Uncomment for timing
    # start = timer()
    # solve(diag_sudoku_grid)
    # print(timer()-start)

    # Visualization
    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
