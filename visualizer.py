"""Python script for visualizing caps generated in one of the search methods in this library. 

Jaron Wang"""
import numpy as np 
import pickle
import sys
import csv
import cv2
import os
from affine_space_core import vector_to_index


""" Draws the 2-dimensional grid onto frame using the top left corner p1 and bottom right corner p2"""
def draw_grid_full(frame, p1, p2, q, padding):
    x1, y1 = p1
    x2, y2 = p2
    box_width = (x2 - x1) // q - padding 
    sub_boxes = []
    # Draw vertical lines
    for i in range(1, q):
        x = x1 + (box_width + padding) * i - padding // 3
        cv2.line(frame, (x, y1), (x, y1 + (box_width + padding) * q), (0,0,0), thickness= padding // 3)
    
    # Draw horizontal lines
    for j in range(1, q):
        y = y1 + (box_width + padding) * j  - padding // 3
        cv2.line(frame, (x1, y), ((x1 + (box_width + padding) * q), y), (0,0,0), thickness= padding // 3)

    for i in range(q):
        for j in range(q):
            sub_boxes.append(((x1 + i * (box_width + padding) + padding // 2 , y1 + j * (box_width + padding) + padding // 2) , 
                             (x1 + i * (box_width + padding) + box_width, y1 + j * (box_width + padding) + box_width)))

    return sub_boxes

""" Draws the wide grid starting at x1, y1 and returns the the top left corner of the sub-boxes."""
def draw_grid_wide(frame, p1, p2, q, padding):
    x1, y1 = p1
    x2, y2 = p2
    box_width = (x2 - x1) // q - padding
    sub_boxes = []
    sub_boxes.append(((x1+ padding // 2, y1 + padding // 2), (x1 + box_width, y1 + box_width)))
    for i in range(1, q):
        x = x1 + (box_width + padding) * i 
        cv2.line(frame, (x, y1), (x, y1 + box_width), (0,0,0), thickness= padding // 3)
        sub_boxes.append(((x + padding // 2, y1 + padding // 2), (x + box_width, y1 + box_width)))
    return sub_boxes

""" Draws the grid and returns the necessary params of the sub-boxes."""
def draw_grid(frame, q, n, padding):
    height, width, _ = frame.shape
    if n % 2 == 1:
        n -= 1
        sub_boxes = draw_grid_wide(canvas_img, (0,0), (width, height), q, padding)
        padding = padding // 3
    else:
        sub_boxes = [((0,0), (width, height))]

    while n > 0:
        new_sub_boxes = []
        for p1, p2 in sub_boxes:
            new_sub_boxes += draw_grid_full(canvas_img, p1, p2, q, padding)
        n -=2
        padding = padding // 3
        sub_boxes = new_sub_boxes
    
    return sub_boxes


""" Marks the given box with an X"""
def mark_box(frame, sub_boxes, point, q, n):
    idx = vector_to_index(point, q, n)
    p1, p2 = sub_boxes[idx]
    x1, y1 = p1
    x2, y2 = p2
    cv2.line(frame, p1, p2, color = (255,0,0), thickness=2)
    cv2.line(frame, (x1, y2), (x2, y1), color = (255,0,0), thickness=2)

if __name__ == '__main__':
    if len(sys.argv) == 4:
        d = int(sys.argv[1])
        q = int(sys.argv[2])
        n = int(sys.argv[3])
    else: 
        d = 3
        q = 3
        n = 3

    std_width = 4096
    padding = q ** n
    width = std_width
    height = std_width if n % 2 == 0 else int(std_width / 3)
    output = os.path.join(os.getcwd(), 'result.png')

    if __debug__:
        cap_path = os.path.join(os.path.join(os.getcwd(), 'results'), str(d) + '_' + str(q) + '_' + str(n) + '.dat')

        with open(cap_path, 'rb') as f:
            cap = pickle.load(f)
        canvas_img = np.zeros((height,  width , 3), np.uint8)
        canvas_img.fill(255)
        
        sub_boxes = draw_grid(canvas_img, q, n , padding)
        for point in cap:
            mark_box(canvas_img, sub_boxes, point, q, n)
        cv2.imwrite(output, canvas_img)
    else:
        cap_path = os.path.join(os.path.join(os.getcwd(), 'results'), str(d) + '_' + str(q) + '_' + str(n) + '_all.dat')

        with open(cap_path, 'rb') as f:
            caps = pickle.load(f)

        folder = os.path.join(os.path.join(os.getcwd(), 'imgs'), str(d) + '_' + str(q) + '_' + str(n)) 
        try:
            os.mkdir(folder)
        except FileExistsError:
            pass
        for i, cap in enumerate(caps):
            canvas_img = np.zeros((height,  width , 3), np.uint8)
            canvas_img.fill(255)
            
            sub_boxes = draw_grid(canvas_img, q, n, padding)
            for point in cap:
                mark_box(canvas_img, sub_boxes, point, q, n)
           
            output = os.path.join(folder, str(i) + '.png')
            cv2.imwrite(output, canvas_img)
            
        


    



    
