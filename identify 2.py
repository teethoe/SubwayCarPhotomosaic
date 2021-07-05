import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from sklearn.cluster import KMeans
from collections import Counter

'''
https://towardsdatascience.com/color-identification-in-images-machine-learning-application-b26e770c4c71
'''


def bgr2hex(colour):
    return "#{:02x}{:02x}{:02x}".format(int(colour[2]), int(colour[1]), int(colour[0]))


def rgb2hex(colour):
    return "#{:02x}{:02x}{:02x}".format(int(colour[0]), int(colour[1]), int(colour[2]))


def normalise_hsv(arr):
    for i in range(len(arr)):
        arr[i][0] *= (1/180)
        for j in range(2):
            arr[i][j+1] *= (1/255)
    return arr


def denormalise_rgb(arr):
    for i in range(len(arr)):
        for j in range(3):
            arr[i][j] *= 255
    return arr


class Identify:
    def __init__(self, img):
        self.img = img
        self.hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        self.hsv_colours = [[0 for i in range(3)] for j in range(4)]
        self.counts = Counter()
        self.colour_pos = [[0 for i in range(3)] for j in range(4)]  # n, e, s, w

    def get_colours(self):
        h, w = self.img.shape[:2]
        sampling_area = [[w/2-10, 15], [w-15, h/2-10], [w/2-10, h-15], [15, h/2-10]]
        removed = False
        mod = self.hsv.reshape(self.hsv.shape[0] * self.hsv.shape[1], 3)

        clf = KMeans(n_clusters=5)
        labels = clf.fit_predict(mod)
        counts = Counter(labels)

        del counts[counts.most_common()[0][0]]
        og_len = len(counts)
        counts = Counter({x: count for x, count in counts.items() if count >= 0.1 * sum(counts.values())})
        if len(counts) < og_len:
            removed = True
        center_colours = clf.cluster_centers_
        hsv_colours = [center_colours[i] for i in counts.keys()]
        i = 0
        while not removed and i < og_len:
            if float(hsv_colours[i][1]) < 50.0:
                hsv_colours.pop(i)
                del counts[list(counts.keys())[i]]
                removed = True
            i += 1
        for i in range(len(self.hsv_colours)):
            print(self.hsv_colours[i])
        self.hsv_colours = hsv_colours
        self.counts = counts

    def get_position(self):
        self.get_colours()
        range = 5
        kernel = np.ones((7, 7), np.uint8)
        for colour in self.hsv_colours:
            lowerb = np.array([(colour[0]-range+180)%180, colour[1]-10, colour[2]-10])
            upperb = np.array([(colour[0]+range)%180, colour[1]+30, colour[2]+30])
            if lowerb[0] < upperb[0]:
                mask = cv2.inRange(self.hsv, lowerb, upperb)
            else:
                upperb1 = upperb.copy()
                upperb1[0] = 180
                lowerb2 = lowerb.copy()
                lowerb2[0] = 0
                mask1 = cv2.inRange(self.hsv, lowerb, upperb1)
                mask2 = cv2.inRange(self.hsv, lowerb2, upperb)
                mask = mask1 + mask2

            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            '''cv2.imshow('mask', mask)
            cv2.waitKey(0)'''
            cnts, hierarchy = cv2.findContours(mask, 1, 2)
            # mask = cv2.drawContours(mask, cnts, -1, (0, 255, 0), 3)
            M = cv2.moments(cnts[0])
            center = [int(M['m10']/M['m00']), int(M['m01']/M['m00'])]  # x, y
            print(center)

            h, w = mask.shape[:2]
            if center[0] < 0.25*w:
                self.colour_pos[3] = colour
            elif center[0] > 0.75*w:
                self.colour_pos[1] = colour
            else:
                print(len(self.hsv_colours))
                if len(self.hsv_colours) == 3:
                    self.colour_pos[0] = colour
                else:
                    if center[1] < 0.25*h:
                        self.colour_pos[0] = colour
                    else:
                        self.colour_pos[2] = colour
        return self.colour_pos

    def pie(self):
        self.get_colours()
        '''norm_hsv = normalise_hsv(self.hsv_colours)
        rgb_colours = [hsv_to_rgb(norm_hsv[i]) for i in range(len(norm_hsv))]
        rgb_colours = denormalise_rgb(rgb_colours)
        hex_colours = [rgb2hex(rgb_colours[i]) for i in range(len(norm_hsv))]'''
        hex_colours = [bgr2hex(self.hsv_colours[i]) for i in range(len(self.hsv_colours))]

        plt.figure(figsize=(8, 6))
        plt.pie(self.counts.values(), labels=hex_colours, colors=hex_colours)
        plt.show()