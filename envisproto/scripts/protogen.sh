#!/bin/bash

mkdir -p ./src/gen
mkdir -p ./src/gen/cpp
mkdir -p ./src/gen/python

# protoc -I=../src/envisproto/                                        \
#        ../src/envisproto/commons/*.proto                            \
#        ../src/envisproto/execution/*.proto                          \
#        ../src/envisproto/state/*.proto                              \
#        ../src/envisproto/tensors/*.proto                            \
#        --python_out=../src/gen  

workdir=$1
# cd $workdir

protoc -I=. --cpp_out=./src/gen/cpp envisproto/commons/*.proto
protoc -I=. --cpp_out=./src/gen/cpp envisproto/state/*.proto
protoc -I=. --cpp_out=./src/gen/cpp envisproto/execution/*.proto
protoc -I=. --cpp_out=./src/gen/cpp envisproto/tensors/*.proto


# generate python stubs
protoc -I=. --python_out=./src/gen/python envisproto/commons/*.proto
protoc -I=. --python_out=./src/gen/python envisproto/state/*.proto
protoc -I=. --python_out=./src/gen/python envisproto/execution/*.proto
protoc -I=. --python_out=./src/gen/python envisproto/tensors/*.proto
echo "" > ./src/gen/python/envisproto/__init__.py