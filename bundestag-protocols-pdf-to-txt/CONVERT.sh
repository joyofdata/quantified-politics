#! /bin/bash

pdf=$1

# $2:
# 0: from PDF to PNG
# 1: from h1 on
# 2: from v on
# 3: from h2 on
# 4: only PNG to TXT

# PDF to PNG
if [ "$2" -eq 0 ]; then
    rm -rf processing/imgs0
    mkdir processing/imgs0

    # convert PDF to set of cropped PNGs
    
    # simple version - consumes too much memory for large PDFs
    # convert -density 500 -crop 3328x4840+450+540 $pdf -quality 100 -colorspace Gray imgs0/$pdf.png
    # rename 's/-(\d+)/sprintf("-%03d",$1)/e' imgs0/*
    
    pages=$(pdfinfo processing/$pdf | grep "Pages" | egrep -o "[0-9]+")
    pages="$[$pages-1]"
    
    for p in `eval echo {0..$pages..1}`
    do
        num=$(printf "%03d" $p)
        convert -density 500 processing/$pdf[$p] -quality 100 -colorspace Gray -flatten processing/imgs0/$pdf-$num.png
        convert -crop 3328x4840+450+540 processing/imgs0/$pdf-$num.png -quality 100 processing/imgs0/$pdf-$num.png
    done
fi

if [ "$2" -le 3 ]; then

    if [ "$2" -eq 1 ]; then
        rm -rf processing/imgs1
        mkdir processing/imgs1

        rm -rf processing/imgs2
        mkdir processing/imgs2

        rm -rf processing/imgs3
        mkdir processing/imgs3

        x="h1"
    fi

    if [ "$2" -eq 2 ]; then
        rm -rf processing/imgs2
        mkdir processing/imgs2

        rm -rf processing/imgs3
        mkdir processing/imgs3

        x="v"
    fi

    if [ "$2" -eq 3 ]; then
        rm -rf processing/imgs3
        mkdir processing/imgs3

        x="h2"
    fi

    # split PNGs horizontally if necessary
    python3 apply_serialization_of_layout.py $x
fi


if [ "$2" -ge 4 ]; then
    rm -rf processing/txts
    mkdir processing/txts

    # OCR PNGs to text
    for png in processing/imgs3/*.png
    do
        bn=$(basename $png)
        tesseract processing/imgs3/$bn processing/txts/$bn -l deu bazaar
    done
fi
