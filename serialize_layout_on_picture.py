from PIL import Image
import os
import re
import numpy

def split_png_into_segments(pic_name, source_path, target_path):

    img = Image.open(source_path + "/" + pic_name)

    w,h = img.size

    if is_image_empty(img):
        return

    segments = segment_horizontally(img)

    res = re.search("^(.+)\.png$", pic_name)
    base_pic_name = res.group(1)

    if len(segments) == 0:
        img.save(target_path + "/" + base_pic_name + "_p1.png")
    else:
        part = 0
        for seg in segments:
            part += 1
            img0 = img.crop((0,seg[0],w,seg[1]))
            img0.save(target_path + "/" + base_pic_name + "_p" + str(part) + ".png")

####################################################################################

def segment_horizontally(img, min_break_height=100, clr_threshold=60000, ratio_threshold=0.995, padding=10):
    w,h = img.size

    arr = numpy.asarray(img)

    # element at n is True if row at y=n contains
    # sufficiently many sufficiently white pixels
    sps = [((arr[y,:] > clr_threshold).sum()/w > ratio_threshold) for y in range(h)]

    looking_for_start_of_break = True
    y_breaks = []
    y = -1
    while y < h:
        y += 1
        if h > y + min_break_height + 1:
            if sum(sps[y:(y+min_break_height)]) == min_break_height:
                if looking_for_start_of_break:
                    y_breaks.append(y+padding)
                    looking_for_start_of_break = False
                else:
                    if not sps[y+min_break_height+1]:
                        y_breaks.append(y+min_break_height+1-padding)
                        looking_for_start_of_break = True
                        y = y+min_break_height
   
    if len(y_breaks) > 0:
        if y_breaks[0] > 10:
            y_breaks = [0] + y_breaks
        else:
            y_breaks = y_breaks[1:]
    
        if y_breaks[len(y_breaks)-1] > h-10:
            y_breaks = y_breaks[:-1]
        else:
            y_breaks = y_breaks + [h]

    y_content = list(zip(y_breaks[0::2], y_breaks[1::2]))

    print(y_content)
    
    return y_content

####################################################################################

def is_image_empty(im):
    return len(im.getcolors()) == 1
