import serialize_layout_on_picture as slop
import os
import sys

what_to_do = sys.argv[1]

if what_to_do in ["h1"]:
    rootdir = './processing/imgs0/'
 
    for file in os.listdir(rootdir):
        print("seg h1: ", file)
        slop.split_png_into_segments("h", file, \
                "./processing/imgs0", \
                "./processing/imgs1", \
                min_break_height=100,
                prevent_cut_through_vline=True)

if what_to_do in ["h1","v"]:
    rootdir = './processing/imgs1/'
    
    for file in os.listdir(rootdir):
        print("seg v: ", file)
        slop.split_png_into_segments("v", file, \
                "./processing/imgs1", \
                "./processing/imgs2",
                ratio_threshold_halve=0.8,
                ratio_threshold_quarter=0.999)


if what_to_do in ["h1","v","h2"]:
    rootdir = './processing/imgs2/'
    
    for file in os.listdir(rootdir):
        print("seg h2: ", file)
        slop.split_png_into_segments("h", file, \
                "./processing/imgs2", \
                "./processing/imgs3", \
                min_break_height=35)
