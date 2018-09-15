import cv2
import math
import sys
import os
import json
from sklearn.cluster import KMeans

if __name__ == "__main__":
	pic1 = str(sys.argv[1])
	pic2 = str(sys.argv[2])
	nClusters = int(sys.argv[3])
	show = int(sys.argv[4])

# find difference between two images and
# store that as a new image file
img1 = cv2.imread(pic1)
img2 = cv2.imread(pic2)
imgDif = img1 - img2

# get image width and height
height, width = imgDif.shape[:2]

# go through every pixel and check if it is
# not black, if so, push it's coordinates
# into a list for k-means clustering
points = list()
for x in range(0, width):
	for y in range(0, height):
		if (imgDif[y, x] != [0, 0, 0]).all():
			points.append((x, y))

# CLUSTER!
kmeans = KMeans(n_clusters=nClusters)
kmeans.fit(points)

# Iterate through each point in the cluster, 
# and estimate an elipse that covers the 
# cluster
data = {}
data[str(pic1)] = {}

for i in range(nClusters):
	left = None
	right = None
	up = None
	down = None
	for j in range(len(points)):
		if kmeans.labels_[j] == i:
			# point is left of center
			if points[j][0] < kmeans.cluster_centers_[i][0]:
				if left is None:
					left = points[j]
				else:
					if points[j][0] < left[0]:
						left = points[j]
			# point is right of center
			elif points[j][0] > kmeans.cluster_centers_[i][0]:
				if right is None:
					right = points[j]
				else:
					if points[j][0] > right[0]:
						right = points[j]

			# point is up of center
			if points[j][1] < kmeans.cluster_centers_[i][1]:
				if up is None:
					up = points[j]
				else:
					if points[j][1] < up[1]:
						up = points[j]
			# point is down of center
			elif points[j][1] > kmeans.cluster_centers_[i][1]:
				if down is None:
					down = points[j]
				else:
					if points[j][1] > down[1]:
						down = points[j]

	tl = (left[0], up[1]) # top left point
	tr = (right[0], up[1]) # top right point
	bl = (left[0], down[1]) # bottom left point
	br = (right[0], down[1]) # bottom right point

	# horizontal and vertical axis
	haxis = ((tl[0], (tl[1] + bl[1]) / 2), (tr[0], (tr[1] + br[1]) / 2))
	vaxis = (((tl[0] + tr[0]) / 2, tl[1]), ((bl[0] + br[0]) / 2, bl[1]))

	# JSON data collection for output
	data[str(pic1)]['cluster_' + str(i)] = {
		'center_x': str(math.floor(kmeans.cluster_centers_[i][0])),
		'center_y': str(math.floor(kmeans.cluster_centers_[i][1])), 
		'tl_x': str(tl[0]), 'tl_y': str(tl[1]),
		'tr_x': str(tr[0]), 'tr_y': str(tr[1]),
		'bl_x': str(bl[0]), 'bl_y': str(bl[1]),
		'br_x': str(br[0]), 'br_y': str(br[1]),
		#'hax1x': str(haxis[0][0]), 'hax1y': str(haxis[0][1]),
		#'hax2x': str(haxis[1][0]), 'hax2y': str(haxis[1][1]),
		#'vax1x': str(vaxis[0][0]), 'vax1y': str(vaxis[0][1]),
		#'vax2x': str(vaxis[1][0]), 'vax2y': str(vaxis[1][1]),
	}

	if show == 1:
		# draw borders
		cv2.line(img1, (math.floor(tl[0]), math.floor(tl[1])),
			(math.floor(tr[0]), math.floor(tr[1])), (0, 0, 255), 4)

		cv2.line(img1, (math.floor(tr[0]), math.floor(tr[1])),
			(math.floor(br[0]), math.floor(br[1])), (0, 0, 255), 4)

		cv2.line(img1, (math.floor(br[0]), math.floor(br[1])),
			(math.floor(bl[0]), math.floor(bl[1])), (0, 0, 255), 4)

		cv2.line(img1, (math.floor(bl[0]), math.floor(bl[1])),
			(math.floor(tl[0]), math.floor(tl[1])), (0, 0, 255), 4)

print(data)
# write to JSON file
# append to old JSON file
if os.path.exists('./clusterData.json'):
	with open('./clusterData.json') as file:
		oldData = json.load(file)
	oldData.update(data)

	with open('./clusterData.json', 'w') as file:
		json.dump(oldData, file)

# create new JSON file
else:		
	with open('./clusterData.json', 'w') as file:
		json.dump(data, file)

if show == 1:
	cv2.imshow('img1', img1)
	cv2.waitKey(0)
	cv2.imwrite('01.png', imgDif)
	cv2.destroyAllWindows()