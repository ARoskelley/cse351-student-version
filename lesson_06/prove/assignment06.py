"""
Course: CSE 351
Assignment: 06
Author: Aiden Roskelley

Instructions:

- see instructions in the assignment description in Canvas

""" 

import multiprocessing as mp
import os
import cv2
import numpy as np

from cse351 import *

# Folders
INPUT_FOLDER = "faces"
STEP1_OUTPUT_FOLDER = "step1_smoothed"
STEP2_OUTPUT_FOLDER = "step2_grayscale"
STEP3_OUTPUT_FOLDER = "step3_edges"

# Parameters for image processing
GAUSSIAN_BLUR_KERNEL_SIZE = (5, 5)
CANNY_THRESHOLD1 = 75
CANNY_THRESHOLD2 = 155

# Allowed image extensions
ALLOWED_EXTENSIONS = ['.jpg']

# Number of processes for each stage of the pipeline
SMOOTH_PROCESSES = 4
GRAYSCALE_PROCESSES = 2
EDGE_PROCESSES = 4

# Message placed on a queue to tell a worker there is no more work
ALL_DONE = None

# ---------------------------------------------------------------------------
def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created folder: {folder_path}")

# ---------------------------------------------------------------------------
def task_convert_to_grayscale(image):
    if len(image.shape) == 2 or (len(image.shape) == 3 and image.shape[2] == 1):
        return image # Already grayscale
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# ---------------------------------------------------------------------------
def task_smooth_image(image, kernel_size):
    return cv2.GaussianBlur(image, kernel_size, 0)

# ---------------------------------------------------------------------------
def task_detect_edges(image, threshold1, threshold2):
    if len(image.shape) == 3 and image.shape[2] == 3:
        print("Warning: Applying Canny to a 3-channel image. Converting to grayscale first for Canny.")
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif len(image.shape) == 3 and image.shape[2] != 1 : # Should not happen with typical images
        print(f"Warning: Input image for Canny has an unexpected number of channels: {image.shape[2]}")
        return image # Or raise error
    return cv2.Canny(image, threshold1, threshold2)

# ---------------------------------------------------------------------------
def smooth_worker(que_in, que_out, barrier, next_stage_count):
    """ Stage 1: read an original image from disk and smooth it.
        que_in  items: filename
        que_out items: (filename, smoothed image) """
    while True:
        filename = que_in.get()
        if filename is ALL_DONE:
            break

        input_image_path = os.path.join(INPUT_FOLDER, filename)
        try:
            img = cv2.imread(input_image_path)
            if img is None:
                print(f"Warning: Could not read image '{input_image_path}'. Skipping.")
                continue
            que_out.put((filename, task_smooth_image(img, GAUSSIAN_BLUR_KERNEL_SIZE)))
        except Exception as e:
            print(f"Error smoothing file '{input_image_path}': {e}")

    if barrier.wait() == 0:
        for _ in range(next_stage_count):
            que_out.put(ALL_DONE)

# ---------------------------------------------------------------------------
def grayscale_worker(que_in, que_out, barrier, next_stage_count):
    """ Stage 2: convert a smoothed image to grayscale.
        que_in  items: (filename, smoothed image)
        que_out items: (filename, grayscale image) """
    while True:
        item = que_in.get()
        if item is ALL_DONE:
            break

        filename, img = item
        try:
            que_out.put((filename, task_convert_to_grayscale(img)))
        except Exception as e:
            print(f"Error converting file '{filename}' to grayscale: {e}")

    if barrier.wait() == 0:
        for _ in range(next_stage_count):
            que_out.put(ALL_DONE)

# ---------------------------------------------------------------------------
def edge_worker(que_in):
    """ Stage 3: detect edges and save the final image to STEP3_OUTPUT_FOLDER.
        que_in items: (filename, grayscale image) """
    while True:
        item = que_in.get()
        if item is ALL_DONE:
            break

        filename, img = item
        output_image_path = os.path.join(STEP3_OUTPUT_FOLDER, filename) # Keep original filename
        try:
            edges = task_detect_edges(img, CANNY_THRESHOLD1, CANNY_THRESHOLD2)
            cv2.imwrite(output_image_path, edges)
        except Exception as e:
            print(f"Error detecting edges for file '{filename}': {e}")

# ---------------------------------------------------------------------------
def run_image_processing_pipeline(log):
    print("Starting image processing pipeline...")

    create_folder_if_not_exists(STEP3_OUTPUT_FOLDER)

    que1 = mp.Queue()   
    que2 = mp.Queue()   
    que3 = mp.Queue()   

    smooth_barrier = mp.Barrier(SMOOTH_PROCESSES)
    grayscale_barrier = mp.Barrier(GRAYSCALE_PROCESSES)

    smoothers = [mp.Process(target=smooth_worker,
                            args=(que1, que2, smooth_barrier, GRAYSCALE_PROCESSES))
                 for _ in range(SMOOTH_PROCESSES)]
    grayscalers = [mp.Process(target=grayscale_worker,
                              args=(que2, que3, grayscale_barrier, EDGE_PROCESSES))
                   for _ in range(GRAYSCALE_PROCESSES)]
    edge_detectors = [mp.Process(target=edge_worker, args=(que3,))
                      for _ in range(EDGE_PROCESSES)]

    all_processes = smoothers + grayscalers + edge_detectors
    for p in all_processes:
        p.start()

    image_count = 0
    for filename in os.listdir(INPUT_FOLDER):
        if os.path.splitext(filename)[1].lower() in ALLOWED_EXTENSIONS:
            que1.put(filename)
            image_count += 1

    for _ in range(SMOOTH_PROCESSES):
        que1.put(ALL_DONE)

    for p in all_processes:
        p.join()

    for que in (que1, que2, que3):
        que.close()

    output_count = len(os.listdir(STEP3_OUTPUT_FOLDER))
    log.write(f'Processes: smooth={SMOOTH_PROCESSES}, grayscale={GRAYSCALE_PROCESSES}, edge={EDGE_PROCESSES}')
    log.write(f'{image_count} images sent into the pipeline')
    log.write(f'{output_count} images in {STEP3_OUTPUT_FOLDER}')

    print("\nImage processing pipeline finished!")
    print(f"Original images are in: '{INPUT_FOLDER}'")
    print(f"Edge images are in: '{STEP3_OUTPUT_FOLDER}'")


# ---------------------------------------------------------------------------
if __name__ == "__main__":
    log = Log(show_terminal=True)
    log.start_timer('Processing Images')

    # check for input folder
    if not os.path.isdir(INPUT_FOLDER):
        print(f"Error: The input folder '{INPUT_FOLDER}' was not found.")
        print(f"Create it and place your face images inside it.")
        print('Link to faces.zip:')
        print('   https://drive.google.com/file/d/1eebhLE51axpLZoU6s_Shtw1QNcXqtyHM/view?usp=sharing')
    else:
        run_image_processing_pipeline(log)

    log.write()
    log.stop_timer('Total Time To complete')
