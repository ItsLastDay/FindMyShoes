#!/bin/bash
if [ -z $1 ]
then
    echo "USAGE: $0 json-dir"
    exit 1
fi
json_dir="$1"

tmp_file=$(tempfile)
for f in "$json_dir"/*.json; 
do 
    cat "$f"; 
    echo; 
done > "$tmp_file"

mongoimport --db=findmyshoes --collection=data --drop "$tmp_file"

