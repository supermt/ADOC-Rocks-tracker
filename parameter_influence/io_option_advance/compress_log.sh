#files=($(find ./ -name "LOG*"))
#echo ${files[0]}

for file in $(find ./ -name "LOG*") 
do
  gzip $file
done
