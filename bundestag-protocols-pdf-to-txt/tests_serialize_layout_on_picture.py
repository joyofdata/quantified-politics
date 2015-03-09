from serialize_layout_on_picture import segment_vertically
from serialize_layout_on_picture import segment_horizontally
from serialize_layout_on_picture import white_value
from PIL import Image

# 1
# expected is vertical halving:

ratio_threshold_quarter=0.999
ratio_threshold_halve=0.8

img = Image.open("tests_imgs/18003.pdf-098_p01.png")
wht = white_value(img)
res = segment_vertically(img, 
        color_threshold=int(wht*0.9), 
        ratio_threshold_halve=ratio_threshold_halve,
        ratio_threshold_quarter=ratio_threshold_quarter)

print(len(res) == 2)
print(res)


# 2
# expected is no manipulation 

ratio_threshold_quarter=0.999
ratio_threshold_halve=0.8

img = Image.open("tests_imgs/18003.pdf-143_p02.png")
wht = white_value(img)
res = segment_vertically(img, 
        color_threshold=int(wht*0.9), 
        ratio_threshold_halve=ratio_threshold_halve,
        ratio_threshold_quarter=ratio_threshold_quarter)

print(len(res)==0)
print(res)


# 3
# expected are 9 segments

min_break_height=35

img = Image.open("tests_imgs/18003.pdf-159_p01_p01.png")
wht = white_value(img)
res = segment_horizontally(img,
        min_break_height=min_break_height,
        color_threshold=int(wht*0.9))

print(len(res)==9, " / ", len(res))
print(res)
