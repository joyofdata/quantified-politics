import sys
import subprocess
import re
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import glob
import os

std_config = {
        "margin":10,
        "init_crop": {
                "r1":230, 
                "r2":5650, 
                "c1":400, 
                "c2": 3720
            },
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
                        "min_size": 50,
                        "max_black": 0
                    },
                "vertical": {
                        "min_size":  40,
                        "max_black": 0
                    },
                "horizontal_2": {
                        "min_size": 45,
                        "max_black": 0
                    }
            }
    }

def convert_pdf_to_txt_IO(pdf_name, pdf_path, img_type, imgs_path, img_segs_path, txt_base_path, config):
    proc = subprocess.Popen(["rm","-rf",imgs_path]).communicate()
    proc = subprocess.Popen(["rm","-rf",img_segs_path]).communicate()
    proc = subprocess.Popen(["mkdir",imgs_path]).communicate()
    proc = subprocess.Popen(["mkdir",img_segs_path]).communicate()

    convert_pdf_to_images_IO(pdf_name, pdf_path, img_type, imgs_path)
    segment_images_IO(imgs_path, img_segs_path, config, "png")

    txt_path = "{}/txt_{}".format(txt_base_path,pdf_name)
    proc = subprocess.Popen(["mkdir",txt_path])

    imgs = glob.glob("{}/*".format(img_segs_path))
    for img in imgs:
        img_bn = os.path.basename(img)
        img_bn = img_bn[:-4]

        proc = subprocess.Popen([
                "tesseract",
                img,
                "{}/{}".format(txt_path,img_bn),
                "-l", "deu",
                "bazaar"
            ])
        proc.communicate()

    proc = subprocess.Popen(
        '''find {0}/*.txt -type f \
        | sort \
        | while read file; do echo "====" ; cat $file; done \
        > {0}.txt'''.format(txt_path), 
    shell=True)


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
            "-sOutputFile=" + imgs_path + "/" + pdf_name + "_" + "{:03d}".format(i+1) + "." + img_types[img_type],
            pdf_path + "/" + pdf_name
            ])
        proc.communicate()

    return 0

def measure_crop_area(imgs_path):
    arr = None
    for f in glob.glob("{}/*".format(imgs_path)):
        img = Image.open(f)
        if arr is None:
            arr = np.asarray(img)
        else:
            arr = np.maximum(arr, np.asarray(img))

    h,w = arr.shape
    segs = [{"r1":0,"r2":h-1,"c1":0,"c2":w-1}]
    config = {"margin":20, "max_black": {"top":0.01,"bottom":0.01,"left":0.1,"right":0.1}}
    segs = crop_segments(arr, segs, config)

    return segs[0]

def segment_images_IO(imgs_src_path, imgs_dest_path, config, img_ext):

    config["init_crop"] = measure_crop_area(imgs_src_path)

    filenames = glob.glob("{}/{}".format(imgs_src_path,"*"))
    for f in filenames:
        img = Image.open(f)
        segs = calc_segments_for_image(img, config)
        sub_imgs = segment_image(img, segs["h2_crop"])

        bn = os.path.basename(f)
        bn = bn[:-4]

        for i, sub_img in enumerate(sub_imgs):
            sub_img.save("{}/{}_{:03d}.{}".format(imgs_dest_path, bn, i+1,img_ext))


def segment_image(img, segments):
    img_segs = []
    for seg in segments:
        x1 = seg["c1"]
        x2 = seg["c2"]
        y1 = seg["r1"]
        y2 = seg["r2"]

        img_segs.append(img.crop((x1,y1,x2,y2)))

    return img_segs

def calc_segments_for_image(img, config):
    """Calculates segmenting boxes for image.
    """
    arr = np.asarray(img)

    all_segs = {}

    segs = [config["init_crop"]]
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
