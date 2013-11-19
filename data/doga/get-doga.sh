#!/bin/bash

httrack "http://www.xunta.es/diario-oficial-galicia/construirMapaCalendario.do?compMenu=10103&year=2013" \
	-v \
	-r6 \
	--include-query-string \
	'-*' \
	'+*Publicados*' \
	'+*mostrarContenido*' \
	'-*pdf'
