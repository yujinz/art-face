from skimage import io
import sys
import dlib
import cv2
import scipy.misc
import numpy as np
import matplotlib.pyplot as plt
from facial_landmark_detection import (resize, draw_and_write_landmark)
from moving_least_squares import (mls_affine_deformation, mls_affine_deformation_inv,
                       mls_similarity_deformation, mls_similarity_deformation_inv,
                       mls_rigid_deformation, mls_rigid_deformation_inv)



if len(sys.argv) != 3:
    print(
        "Usage:\n"
        "    ./facial_landmark_detection.py ./examples/art/01.jpg ./examples/target/01.jpg\n")
    exit()

predictor_path = "shape_predictor_68_face_landmarks.dat"
art_face_path = sys.argv[1]
target_face_path = sys.argv[2]

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)

art_img = io.imread(art_face_path)
tar_img = io.imread(target_face_path)
ah, aw = art_img.shape[:2]
th, tw = tar_img.shape[:2]
#print(art_img.shape[:2], tar_img.shape[:2], th*1.0/tw, ah*1.0/aw)
is_height_resize = th*1.0/tw > ah*1.0/aw
if is_height_resize:
	print("resize height")
	art_resized = resize(art_img, height=500)
	tar_resized = resize(tar_img, height=500)
else:
	art_resized = resize(art_img, width=300)
	tar_resized = resize(tar_img, width=300)
art_grey = cv2.cvtColor(art_resized, cv2.COLOR_BGR2GRAY)
tar_grey = cv2.cvtColor(tar_resized, cv2.COLOR_BGR2GRAY)
draw_and_write_landmark(art_grey, detector, predictor, "art", True)#, True
draw_and_write_landmark(tar_grey, detector, predictor, "target")

p = np.loadtxt('output/art.txt')
q = np.loadtxt('output/target.txt')
if is_height_resize:
	p = p/2
	q = q/2
	art_resized = resize(art_img, height=250)

art_transformed = mls_rigid_deformation_inv(art_resized, p, q, alpha=1, density=1)
scipy.misc.imsave('output/temp.jpg', art_transformed)
if is_height_resize:
	art_transformed = resize(art_transformed, height=500)
#plt.imshow(art_transformed)
#plt.show()

im1 = art_transformed
im2 = cv2.normalize(tar_resized, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
        
height1, width1 = im1.shape[:2]
height2, width2 = im2.shape[:2]
result = im2
for y in range(height2):
    for x in range(width2):
    	if y < height1 and x < width1:
	        result[y, x, 0] = result[y, x, 0] / 2 + im1[y, x, 0] / 2
	        result[y, x, 1] = result[y, x, 1] / 2 + im1[y, x, 1] / 2
	        result[y, x, 2] = result[y, x, 2] / 2 + im1[y, x, 2] / 2


plt.imshow(result)
plt.show()