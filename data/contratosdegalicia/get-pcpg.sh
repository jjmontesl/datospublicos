#!/bin/bash

mkdir -p data

#for i in {7143..19855} ; do
for i in {19855..25000} ; do
	if [ ! -f "data/licitacion-$i.html" ] ; then
	        wget --no-check-certificate "http://www.contratosdegalicia.es/licitacion?N=$i" -O "data/licitacion-$i.html"
	fi
	
	grep -q 'Intentouse acceder a un concurso que non existe' data/licitacion-$i.html
	if [ $? -eq 0 ] ; then
		rm data/licitacion-$i.html
	fi
done

