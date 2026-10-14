""" 
Course: CSE 351
Team  : Week 04
File  : team.py
Author: <Student Name>

See instructions in canvas for this team activity.

"""

import random
import threading
import numpy

# Include CSE 351 common Python files. 
from cse351 import *

# Constants
MAX_QUEUE_SIZE = 10
PRIME_COUNT = 1000
FILENAME = 'primes.txt'
PRODUCERS = 3
CONSUMERS = 5

# ---------------------------------------------------------------------------
def is_prime(n: int):
    if n <= 3:
        return n > 1
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True

# ---------------------------------------------------------------------------
class Queue351():
    """ This is the queue object to use for this class. Do not modify!! """

    def __init__(self):
        self.__items = []
   
    def put(self, item):
        assert len(self.__items) <= 10
        self.__items.append(item)

    def get(self):
        return self.__items.pop(0)

    def get_size(self):
        """ Return the size of the queue like queue.Queue does -> Approx size """
        extra = 1 if random.randint(1, 50) == 1 else 0
        if extra > 0:
            extra *= -1 if random.randint(1, 2) == 1 else 1
        return len(self.__items) + extra

# ---------------------------------------------------------------------------
def producer(que,bar,sem_empty,sem_full):
    for i in range(PRIME_COUNT):
        number = random.randint(1, 1_000_000_000_000)
        # TODO - place on queue for workers
        sem_empty.acquire()  # Wait for empty slot
        que.put(number)
        sem_full.release()  # Signal that an item was added

    id = bar.wait()  # Wait for all producers to finish

    # TODO - select one producer to send the "All Done" message
    if id == 0:
        for i in range(CONSUMERS):
            sem_empty.acquire()
            que.put(None)  # Send "All Done" message to consumers
            sem_full.release()

# ---------------------------------------------------------------------------
def consumer(que,sem_empty,sem_full):
    # TODO - get values from the queue and check if they are prime
    sem_full.acquire()
    number = que.get()
    sem_empty.release()
    # TODO - if prime, write to the file
    if is_prime(number):
        with open(FILENAME, 'a') as f:
            f.write(f"{number}\n")
        print(f"Found prime: {number}")
    # TODO - if "All Done" message, exit the loop
    if number is None:
        return

# ---------------------------------------------------------------------------
def main():

    random.seed(102030)

    que = Queue351()

    # TODO - create semaphores for the queue (see Queue351 class)
    sem_empty = threading.Semaphore(MAX_QUEUE_SIZE)
    sem_full = threading.Semaphore(0)

    # TODO - create barrier
    bar = threading.Barrier(PRODUCERS + CONSUMERS)

    # TODO - create producers threads (see PRODUCERS value)
    pros = [ threading.Thread(target=producer, args=(que,bar,sem_empty,sem_full)) for id in range(PRODUCERS) ]
    # TODO - create consumers threads (see CONSUMERS value)
    cons = [ threading.Thread(target=consumer, args=(que,sem_empty,sem_full)) for id in range(CONSUMERS) ]

    for p in pros:
        p.start()
    for c in cons:
        c.start()

    for p in pros:
        p.join()
    for c in cons:
        c.join()

    if os.path.exists(FILENAME):
        with open(FILENAME, 'r') as f:
            primes = len(f.readlines())
    else:
        primes = 0
    print(f"Found {primes} primes. Must be 108 found.")



if __name__ == '__main__':
    main()
