#! /bin/bash

# ./CONVERT.sh [PDF name] [absolute path] [todo index: 0-4]

pdf=$1

folder=$2

# $todo:
# 0: from PDF to PNG
# 1: from h1 on
# 2: from v on
# 3: from h2 on
# 4: only PNG to TXT

todo=$3

# PDF to PNG
if [ "$todo" -eq 0 ]; then
    rm -rf $folder/imgs0
    mkdir $folder/imgs0

    # convert PDF to set of cropped PNGs
    
    # simple version - consumes too much memory for large PDFs
    # convert -density 500 -crop 3328x4840+450+540 $pdf -quality 100 -colorspace Gray imgs0/$pdf.png
    # rename 's/-(\d+)/sprintf("-%03d",$1)/e' imgs0/*
    
    pages=$(pdfinfo $folder/$pdf | grep "Pages" | egrep -o "[0-9]+")
    pages="$[$pages-1]"
    
    for p in `eval echo {0..$pages..1}`
    do
        num=$(printf "%03d" $p)
        convert -density 500 $folder/$pdf[$p] -quality 100 -colorspace Gray -flatten $folder/imgs0/$pdf-$num.png
        convert -crop 3428x4940+400+490 $folder/imgs0/$pdf-$num.png -quality 100 $folder/imgs0/$pdf-$num.png
    done
fi

if [ "$todo" -le 3 ]; then

    if [ "$todo" -le 1 ]; then
        rm -rf $folder/imgs1
        mkdir $folder/imgs1

        rm -rf $folder/imgs2
        mkdir $folder/imgs2

        rm -rf $folder/imgs3
        mkdir $folder/imgs3

        x="h1"
    fi

    if [ "$todo" -eq 2 ]; then
        rm -rf $folder/imgs2
        mkdir $folder/imgs2

        rm -rf $folder/imgs3
        mkdir $folder/imgs3

        x="v"
    fi

    if [ "$todo" -eq 3 ]; then
        rm -rf $folder/imgs3
        mkdir $folder/imgs3

        x="h2"
    fi

    # split PNGs horizontally if necessary
    python3 apply_serialization_of_layout.py $x $folder 
fi


if [ "$todo" -le 4 ]; then
    rm -rf $folder/txts
    mkdir $folder/txts

    # OCR PNGs to text
    for png in $folder/imgs3/*.png
    do
        bn=$(basename $png)
        tesseract $folder/imgs3/$bn $folder/txts/$bn -l deu bazaar
    done

    mv $folder/txts $folder/txt_$pdf
fi
