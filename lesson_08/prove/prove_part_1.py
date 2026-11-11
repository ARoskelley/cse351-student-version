"""
Course: CSE 251 
Assignment: 08 Prove Part 1
File:   prove_part_1.py
Author: Aiden Roskelley

Purpose: Part 1 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:

- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- Complete any TODO comments.

-------------------------------------------------------------------------------
CHECKLIST (mark [x] as you go)
-------------------------------------------------------------------------------
Setup
  [ ] Put your name in the Author line above
  [ ] opencv-python is installed (python -m pip install opencv-python)
  [ ] Read the public methods in maze.py (the ones that don't start with '_')

Recursive helper (an inner function inside solve_path)
  [ ] Define the inner function; it takes a position (row, col)
  [ ] If the square can't be moved into, return "not found"
  [ ] Move into the square (maze.move with COLOR) and add it to path
  [ ] Base case: if this is the end position, return "found"
  [ ] Recurse into each of maze.get_possible_moves(row, col)
  [ ] If any recursive call found the end, return "found" right away
  [ ] Dead end: maze.restore() the square, remove it from path,
      return "not found"

solve_path
  [ ] Start the recursion at maze.get_start_pos()
  [ ] Return path (start position first, end position last)

Testing
  [ ] very-small.bmp reports a path length of about 11
  [ ] Grey squares appear where the search backed up
  [ ] The final colored path runs unbroken from start to end
  [ ] All 10 mazes finish with no errors or recursion crashes
  [ ] No "ERROR: You are trying to move..." messages in the output

Submission
  [ ] Submit prove_part_1.py with prove_part_2.py
  [ ] Add a submission comment with your grading category and a 1-2
      sentence justification
-------------------------------------------------------------------------------
"""

import math
from screen import Screen
from maze import Maze
import cv2
import sys

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 800
COLOR = (0, 0, 255)
SLOW_SPEED = 100
FAST_SPEED = 1
speed = SLOW_SPEED

# TODO: Add any functions needed here.

def solve_path(maze):
    """ Solve the maze and return the path found between the start and end positions.  
        The path is a list of positions, (x, y) """
    path = []
    # TODO: Solve the maze recursively while tracking the correct path.

    # Hint: You can create an inner function to do the recursion

    return path


def get_path(log, filename):
    """ Do not change this function """
    # 'Maze: Press "q" to quit, "1" slow drawing, "2" faster drawing, "p" to play again'
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename)

    path = solve_path(maze)

    log.write(f'Drawing commands to solve = {screen.get_command_count()}')

    done = False
    while not done:
        if screen.play_commands(speed): 
            key = cv2.waitKey(0)
            if key == ord('1'):
                speed = SLOW_SPEED
            elif key == ord('2'):
                speed = FAST_SPEED
            elif key == ord('q'):
                exit()
            elif key != ord('p'):
                done = True
        else:
            done = True

    return path


def find_paths(log):
    """ Do not change this function """

    files = (
        'very-small.bmp',
        'very-small-loops.bmp',
        'small.bmp',
        'small-loops.bmp',
        'small-odd.bmp',
        'small-open.bmp',
        'large.bmp',
        'large-loops.bmp',
        'large-squares.bmp',
        'large-open.bmp'
    )

    log.write('*' * 40)
    log.write('Part 1')
    for filename in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        path = get_path(log, filename)
        log.write(f'Found path has length     = {len(path)}')
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_paths(log)


if __name__ == "__main__":
    main()