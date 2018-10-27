#!/bin/bash
# Dependencies: 	
# Usage: Place in top level directory of your project and run as a shell script `./minify.sh`
# Modify YUI_PATH with the path to the yuicompressor jar file
YUI_PATH="min.jar"
LOG_PATH="minify_log.txt"
RED="\033[0;31m"
GREEN="\033[0;32m"
END_COL="\e[0m"


echo "Minifying JS files..."
for file in $(find `pwd` -type f -name "*.js");
do
	# Ignore minified files
	if [[ ($file =~ "min.js") ]] ; then
		continue 
	fi
		# Append errors (2>&1) to logfile
      	npx babel $file --presets minify -o "${file%.*}.min.js"  >> $LOG_PATH 2>&1
      	if (( $? )); then
    		echo -e "${RED}$(basename $file) was not able to be minified! ${END_COL}"
      	else
        	echo -e "${GREEN}$(basename $file) was minified to $(basename ${file%.*}).min.js ${END_COL}"
      	fi
done;

echo "Minifying CSS files..."
for file in $(find `pwd` -type f -name "*.css");
do
	# Ignore minified files
	if [[ ($file =~ "min.css") ]] ; then
		continue 
	fi

     	java -jar $YUI_PATH -o "${file%.*}.min.css" "$file" >> $LOG_PATH 2>&1
     	if (( $? )); then
    		echo -e "${RED}$(basename $file) was not able to be minified! ${END_COL}"
      	else
        	echo -e "${GREEN}$(basename $file) was minified to $(basename ${file%.*}).min.css ${END_COL}"
      	fi
done;

echo "Check $LOG_PATH for errors."
exit 0