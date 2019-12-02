import numpy as np 
import pickle
import sys
import csv
import cv2
import os

def draw_grid_full(frame, p1, p2, q, padding):
    x1, y1 = p1
    x2, y2 = p2
    box_width = (x2 - x1) // q - padding 
    sub_boxes = []
    cv2.imshow("pre", frame)
    cv2.waitKey(0)
    # Draw vertical lines
    for i in range(1, q):
        x = x1 + box_width * i + padding // 2
        cv2.line(frame, (x, y1), (x, y1 + (box_width + padding) * q), (0,0,0), thickness= padding // 3)
        cv2.imshow("pre", frame)
        cv2.waitKey(0)
    
    # Draw horizontal lines
    for j in range(1, q):
        y = y1 + box_width * j + padding // 2
        cv2.line(frame, (x1, y), ((x1 + (box_width + padding) * q), y), (0,0,0), thickness= padding // 3)
        cv2.imshow("pre", frame)
        cv2.waitKey(0)

    for i in range(q):
        for j in range(q):
            sub_boxes.append((x1 + i * (box_width + padding) , y1 + j * (box_width + padding), 
                             (x1 + i * (box_width + padding) + box_width, y1 + j * (box_width + padding) + box_width)))

    return sub_boxes

# Draws the wide grid starting at x1, y1 and returns the the top left corner of the sub-boxes.
def draw_grid_wide(frame, p1, p2, q, padding):
    x1, y1 = p1
    x2, y2 = p2
    box_width = y2 - y1
    sub_boxes = []
    sub_boxes.append(((x1, y1), (x1 + box_width, y1 + box_width)))
    for i in range(1, q):
        x = x1 + box_width * i + padding // 2
        cv2.line(frame, (x, y1), (x, y1 + box_width), (0,0,0), thickness= padding // 3)
        sub_boxes.append(((x + padding // 2, y1), (x + padding // 2 + box_width, y1 + box_width)))
    return sub_boxes

if __name__ == '__main__':
    if len(sys.argv) == 4:
        d = sys.argv[1]
        q = sys.argv[2]
        n = sys.argv[3]
    else: 
        d = 2
        q = 3
        n = 4
    cap_path = os.path.join(os.path.join(os.getcwd(), 'results'), str(d) + '_' + str(q) + '_' + str(n) + '.dat')

    with open(cap_path, 'rb') as f:
        cap = pickle.load(f)

    std_width = 80
    padding = 27
    width = (std_width + padding) * q ** ((n+1) // 2)
    height = (std_width + padding) * q ** (n // 2)
    output = os.path.join(os.getcwd(), 'test.png')

    
    print("width, height : {} , {}".format(width, height))

    canvas_img = np.zeros((height,  width , 3), np.uint8)
    canvas_img.fill(255)

    if n % 2 == 1:
        n -= 1
        sub_boxes = draw_grid_wide(canvas_img, (0,0), (width, height), q, padding)
    else:
        sub_boxes = [((0,0), (width, height))]

    while n > 0:
        new_sub_boxes = []
        for p1, p2 in sub_boxes:
            new_sub_boxes.append(draw_grid_full(canvas_img, p1, p2, q, padding))
        n -=2
        padding = padding // 3
        sub_boxes = new_sub_boxes

    cv2.imwrite(output, canvas_img)



    
