#!/bin/bash


function get_boe {

	YEAR=$1
	BOE_A_NUM=$2
	BOE_B_NUM=$3

	mkdir -p data/$YEAR

	for i in $( seq 1 $BOE_A_NUM ) ; do
		if [ ! -f "data/$YEAR/BOE-A-$YEAR-$i.xml" ] ; then
			wget --no-check-certificate "http://www.boe.es/diario_boe/xml.php?id=BOE-A-$YEAR-$i" -O "data/$YEAR/BOE-A-$YEAR-$i.xml"
		fi
	done
	for i in $( seq 1 $BOE_B_NUM ) ; do
		if [ ! -f "data/$YEAR/BOE-B-$YEAR-$i.xml" ] ; then
			wget  --no-check-certificate "http://www.boe.es/diario_boe/xml.php?id=BOE-B-$YEAR-$i" -O "data/$YEAR/BOE-B-$YEAR-$i.xml"
		fi
	done

}

#get_boe 2013 12002 43008
#get_boe 2012 15822 45268
#get_boe 2011 20867 43124
#get_boe 2010 20188 44900
get_boe 2009 21238 45309
#get_boe 2008 21053 315270


