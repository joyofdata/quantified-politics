import sys
import subprocess
import re
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

std_config = {
        "margin":10,
        "std_crop": {
            "margin": 10,
            "max_black": {
                    "top":   0,
                    "bottom":0,
                    "left":  0,
                    "right": 0
                }
            },
        "seg": {
                "horizontal_1": {
                        "min_size": 70,
                        "max_black": 0
                    },
                "vertical": {
                        "min_size":  40,
                        "max_black": 0
                    },
                "horizontal_2": {
                        "min_size": 50,
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

def calc_segments_for_image(img, config):
    """Calculates segmenting boxes for image.
    """
    arr = np.asarray(img)

    all_segs = {}

    segs = [{"r1":230, "r2":5650, "c1":400, "c2": 3720}]
    all_segs["init_crop"] = segs

    segs = segmentation(arr, config["seg"]["horizontal_1"], segs, "h", False)
    all_segs["h1"] = segs

    segs = crop_segments(arr, segs, config["std_crop"])
    all_segs["h1_crop"] = segs

    segs = segmentation(arr, config["seg"]["vertical"], segs, "v", True)
    all_segs["v"] = segs

    segs = crop_segments(arr, segs, config["std_crop"])
    all_segs["v_crop"] = segs

    segs = segmentation(arr, config["seg"]["horizontal_2"], segs, "h", False)
    all_segs["h2"] = segs

    segs = crop_segments(arr, segs, config["std_crop"])
    all_segs["h2_crop"] = segs

    return all_segs

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

def plot_page_and_black_white_projection(img, config, segs_step="h2_crop"):
    arr = np.asarray(img)
    h, w = arr.shape

    hor = share_of_black_per_white(arr, "h")
    ver = share_of_black_per_white(arr, "v")
    
    fig = plt.figure()
    
    ax0 = plt.subplot2grid((2,2),(0,0),rowspan=2)
    ax0.imshow(img)
    ax1 = plt.subplot2grid((2,2),(0,1))
    ax1.plot(hor)
    ax2 = plt.subplot2grid((2,2),(1,1))
    ax2.plot(ver)

    def draw_rects(elem, segs, clr):
        for seg in segs:
            rows = seg["r2"] - seg["r1"]
            cols = seg["c2"] - seg["c1"]
            elem.add_patch(patches.Rectangle((seg["c1"],seg["r1"]),cols,rows,fill=False,edgecolor=clr))

    segs = calc_segments_for_image(img, config)
    draw_rects(ax0, segs[segs_step], "red")
        
    plt.show()

def segmentation(arr, config_seg, segments, orientation, v_seg_at_black_line=False, debug=False):
    new_segments = []

    for seg in segments:
        arr_seg = segment_of_array(arr, seg)
        if orientation == "h":
            proj = share_of_black_per_white(arr_seg, "v")
            if debug:
                return proj
        elif orientation == "v":
            proj = share_of_black_per_white(arr_seg, "h")
        else:
            error(str(orientation) + " ?")

        segment_at = []

        section_vertically_at_black_line = False
        if v_seg_at_black_line:
            if orientation != "v":
                error("v_seg_at_black_line is True but orientation is not 'v' !?")

            rc1 = seg["c1"]
            rc2 = seg["c2"]
            
            center_column = int((seg["c2"] - seg["c1"])/2.0 + seg["c1"])
            tol = int((seg["c2"] - seg["c1"]) * 0.1)
            for c in range(center_column - tol, center_column + tol):
                if proj[c - seg["c1"]] > 0.9:
                    segment_at = [c-10,c+10]
                    section_vertically_at_black_line = True

        if not section_vertically_at_black_line:
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

                # the middle segment is just the black line itself
                if section_vertically_at_black_line and i == 1:
                    continue

                if orientation == "h":
                    new_segments.append({"r1":new_rc1[i],"r2":new_rc2[i],"c1":seg["c1"],"c2":seg["c2"]})
                elif orientation == "v":
                    new_segments.append({"c1":new_rc1[i],"c2":new_rc2[i],"r1":seg["r1"],"r2":seg["r2"]})
        
    return new_segments

def crop_segments(arr, segs, cfg):
    new_segments = []

    for seg in segs:
        arr_seg = segment_of_array(arr, seg)

        if arr_seg.mean() == 0:
            continue

        h, w = arr_seg.shape
        
        hor = share_of_black_per_white(arr_seg, "h")
        ver = share_of_black_per_white(arr_seg, "v")

        new_seg = {"r1":None, "r2":None, "c1":None, "c2":None}

        for r in range(seg["r1"], seg["r2"]):
            if ver[r - seg["r1"]] > cfg["max_black"]["top"]:
                new_seg["r1"] = r - cfg["margin"]
                break

        for r in reversed(range(seg["r1"], seg["r2"])):
            if ver[r - seg["r1"]] > cfg["max_black"]["bottom"]:
                new_seg["r2"] = r + cfg["margin"]
                break
         
        for c in range(seg["c1"], seg["c2"]):
            if hor[c - seg["c1"]] > cfg["max_black"]["left"]:
                new_seg["c1"] = c - cfg["margin"]
                break

        for c in reversed(range(seg["c1"], seg["c2"])):
            if hor[c - seg["c1"]] > cfg["max_black"]["right"]:
                new_seg["c2"] = c + cfg["margin"]
                break

        new_segments.append(new_seg)

    return new_segments

def segment_of_array(arr, segment):
    return arr[segment["r1"]:segment["r2"], segment["c1"]:segment["c2"]]
