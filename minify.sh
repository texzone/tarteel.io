# #!/bin/sh
# for file in $(find `pwd` -type f -name "*.js")
# do
# 	if [[ $file = *".min.js"* ]]; then
#   		continue
# 	fi

# 	filename=`basename $file .js`
# 	echo "Compressing $filename.js into $filename.min.js"
# 	java -jar min.jar $file -o ${file%.*}.min.js
# done

# Modify YUI_PATH with the path to the yuicompressor jar file
YUI_PATH="min.jar"

# if [ $# -eq 0 ]; then
#   echo "Please include the file path(s) for the file(s) that you would like to compress." 1>&2
#   exit 1
# fi

for file in $(find `pwd` -type f -name "*.js");
do
if [ -f "$file" ]; then
	if [[ ($file =~ "min.js") || ($file =~ "min.min.js") ]] ; then
		continue 
	fi
      java -jar "$YUI_PATH" -o "${file%.*}.min.js" "$file"
      if (( $? )); then
          echo "$file was not able to be minified"
      else
          echo "$file was minified to ${file%.*}.min.js"
      fi
  else
      echo "Unable to find the javascript file '$file'."
fi
done;
exit 0