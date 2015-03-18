import sys
import subprocess
import re
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt

config = {
        "margin":10,
        "crop": {
            "top":0,
            "bottom":0,
            "left":0.02,
            "right":0.02
            },
        "seg": {
                "horizontal_1": {
                        "min_size": 70,
                        "max_black": 0
                    }
            }
    }

def convert_pdf_to_images_IO(pdf_name, pdf_path, img_type, imgs_path):
    """Converts a PDF into either a set of PNGs or TIFFs and puts them in dest_path.
    """
    num_of_pages = num_of_pages_in_pdf(pdf_path + "/" + pdf_name)

    img_types = {
            "pnggray" : "png", 
            "pngmono" : "png"
        }

    for i in range(num_of_pages):
        proc = subprocess.Popen([
            "gs",
            "-dNOPAUSE", "-q", 
            "-sDEVICE=" + img_type, 
            "-r500", "-dBATCH",
            "-dFirstPage="+str(i+1),
            "-dLastPage="+str(i+1),
            "-sOutputFile=" + imgs_path + "/" + pdf_name + "_" + "{:03d}".format(i) + "." + img_types[img_type],
            pdf_path + "/" + pdf_name
            ])
        proc.communicate()

    return 0

def calc_segments_for_img(img):
    """Calculates segmenting boxes for image.
    """
    return 0

def dissect_img(img):
    """Dissects image into segments and returns segments.
    """
    return 0

def draw_segments_on_img(img):
    """Draws segmenting boxes on image for debugging purposes.
    """
    return 0

def num_of_pages_in_pdf(pdf):
    """Return number of pages in given PDF.
    """
    proc = subprocess.Popen(["pdfinfo", pdf], stdout=subprocess.PIPE)
    try:
        res = subprocess.check_output(["grep", "Pages"], stdin=proc.stdout)
        res = res.decode("utf-8")
        pages = re.search("[0-9]+", res).group(0)
        pages = int(pages)
    except:
        sys.exit("pdfinfo on "+pdf+" was not successful")

    return pages

def share_of_black_per_white(arr, orientation):
    h, w = arr.shape

    if orientation == "h":
        axis = 0
        num = h
    elif orientation == "v":
        axis = 1
        num = w
    else:
        exit("the following orientation is invalid: " + str(orientation))

    v_sum = arr.sum(axis = axis)
    v_sum = v_sum / num

    return v_sum

def plot_page_and_black_white_projection(img):
    arr = np.asarray(img)

    hor = share_of_black_per_white(arr, "h")
    ver = share_of_black_per_white(arr, "v")
    
    fig = plt.figure()
    
    ax0 = plt.subplot2grid((2,2),(0,0),rowspan=2)
    ax0.imshow(img)
    ax1 = plt.subplot2grid((2,2),(0,1))
    ax1.plot(hor)
    ax2 = plt.subplot2grid((2,2),(1,1))
    ax2.plot(ver)

    plt.show()

def segmentation(arr, config_seg, segments, orientation):

    new_segments = []

    for seg in segments:
        arr_seg = segment_of_array(arr, seg)
        if orientation == "h":
            proj = share_of_black_per_white(arr_seg, "v")
        elif orientation == "v":
            proj = share_of_black_per_white(arr_seg, "h")
        else:
            error(str(orientation) + " ?")

        segment_at = []
        looking_for_start_of_break = True
        size_of_break_until_now = 0

        if orientation == "h":
            rc1 = seg["r1"]
            rc2 = seg["r2"]
        elif orientation == "v":
            rc1 = seg["c1"]
            rc2 = seg["c2"]

        for rc in range(rc1, rc2):
            if proj[rc-rc1] <= config_seg["max_black"]:
                looking_for_start_of_break = False
                size_of_break_until_now += 1

            if proj[rc-rc1] > config_seg["max_black"] and not looking_for_start_of_break:
                if size_of_break_until_now >= config_seg["min_size"]:
                    segment_at.append(int(rc - size_of_break_until_now/2.0))
                    looking_for_start_of_break = True
                    size_of_break_until_now = 0

        if len(segment_at) == 0:
            new_segments.append(seg)
        else:
            new_rc1 = [rc1] + segment_at
            new_rc2 = segment_at + [rc2]
            for i,_ in enumerate(new_rc1):
                if orientation == "h":
                    new_segments.append({"r1":new_rc1[i],"r2":new_rc2[i],"c1":seg["c1"],"c2":seg["c2"]})
                elif orientation == "v":
                    new_segments.append({"c1":new_rc1[i],"c2":new_rc2[i],"r1":seg["r1"],"r2":seg["r2"]})

    return new_segments

def crop_image(arr, config_crop):
    h, w = arr.shape
    
    hor = share_of_black_per_white(arr, "h")
    ver = share_of_black_per_white(arr, "v")

    cropping = {"top":None, "bottom":None, "left":None, "right":None}

    for r in range(h):
        if ver[r] > config_crop["top"]:
            cropping["top"] = r - config["margin"]
            break
    
    for r in reversed(range(h)):
        if ver[r] > config_crop["bottom"]:
            cropping["bottom"] = r + config["margin"]
            break

    for c in range(w):
        if hor[c] > config_crop["left"]:
            cropping["left"] = c - config["margin"]
            break

    for c in reversed(range(w)):
        if hor[c] > config_crop["right"]:
            cropping["right"] = c + config["margin"]
            break

    segments = [{
            "c1":cropping["left"],
            "r1":cropping["top"],
            "c2":cropping["right"],
            "r2":cropping["bottom"]
        }]


    return segments

def segment_of_array(arr, segment):
    return arr[segment["r1"]:segment["r2"], segment["c1"]:segment["c2"]]
