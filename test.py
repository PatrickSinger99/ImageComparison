import matplotlib.pyplot as plt
import os
import cv2
import time
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

pil_img = Image.open("E:\GitHub Repositories\ImageComparison\imgs\white_test (6).png")
print(pil_img)
img = np.array(pil_img)
print(img.shape)