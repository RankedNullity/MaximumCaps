import csv
import cv2
import os
import numpy as np
import multiprocessing
from multiprocessing import Pool
from functools import partial
import time
import sys
sys.path.append('baseline-detector')
from baseline_detector import BaselineDetector
import constant_array
''' Script for calculating the mAP of a certain classifier.
    Expected output and label format is (class, (xmin, ymin, xmax, ymax))

    Jaron Wang
'''
def draw_boxes(labels, frame, color):
    h, w, c = frame.shape
    thickness = 4 if (255, 0, 255) == color else 2
    #print("image: {}".format(frame.shape))

    for C, BB in labels:
        x1, y1, x2, y2 = BB
        x1 = int(x1 * w)
        x2 = int(x2 * w)
        y1 = int(y1 * h)
        y2 = int(y2 * h)
        #print("({}, ({}, {}, {},{}))".format(C, x1, y1, x2, y2))
        #print("Points: ({}, {}) , ({}, {})")
        cv2.line(frame, (x1, y1), (x1, y2), color, thickness)
        cv2.line(frame, (x1, y1), (x2, y1), color, thickness)
        cv2.line(frame, (x2, y1), (x2, y2), color, thickness)
        cv2.line(frame, (x1, y2), (x2, y2), color, thickness)

def compare_boxes(classifier1, classifier2, folder, csv_path):
    # classifier : function which takes an input img path and returns a list with (label, bounding box) in DESC order
    #     folder : path which is the directory which contains all the img files in the csv
    #   csv_path : path to the csv files which contains the true labels
    test_set = {}
    with open(csv_path) as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        csv_reader.__next__()
        for row in csv_reader:
            img =  row[0]
            if img not in test_set.keys():
                test_set[img] = []
            if len(row) >= 6:
                test_set[img].append((int(row[1]), (float(row[2]), float(row[3]), float(row[4]), float(row[5]))))

    iou_thresh = np.linspace(0, 0.95, 20)
    APk = []     
    #print("Finished loading from csv")

    for img in test_set.keys():
        print("Img: {}".format(img))
        frame = cv2.imread(os.path.join(folder , img))
        # List of prediction bounding boxes
        y_pred1 = classifier1(os.path.join(folder , img))
        y_pred2 = classifier2(os.path.join(folder, img))
        # List of label boundign boxes
        y_actual = test_set[img]
        print("y_pred1: {} \ny_pred2: {}\ny_actual: {}".format(y_pred1, y_pred2, y_actual))
        draw_boxes(y_actual, frame, (51, 153, 51)) # green
        draw_boxes(y_pred1, frame, (255, 0, 255)) # pink
        draw_boxes(y_pred2, frame, (0, 154, 255)) # orange
        cv2.imwrite(os.path.join(os.path.join(os.getcwd(), 'comparison'), img) , frame)

if __name__ == '__main__':
    # Put your classifier and labels here
    
    folder = os.path.join(os.getcwd(), "image_data")
    test_csv = os.path.join(os.getcwd(), "test.csv")
    # End
    import genetic_train
    classifier1 = genetic_train.get_baseline_classifier(constant_array.HARDCODE_CONST)
    classifier2 = genetic_train.get_baseline_classifier(constant_array.DEFAULT_CONST)
    compare_boxes(classifier1, classifier2, folder, test_csv)
