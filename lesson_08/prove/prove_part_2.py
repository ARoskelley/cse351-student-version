"""
Course: CSE 351 
Assignment: 08 Prove Part 2
File:   prove_part_2.py
Author: <Add name here>

Purpose: Part 2 of assignment 8, finding the path to the end of a maze using recursion.

Instructions:
- Do not create classes for this assignment, just functions.
- Do not use any other Python modules other than the ones included.
- You MUST use recursive threading to find the end of the maze.
- Each thread MUST have a different color than the previous thread:
    - Use get_color() to get the color for each thread; you will eventually have duplicated colors.
    - Keep using the same color for each branch that a thread is exploring.
    - When you hit an intersection spin off new threads for each option and give them their own colors.

This code is not interested in tracking the path to the end position. Once you have completed this
program however, describe how you could alter the program to display the found path to the exit
position:

What would be your strategy?

<Answer here>

Why would it work?

<Answer here>

-------------------------------------------------------------------------------
CHECKLIST (mark [x] as you go)
-------------------------------------------------------------------------------
Setup
  [ ] Put your name in the Author line above
  [ ] Create one shared threading.Lock() at module level

Recursive thread function (e.g. explore(maze, row, col, color))
  [ ] First thing: if stop is set, return
  [ ] Under the lock: if the square can't be moved into, return
      (this thread lost a race or ran into another thread);
      otherwise maze.move() into it with this thread's color
  [ ] If this is the end position: set stop = True and return
  [ ] Get the possible moves; if there are none, return (dead end or
      collision)
  [ ] For every move except the first:
        [ ] Under the lock: get_color() and thread_count += 1
        [ ] Create and start a Thread that runs explore on that move
        [ ] Keep the thread in a list of children
  [ ] Recurse into the first move with the SAME color
  [ ] Only after that recursive call returns, join all child threads

solve_find_end
  [ ] Reset stop = False and thread_count = 0 for each maze
  [ ] Create the first thread at maze.get_start_pos() with get_color()
  [ ] Count the first thread in thread_count
  [ ] Start it, then join it (it joins its children, so this waits for all)

Concurrency checks
  [ ] Don't call join() right after start() (that makes the threads take
      turns instead of running at the same time)
  [ ] Every read-then-write of shared globals happens under the lock
  [ ] Playback shows several colors moving at the same time
  [ ] All threads stop soon after the exit is found

Testing
  [ ] All 10 mazes finish with no errors or crashes
  [ ] No "ERROR: You are trying to move..." messages in the output
  [ ] Thread counts look reasonable (very-small: a few; large: hundreds)
  [ ] If large mazes crash in threads: raise threading.stack_size()
      before creating any threads

Questions and submission
  [ ] Answer "What would be your strategy?" above
  [ ] Answer "Why would it work?" above
  [ ] Submit prove_part_2.py with prove_part_1.py
  [ ] Add a submission comment with your grading category and a 1-2
      sentence justification
-------------------------------------------------------------------------------
"""

import math
import threading 
from screen import Screen
from maze import Maze
import sys
import cv2

# Include cse 351 files
from cse351 import *

SCREEN_SIZE = 700
COLOR = (0, 0, 255)
COLORS = (
    (0,0,255),
    (0,255,0),
    (255,0,0),
    (255,255,0),
    (0,255,255),
    (255,0,255),
    (128,0,0),
    (128,128,0),
    (0,128,0),
    (128,0,128),
    (0,128,128),
    (0,0,128),
    (72,61,139),
    (143,143,188),
    (226,138,43),
    (128,114,250)
)
SLOW_SPEED = 100
FAST_SPEED = 0

# Globals
current_color_index = 0
thread_count = 0
stop = False
speed = SLOW_SPEED

def get_color():
    """ Returns a different color when called """
    global current_color_index
    if current_color_index >= len(COLORS):
        current_color_index = 0
    color = COLORS[current_color_index]
    current_color_index += 1
    return color


# TODO: Add any function(s) you need, if any, here.


def solve_find_end(maze):
    """ Finds the end position using threads. Nothing is returned. """
    # When one of the threads finds the end position, stop all of them.
    global stop
    stop = False




def find_end(log, filename, delay):
    """ Do not change this function """

    global thread_count
    global speed

    # create a Screen Object that will contain all of the drawing commands
    screen = Screen(SCREEN_SIZE, SCREEN_SIZE)
    screen.background((255, 255, 0))

    maze = Maze(screen, SCREEN_SIZE, SCREEN_SIZE, filename, delay=delay)

    solve_find_end(maze)

    log.write(f'Number of drawing commands = {screen.get_command_count()}')
    log.write(f'Number of threads created  = {thread_count}')

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


def find_ends(log):
    """ Do not change this function """

    files = (
        ('very-small.bmp', True),
        ('very-small-loops.bmp', True),
        ('small.bmp', True),
        ('small-loops.bmp', True),
        ('small-odd.bmp', True),
        ('small-open.bmp', False),
        ('large.bmp', False),
        ('large-loops.bmp', False),
        ('large-squares.bmp', False),
        ('large-open.bmp', False)
    )

    log.write('*' * 40)
    log.write('Part 2')
    for filename, delay in files:
        filename = f'./mazes/{filename}'
        log.write()
        log.write(f'File: {filename}')
        find_end(log, filename, delay)
    log.write('*' * 40)


def main():
    """ Do not change this function """
    sys.setrecursionlimit(5000)
    log = Log(show_terminal=True)
    find_ends(log)


if __name__ == "__main__":
    main()