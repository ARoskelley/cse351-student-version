"""
Course: CSE 351 
Assignment: 08 Prove Part 2
File:   prove_part_2.py
Author: Aiden Roskelley

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

Pass each thread the path it took to get to its starting square (a copy of the parent's
path list). As a thread moves, it appends each square to its own path. When a thread finds
the exit, it saves its path into a shared global (under the lock) before setting stop.
After all threads are joined, the main thread draws that saved path in a single color.

Why would it work?

Every square is claimed by exactly one thread, and each thread's path is the parent's path
up to the fork plus the squares it walked, so the path held by the thread that reaches the
exit is a connected route from start to end. Because each thread has its own copy, threads
never interfere with each other's paths, and only the winning thread writes the shared result.

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


# Protects the maze squares and the shared globals (stop, thread_count, colors)
lock = threading.Lock()


def _explore(maze, row, col, color):
    """ Recursively explore from (row, col). At a fork, this thread takes the
        first path and starts a new thread (with a new color) for each other path. """
    global stop
    global thread_count

    if stop:
        return

    # Check-and-move must be atomic so two threads never claim the same square
    with lock:
        if stop or not maze.can_move_here(row, col):
            return
        maze.move(row, col, color)

    # Base case: found the exit, tell every thread to stop
    if maze.at_end(row, col):
        stop = True
        return

    moves = maze.get_possible_moves(row, col)
    if not moves:
        return

    # Spin off a new thread for every path except the first
    children = []
    for next_row, next_col in moves[1:]:
        with lock:
            new_color = get_color()
            thread_count += 1
        t = threading.Thread(target=_explore, args=(maze, next_row, next_col, new_color))
        t.start()
        children.append(t)

    # This thread keeps going down the first path with the same color
    _explore(maze, moves[0][0], moves[0][1], color)

    # Wait for the threads this one created (after doing our own work,
    # so everything runs concurrently)
    for t in children:
        t.join()


def solve_find_end(maze):
    """ Finds the end position using threads. Nothing is returned. """
    # When one of the threads finds the end position, stop all of them.
    global stop
    global thread_count
    stop = False
    thread_count = 0

    start_row, start_col = maze.get_start_pos()
    with lock:
        color = get_color()
        thread_count += 1
    first = threading.Thread(target=_explore, args=(maze, start_row, start_col, color))
    first.start()
    first.join()




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