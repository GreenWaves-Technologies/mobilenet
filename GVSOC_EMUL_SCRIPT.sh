#!/bin/bash
for i in {0..17}
do
   make -f GVSOC_EMUL.mk check MODEL_ID=${i}
done