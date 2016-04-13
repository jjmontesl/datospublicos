#!/bin/bash

mkdir -p data

#for i in {7143..19855} ; do
#for i in {7143..28000} ; do
for i in {25729..25730} ; do
	if [ ! -f "data/licitacion-$i.html" ] ; then
	        wget --no-check-certificate "http://www.contratosdegalicia.es/licitacion?N=$i" -O "data/licitacion-$i.html" #\
	#        	-U "Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:35.0) Gecko/20100101 Firefox/35.0"
	fi
	
	grep -q 'O procedemento indicado non existe ou xa' data/licitacion-$i.html
	if [ $? -eq 0 ] ; then
		rm data/licitacion-$i.html
	fi
done

