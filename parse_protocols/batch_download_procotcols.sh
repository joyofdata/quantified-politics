
echo "https://www.bundestag.de/plenarprotokolle" | \
    wget -O- -i- | \
    hxnormalize -x | \
    hxselect -i "div.linkGeneric a" | \
    grep -Po '(?<=href=")[^"]*(?=")' | \
    awk '{print "https://www.bundestag.de"$1}' | \
    wget -i- -P /media/Volume/data/bundestag/Term18/
