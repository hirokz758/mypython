from turtle import *
shape("turtle")
speed(100)
col = ["orange","limegreen","gold","plum","tomato"]

def myblock():
    for i in range(5):
        color(col[i])
        circle(30)
        left(72)

for j in range(100):
    myblock()
    left(j*5)
    forward(j*5)

done()


