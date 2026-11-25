"""
Course: CSE 351, week 10
File: functions.py
Author: <your name>

Instructions:

Depth First Search
https://www.youtube.com/watch?v=9RHO6jU--GU

Breadth First Search
https://www.youtube.com/watch?v=86g8jAQug04


Requesting a family from the server:
family_id = 6128784944
data = get_data_from_server('{TOP_API_URL}/family/{family_id}')

Example JSON returned from the server
{
    'id': 6128784944, 
    'husband_id': 2367673859,        # use with the Person API
    'wife_id': 2373686152,           # use with the Person API
    'children': [2380738417, 2185423094, 2192483455]    # use with the Person API
}

Requesting an individual from the server:
person_id = 2373686152
data = get_data_from_server('{TOP_API_URL}/person/{person_id}')

Example JSON returned from the server
{
    'id': 2373686152, 
    'name': 'Stella', 
    'birth': '9-3-1846', 
    'parent_id': 5428641880,   # use with the Family API
    'family_id': 6128784944    # use with the Family API
}


--------------------------------------------------------------------------------------
You will lose 10% if you don't detail your part 1 and part 2 code below

Describe how to speed up part 1

Part 1 uses a recursive depth-first traversal.  A thread pool retrieves the
family and all of the people in that family concurrently with other family
branches.  A shared visited set prevents the same family from being added or
retrieved more than once.


Describe how to speed up part 2

Part 2 uses a queue for breadth-first traversal.  Each level is submitted to
a thread pool, and the next level is processed only after every family at the
current level finishes.  This overlap keeps the server requests concurrent
without using recursion.


Extra (Optional) 10% Bonus to speed up part 3

Part 3 uses the breadth-first queue, but limits the thread pool to five so
the server never has more than five active requests.

"""
from common import *
import queue
import threading
from concurrent.futures import ThreadPoolExecutor


def _fetch_family(family_id, person_workers=1):
    family_data = get_data_from_server(f'{TOP_API_URL}/family/{family_id}')
    if family_data is None:
        return None

    family = Family(family_data)
    people = []

    person_ids = []
    husband_id = family.get_husband()
    wife_id = family.get_wife()
    if husband_id is not None:
        person_ids.append(husband_id)
    if wife_id is not None:
        person_ids.append(wife_id)
    for child_id in family.get_children():
        if child_id is not None:
            person_ids.append(child_id)

    if person_workers == 1:
        for person_id in person_ids:
            person_data = get_data_from_server(f'{TOP_API_URL}/person/{person_id}')
            if person_data is not None:
                people.append(Person(person_data))
    else:
        def fetch_person(person_id):
            person_data = get_data_from_server(f'{TOP_API_URL}/person/{person_id}')
            if person_data is None:
                return None
            return Person(person_data)

        with ThreadPoolExecutor(max_workers=person_workers) as person_executor:
            fetched_people = person_executor.map(fetch_person, person_ids)
            for person in fetched_people:
                if person is not None:
                    people.append(person)

    parent_ids = []
    for person in people:
        parent_id = person.get_parentid()
        if parent_id is not None:
            parent_ids.append(parent_id)

    return family, people, parent_ids


def _add_family_to_tree(tree, fetched):
    if fetched is None:
        return []

    family, people, parent_ids = fetched
    tree.add_family(family)
    for person in people:
        tree.add_person(person)
    return parent_ids


def _fetch_family_parallel(family_id):
    return _fetch_family(family_id, person_workers=8)

# -----------------------------------------------------------------------------
def depth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    visited = set()
    visited_lock = threading.Lock()

    def retrieve_recursive(current_family_id):
        with visited_lock:
            if current_family_id in visited:
                return
            visited.add(current_family_id)

        fetched = _fetch_family_parallel(current_family_id)
        parent_ids = _add_family_to_tree(tree, fetched)

        child_futures = []
        for parent_id in parent_ids:
            child_futures.append(executor.submit(retrieve_recursive, parent_id))
        for child_future in child_futures:
            child_future.result()

    with ThreadPoolExecutor(max_workers=64) as executor:
        executor.submit(retrieve_recursive, family_id).result()

# -----------------------------------------------------------------------------
def breadth_fs_pedigree(family_id, tree):
    # KEEP this function even if you don't implement it
    current_level = [family_id]
    visited = set()

    with ThreadPoolExecutor(max_workers=64) as executor:
        while current_level:
            next_level = []
            unseen = []
            for current_family_id in current_level:
                if current_family_id not in visited:
                    visited.add(current_family_id)
                    unseen.append(current_family_id)

            fetched_families = executor.map(_fetch_family_parallel, unseen)
            for fetched in fetched_families:
                parent_ids = _add_family_to_tree(tree, fetched)
                for parent_id in parent_ids:
                    if parent_id not in visited:
                        next_level.append(parent_id)

            current_level = next_level


# -----------------------------------------------------------------------------
def breadth_fs_pedigree_limit5(family_id, tree):
    # KEEP this function even if you don't implement it
    current_level = [family_id]
    visited = set()

    with ThreadPoolExecutor(max_workers=5) as executor:
        while current_level:
            next_level = []
            unseen = []
            for current_family_id in current_level:
                if current_family_id not in visited:
                    visited.add(current_family_id)
                    unseen.append(current_family_id)

            fetched_families = executor.map(_fetch_family, unseen)
            for fetched in fetched_families:
                parent_ids = _add_family_to_tree(tree, fetched)
                for parent_id in parent_ids:
                    if parent_id not in visited:
                        next_level.append(parent_id)

            current_level = next_level