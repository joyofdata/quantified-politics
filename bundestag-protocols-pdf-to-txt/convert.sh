#! /bin/bash

pdf=18091.pdf

mkdir imgs0
mkdir imgs1
mkdir imgs2
mkdir imgs3
mkdir txts

# convert PDF to set of cropped PNGs

# simple version - consumes too much memory for large PDFs
# convert -density 500 -crop 3328x4840+450+540 $pdf -quality 100 -colorspace Gray imgs0/$pdf.png
# rename 's/-(\d+)/sprintf("-%03d",$1)/e' imgs0/*

pages=$(pdfinfo $pdf | grep "Pages" | egrep -o "[0-9]+")
pages="$[$pages-1]"

for p in `eval echo {0..$pages..1}`
do
    num=$(printf "%03d" $p)
    convert -density 500 -crop 3328x4840+450+540 $pdf[$p] -quality 100 -colorspace Gray imgs0/$pdf-$num.png
done

# split PNGs horizontally if necessary
python3 apply_serialization_of_layout.py

# OCR PNGs to text
for png in imgs3/*.png
do
    bn=$(basename $png)
    tesseract imgs3/$bn txts/$bn -l deu bazaar
done

cat txts/* > $pdf.txt

#sed -i -e ':a;N;$!ba;s/-\n//g' $pdf.txt
