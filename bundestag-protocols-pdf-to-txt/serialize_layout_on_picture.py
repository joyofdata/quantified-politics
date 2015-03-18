from PIL import Image
import os
import re
import numpy

def split_png_into_segments(direction, pic_name, source_path, target_path, 
        min_break_height=100, 
        prevent_cut_through_vline=False,
        ratio_threshold_halve=0.85,
        ratio_threshold_quarter=0.99,
        ratio_threshold_horizontally=0.99):

    img = Image.open(source_path + "/" + pic_name)

    w,h = img.size

    if is_image_empty(img):
        return

    white = white_value(img)
    color_threshold = int(white * 0.9)

    if direction == "h":
        segments = segment_horizontally(img, 
                min_break_height=min_break_height, 
                color_threshold=color_threshold, 
                prevent_cut_through_vline=prevent_cut_through_vline,
                ratio_threshold=ratio_threshold_horizontally)
    elif direction == "v":
        segments = segment_vertically(img, 
                color_threshold=color_threshold,
                ratio_threshold_halve=ratio_threshold_halve,
                ratio_threshold_quarter=ratio_threshold_quarter)
    else:
        return

    res = re.search("^(.+)\.png$", pic_name)
    base_pic_name = res.group(1)

    if len(segments) == 0:
        img.save(target_path + "/" + base_pic_name + "_p01.png")
    else:
        part = 0
        for seg in segments:
            if direction == "h":
                img0 = img.crop((0,seg[0],w,seg[1]))
            elif direction == "v":
                img0 = img.crop((seg[0],0,seg[1],h))
            else:
                return

            if not is_image_empty(img0):
                part += 1
                img0.save(target_path + "/" + base_pic_name + "_p" + "{:02d}".format(part) + ".png")


####################################################################################

def segment_vertically(img, 
        color_threshold=60000, 
        ratio_threshold_halve=0.85,
        ratio_threshold_quarter=0.99):
    w,h = img.size 

    # minimum height of three lines of standard text
    if h < 220:
        return []

    segments = halve_image(img, 
                color_threshold=color_threshold,
                ratio_threshold=ratio_threshold_halve
            )
    
    if len(segments) == 0:
        segments = quarter_image(img, 
                    color_threshold=color_threshold,
                    ratio_threshold=ratio_threshold_quarter
                )

    print(segments)

    return segments

def halve_image(img, ratio_threshold=0.85, color_threshold=60000):
    w,h = img.size
    arr = numpy.asarray(img)

    margin = w * 0.03
    middle_area = range(int(w/2-margin), int(w/2+margin))
    
    non_white_columns = [(arr[:,x] < color_threshold).sum() for x in middle_area]
    non_white_pixels_in_column = max(non_white_columns)

    if non_white_pixels_in_column > ratio_threshold * h:
        x = int(w/2-margin) + non_white_columns.index(non_white_pixels_in_column)
        return [(0, x-10), (x+10, w-1)]
    else:
        return []

def quarter_image(img, ratio_threshold=0.99, padding=50, color_threshold=60000):
    w,h = img.size
    arr = numpy.asarray(img)

    margin = int(w * 0.03)
    tolerated_deviation = range(-margin, margin)

    xs_where_quarters_touch = [int(w/4),int(w/2),int(3/4 * w)]

    cut_at_x = []
    for x in xs_where_quarters_touch:
        area_to_check_out = [x + tol for tol in tolerated_deviation]
        white_columns = [(arr[:,x] > color_threshold).sum() for x in area_to_check_out]
        white_pixels_in_column = max(white_columns)

        if white_pixels_in_column > ratio_threshold * h:
            cut_at_x.append(int(x - margin + white_columns.index(white_pixels_in_column))+padding)
        else:
            return []

    segments = list(zip([0]+cut_at_x, cut_at_x+[w]))
    
    return segments

####################################################################################

def segment_horizontally(img, min_break_height=100, color_threshold=60000, ratio_threshold=0.99, padding=10, prevent_cut_through_vline=False):
    w,h = img.size

    arr = numpy.asarray(img)

    # element at n is True if row at y=n contains
    # sufficiently many sufficiently white pixels
    sps = [((arr[y,:] > color_threshold).sum()/w > ratio_threshold) for y in range(h)]

    if prevent_cut_through_vline:
        margin = int(w * 0.03)
        middle = int(w/2)
        arr0 = arr[:,(middle-margin):(middle+margin)]
        black_rows = numpy.amax(arr0 < color_threshold, axis=1)
        preceding_black_line0 = numpy.sum(rolling_window(black_rows, min_break_height), 1) == min_break_height
        preceding_black_line = numpy.concatenate([
                    [False]*(min_break_height-1),
                    preceding_black_line0
            ])

        sps = numpy.logical_and(sps, numpy.logical_not(preceding_black_line))

    looking_for_start_of_break = True
    y_breaks = []
    y = -1
    while y < (h-1):
        y += 1

        if not h > y + min_break_height + 1 and looking_for_start_of_break:
            break

        if sum(sps[y:(y+min_break_height)]) == min_break_height and \
           looking_for_start_of_break:
                y_breaks.append(y+padding)
                looking_for_start_of_break = False
                y = y + min_break_height
        elif not looking_for_start_of_break and \
             not sps[y]:
                y_breaks.append(y-padding)
                looking_for_start_of_break = True
   
    print(y_breaks)

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

def rolling_window(a, window):
    # http://stackoverflow.com/questions/6811183/rolling-window-for-1d-arrays-in-numpy
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    return numpy.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)

def white_value(img):
    clrs = img.getcolors()
    return max([c for (n,c) in clrs])
