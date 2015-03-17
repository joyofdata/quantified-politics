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

#########################################################################
#
# configuration for horizontal segmentation:

min_break_height=35
ratio_threshold_horizontally=0.995

# 3
# expected are 9 segments

img = Image.open("tests_imgs/18003.pdf-159_p01_p01.png")
wht = white_value(img)
res = segment_horizontally(img,
        min_break_height=min_break_height,
        color_threshold=int(wht*0.9),
        ratio_threshold=ratio_threshold_horizontally)

print(len(res)==9, " / ", len(res))
print(res)

# 4
# expected is 1 segment

img = Image.open("tests_imgs/18003.pdf-100_p01_p01.png")
wht = white_value(img)
res = segment_horizontally(img,
        min_break_height=min_break_height,
        color_threshold=int(wht*0.9),
        ratio_threshold=ratio_threshold_horizontally)

print(len(res)==0, " / ", len(res))
print(res)


# 5
# expected are 2 segments

img = Image.open("tests_imgs/18003.pdf-159_p01_p02_p07.png")
wht = white_value(img)
res = segment_horizontally(img,
        min_break_height=min_break_height,
        color_threshold=int(wht*0.9),
        ratio_threshold=ratio_threshold_horizontally)

print(len(res)==2, " / ", len(res))
print(res)

# 6
# expected are 9 segments

img = Image.open("tests_imgs/18003.pdf-022_p01_p01.png")
wht = white_value(img)
res = segment_horizontally(img,
        min_break_height=min_break_height,
        color_threshold=int(wht*0.9),
        ratio_threshold=ratio_threshold_horizontally)

print(len(res)==9, " / ", len(res))
print(res)

