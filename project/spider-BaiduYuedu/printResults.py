# 导入常用的包
import numpy as np
import matplotlib.pyplot as plt
import csv

  
# 显示图像
#plt.show()

dataList = []
cnt = 0
priceList = []
with open('database.csv')as f:
    f_csv = csv.reader(f)
    for row in f_csv:
        if cnt > 0:
            dataList.append([cnt,row[1],row[3]])
            priceList.append(float(row[3]))
        #print(row)
        cnt = cnt + 1
print(dataList)

x = np.arange(0, len(priceList))
y = np.array(priceList)
print(x)
print(y)
plt.rcParams['font.sans-serif']=['STSong']     #解决中文显示问题，目前只知道黑体可行
plt.scatter(x,y)
for i in range(len(x)):
    plt.annotate(dataList[i][1], xy = (x[i], y[i]), xytext = (x[i]+0.1, y[i]+0.1))
plt.show()