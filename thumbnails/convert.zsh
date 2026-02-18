#! /bin/zsh

for f in *.png; do
    echo "Processing" $f
    convert ../images/$f -resize 512 -quality 90 $f
done
