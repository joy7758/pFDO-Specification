!#/bin/bash


convert () {
# 1=file; 2==classname
	filename=${classname}.py
	python3 pydantic_fix.py $file
	localfile=$(basename ${file})
	datamodel-codegen \
		--input $1 \
		--input-file-type jsonschema \
		--output $filename \
		--output-model-type pydantic_v2.BaseModel \
                --enum-field-as-literal all \
                --disable-timestamp \
                --enable-version-header \
		--class-name $2
	rm $localfile
}

for file in ../doip-response-segments/*.json; do
	echo "Processing" $file
	tmp1=${file%.json}
	name=${tmp1##*Op.}
	classname=${name%-Response}_response
	convert $file $classname
done

for file in ../doip-ex-response-segments/*.json; do
	echo "Processing" $file
	tmp1=${file%.json}
	name=${tmp1##*Op.}
	name2=${name%-Response}_response
	classname=extended_${name2##Extended-}
	convert $file $classname
done

for file in ../doip-request-segments/*.json; do
	echo "Processing" $file
	tmp1=${file%.json}
	name=${tmp1##*Op.}
	classname=${name%-Request}_request
	convert $file $classname
done

for file in ../doip-ex-request-segments/*.json; do
	echo "Processing" $file
	tmp1=${file%.json}
	name=${tmp1##*Op.}
	name2=${name%-Request}_request
	classname=extended_${name2##Extended-}
	convert $file $classname
done

