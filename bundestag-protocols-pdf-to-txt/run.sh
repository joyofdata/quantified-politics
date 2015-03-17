#!/bin/bash

abs_path=$1

for file in $abs_path/*.pdf
do
    filename=$(basename $file)
    ./CONVERT.sh $filename $abs_path 0
done
