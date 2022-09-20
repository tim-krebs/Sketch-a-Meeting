#!/usr/bin/env sh

/home/testing/caffe/build/tools/caffe train \
    --solver=models/alexnet_finetune_genre/solver.prototxt \
    --weights=models/bvlc_alexnet.caffemodel
