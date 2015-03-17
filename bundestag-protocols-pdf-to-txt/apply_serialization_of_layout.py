import serialize_layout_on_picture as slop
import os
import sys

what_to_do = sys.argv[1]
abs_path   = sys.argv[2]

if what_to_do in ["h1"]:
    rootdir = abs_path+'/imgs0/'
 
    for file in os.listdir(rootdir):
        print("seg h1: ", file)
        slop.split_png_into_segments("h", file, \
                abs_path+"/imgs0", \
                abs_path+"/imgs1", \
                min_break_height=100,
                prevent_cut_through_vline=True)

if what_to_do in ["h1","v"]:
    rootdir = abs_path+'/imgs1/'
    
    for file in os.listdir(rootdir):
        print("seg v: ", file)
        slop.split_png_into_segments("v", file, \
                abs_path+"/imgs1", \
                abs_path+"/imgs2",
                ratio_threshold_halve=0.8,
                ratio_threshold_quarter=0.999)


if what_to_do in ["h1","v","h2"]:
    rootdir = abs_path+'/imgs2/'
    
    for file in os.listdir(rootdir):
        print("seg h2: ", file)
        slop.split_png_into_segments("h", file, \
                abs_path+"/imgs2", \
                abs_path+"/imgs3", \
                min_break_height=35,
                ratio_threshold_horizontally=0.995)
