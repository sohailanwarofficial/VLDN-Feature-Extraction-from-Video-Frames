import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

import time
start_time = time.time()

csvfile = open("VLDNFeatures.csv", "w")

for video_id in range(1, 301):
    Final_vldn = np.zeros((71, 1), np.uint8)
    print(video_id)
    vldn_id = 0
    for frame_id in range(0, 6):  # Modify the range to process 6 frames per video
        file_vldn = "frames/" + str(video_id) + "_" + str(frame_id) + ".jpg"
        vldn_id = vldn_id + 1

        frame_vldn = cv2.imread(file_vldn)

        frame_vldn_gray = cv2.cvtColor(frame_vldn, cv2.COLOR_BGR2GRAY)
        frame_vldn_gray = cv2.resize(frame_vldn_gray, (224, 224), interpolation=cv2.INTER_AREA)

        height, width = frame_vldn_gray.shape

        # Kirsch Masks
        msk = np.zeros((8, 3, 3), np.int16)
        msk[0] = np.array([[-3, -3, 5], [-3, 0, 5], [-3, -3, 5]])  # east
        msk[1] = np.array([[-3, 5, 5], [-3, 0, 5], [-3, -3, -3]])  # north-east
        msk[2] = np.array([[5, 5, 5], [-3, 0, -3], [-3, -3, -3]])  # north
        msk[3] = np.array([[5, 5, -3], [5, 0, -3], [-3, -3, -3]])  # north-west
        msk[4] = np.array([[5, -3, -3], [5, 0, -3], [5, -3, -3]])  # west
        msk[5] = np.array([[-3, -3, -3], [5, 0, -3], [5, 5, -3]])  # south-west
        msk[6] = np.array([[-3, -3, -3], [-3, 0, -3], [5, 5, 5]])  # south
        msk[7] = np.array([[-3, -3, -3], [-3, 0, 5], [-3, 5, 5]])  # south-east

        # LDN Calculation
        for i in range(0, height - 2):
            for j in range(0, width - 2):
                p = frame_vldn_gray[i:i + 3, j:j + 3]

                z = np.sum(np.multiply(p, msk), axis=(1, 2)).reshape(-1, 1)
                z3 = np.concatenate((z, z, z), axis=0)

                # First:
                z2 = np.zeros((8, 1), np.int16)
                q = np.argsort(z, axis=0)
                g = 7

                z2[q[:g]] = 0
                z2[q[g:]] = 1

                # Third:
                qqq2 = np.argsort(z3, axis=0)
                qqq2[(qqq2 > 7) & (qqq2 < 16)] -= 8
                qqq2[qqq2 >= 16] -= 16

                low_index = qqq2[0]
                high_index = qqq2[23]

                # Fourth:
                zzz22 = np.zeros((8, 1), np.int16)
                zzz22[low_index] = 1
                zzz22[high_index] = 1

                # Decimal to Binary conversion:
                b = np.sum(z2 * (2 ** np.arange(7, -1, -1)))

                # VLDN:
                vldn_value = high_index * 8 + low_index

                Final_vldn[vldn_value] += 1

        print("VLDN frame number:", frame_id)
        print("--- %s seconds elapsed ---" % (time.time() - start_time))

    temp = 0
    for feature in Final_vldn[0:71, 0]:
        if temp < 71:
            csvfile.write(str(feature) + ",")
            temp = temp + 1

    csvfile.write("\n")

csvfile.flush()
csvfile.close()
