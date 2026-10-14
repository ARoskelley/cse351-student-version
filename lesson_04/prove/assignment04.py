"""
Course    : CSE 351
Assignment: 04
Student   : <your name here>

Instructions:
    - review instructions in the course

In order to retrieve a weather record from the server, Use the URL:

f'{TOP_API_URL}/record/{name}/{recno}

where:

name: name of the city
recno: record number starting from 0

"""

import time
from common import *

from cse351 import *

THREADS = 150               # Threads retrieving records from the server
WORKERS = 10                # Threads storing records into the NOAA object
RECORDS_TO_RETRIEVE = 5000  # Don't change
MAX_QUEUE_SIZE = 10         # Queue351 asserts it never holds more than this


# ---------------------------------------------------------------------------
def retrieve_weather_data(command_que, command_empty, command_full,
                          data_que, data_empty, data_full):
    while True:
        command_full.acquire()
        command = command_que.get()
        command_empty.release()

        # "All Done" message
        if command is None:
            break

        city, recno = command
        record = get_data_from_server(f'{TOP_API_URL}/record/{city}/{recno}')

        data_empty.acquire()
        data_que.put((city, record['date'], record['temp']))
        data_full.release()


# ---------------------------------------------------------------------------
class Worker(threading.Thread):

    def __init__(self, noaa, data_que, data_empty, data_full):
        super().__init__()
        self.noaa = noaa
        self.data_que = data_que
        self.data_empty = data_empty
        self.data_full = data_full

    def run(self):
        while True:
            self.data_full.acquire()
            data = self.data_que.get()
            self.data_empty.release()

            # "All Done" message
            if data is None:
                break

            city, date, temp = data
            self.noaa.store(city, date, temp)


# ---------------------------------------------------------------------------
class NOAA:

    def __init__(self):
        self.lock = threading.Lock()
        self.temps = {name: [] for name in CITIES}

    def store(self, city, date, temp):
        with self.lock:
            self.temps[city].append(temp)

    def get_temp_details(self, city):
        with self.lock:
            temps = self.temps[city]
            if len(temps) == 0:
                return 0.0
            return round(sum(temps) / len(temps), 4)


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
def verify_noaa_results(noaa):

    answers = {
        'sandiego': 14.5004,
        'philadelphia': 14.865,
        'san_antonio': 14.638,
        'san_jose': 14.5756,
        'new_york': 14.6472,
        'houston': 14.591,
        'dallas': 14.835,
        'chicago': 14.6584,
        'los_angeles': 15.2346,
        'phoenix': 12.4404,
    }

    print()
    print('NOAA Results: Verifying Results')
    print('===================================')
    for name in CITIES:
        answer = answers[name]
        avg = noaa.get_temp_details(name)

        if abs(avg - answer) > 0.00001:
            msg = f'FAILED  Expected {answer}'
        else:
            msg = f'PASSED'
        print(f'{name:>15}: {avg:<10} {msg}')
    print('===================================')


# ---------------------------------------------------------------------------
def main():

    log = Log(show_terminal=True, filename_log='assignment.log')
    log.start_timer()

    noaa = NOAA()

    # Start server
    data = get_data_from_server(f'{TOP_API_URL}/start')

    # Get all cities number of records
    print('Retrieving city details')
    city_details = {}
    name = 'City'
    print(f'{name:>15}: Records')
    print('===================================')
    for name in CITIES:
        city_details[name] = get_data_from_server(f'{TOP_API_URL}/city/{name}')
        print(f'{name:>15}: Records = {city_details[name]['records']:,}')
    print('===================================')

    records = RECORDS_TO_RETRIEVE

    command_que = Queue351()
    command_empty = threading.Semaphore(MAX_QUEUE_SIZE)
    command_full = threading.Semaphore(0)

    data_que = Queue351()
    data_empty = threading.Semaphore(MAX_QUEUE_SIZE)
    data_full = threading.Semaphore(0)

    retrievers = [threading.Thread(target=retrieve_weather_data,
                                   args=(command_que, command_empty, command_full,
                                         data_que, data_empty, data_full))
                  for _ in range(THREADS)]
    workers = [Worker(noaa, data_que, data_empty, data_full) for _ in range(WORKERS)]

    for t in retrievers + workers:
        t.start()

    for name in CITIES:
        for recno in range(records):
            command_empty.acquire()
            command_que.put((name, recno))
            command_full.release()

    # Tell the retrievers they are done
    for _ in range(THREADS):
        command_empty.acquire()
        command_que.put(None)
        command_full.release()

    for t in retrievers:
        t.join()

    # All records are on the data queue, tell the workers they are done
    for _ in range(WORKERS):
        data_empty.acquire()
        data_que.put(None)
        data_full.release()

    for t in workers:
        t.join()


    # End server - don't change below
    data = get_data_from_server(f'{TOP_API_URL}/end')
    print(data)

    verify_noaa_results(noaa)

    log.stop_timer('Run time: ')


if __name__ == '__main__':
    main()

