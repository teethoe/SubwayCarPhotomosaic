import cv2
import numpy as np
import matplotlib.pyplot as plt
from functions import stitch
from process import Process
from identify import Identify


fixed = [0 for i in range(5)]
colour_pos = [0 for i in range(5)]
ordered = [0 for i in range(5)]

for i in range(5):
    img = cv2.imread('./img/samples/official/sample 3/{}.png'.format(i+1))
    img = Process(img).fix()
    fixed[i] = img
    # img = cv2.resize(img, (100, 100), interpolation=cv2.INTER_AREA)

    x = Identify(img)
    x.pie()

    colour_pos[i] = x.get_position()

found = False
i = 0
while i < 5:
    n = sum(x != [0, 0, 0] for x in colour_pos[i])[0]
    if n == 4:
        side = i
        ordered[0] = fixed[i]
        found = True
    i += 1


for i in range(1, 5):
    acol = colour_pos[side][4-i][:2]
    val = colour_pos[side][4-i][0]
    for j in range(5):
        if j != side:
            bcol = colour_pos[j][0][:2]
            # if val-6 <= colour_pos[j][0][0] <= val+6:
            dist1 = np.linalg.norm(acol[0] - bcol[0])
            dist2 = np.linalg.norm(acol - bcol)
            print(dist2, acol, bcol)
            if dist2 <= 30 and dist1 <= 6:
                ordered[i] = fixed[j]


mosaic = stitch(ordered)
mosaic = cv2.cvtColor(mosaic, cv2.COLOR_BGR2RGB)

# cv2.imshow('stitch', mosaic)

plt.imshow(mosaic)
plt.show()
cv2.waitKey(0)
cv2.destroyAllWindows()
