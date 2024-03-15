'''通过特征匹配+单应性，进行对象查找'''
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt

img1 = cv.imread('./images/21.jpg',0)           # 查询图像
img2 = cv.imread('./images/22.jpg',0)           # 目标图像（训练图像）

# 特征匹配
# 初始化SIFT检测器
sift = cv.xfeatures2d.SIFT_create()
# 找到SIFT特征点和描述符
kp1, des1 = sift.detectAndCompute(img1,None)
kp2, des2 = sift.detectAndCompute(img2,None)
# FLANN 参数
FLANN_INDEX_KDTREE = 1
index_params = dict(algorithm = FLANN_INDEX_KDTREE, trees = 5)
search_params = dict(checks=50)     # 或传递一个空字典
flann = cv.FlannBasedMatcher(index_params,search_params)
matches = flann.knnMatch(des1,des2,k=2)
# 存储通过比率测试的匹配.
good = []
for m,n in matches:
    if m.distance < 0.7*n.distance:
        good.append(m) 
        
# 对象查找（仅在至少有10个合格匹配的请情况下进行）
MIN_MATCH_COUNT = 10
if len(good)>MIN_MATCH_COUNT:
    src_pts = np.float32([ kp1[m.queryIdx].pt for m in good ]).reshape(-1,1,2)
    dst_pts = np.float32([ kp2[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
    M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC,5.0)
    matchesMask = mask.ravel().tolist()
    h,w= img1.shape
    pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
    dst = cv.perspectiveTransform(pts,M)
    img2 = cv.polylines(img2,[np.int32(dst)],True,255,3, cv.LINE_AA)
else:
    print( "Not enough matches are found - {}/{}".format(len(good), MIN_MATCH_COUNT) )
    matchesMask = None
draw_params = dict(matchColor = (0,255,0), # 绘制匹配
                   singlePointColor = None,
                   matchesMask = matchesMask, # 绘制查询图像的轮廓线
                   flags = 2)
img3 = cv.drawMatches(img1,kp1,img2,kp2,good,None,**draw_params)
plt.imshow(img3, 'gray'),plt.show()