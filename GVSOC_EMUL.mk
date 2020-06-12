include common.mk

ifeq ($(AT_INPUT_WIDTH), 224)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_224.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 192)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_192.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 160)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_160.ppm
endif
ifeq ($(AT_INPUT_WIDTH), 128)
	IMAGE=$(CURDIR)/images/ILSVRC2012_val_00011158_128.ppm
endif

TEST_DIR=test_gvsoc_emul
GVSOC=$(TEST_DIR)/$(MODEL_PREFIX)_gvsoc.txt
EMUL=$(TEST_DIR)/$(MODEL_PREFIX)_emul.txt
MAIN=$(TEST_DIR)/gvsoc_vs_emul.c
NNTOOL_SCRIPT=models/nntool_script_test
MODEL_L2_MEMORY=200000

$(EMUL):
	make -f emul.mk clean all MAIN=$(MAIN) MODEL_ID=$(MODEL_ID) NNTOOL_SCRIPT=$(NNTOOL_SCRIPT) MODEL_L2_MEMORY=$(MODEL_L2_MEMORY)
	./$(MODEL_PREFIX)_emul $(IMAGE) > $@

$(GVSOC):
	make clean all run platform=gvsoc MAIN=$(MAIN) MODEL_ID=$(MODEL_ID) NNTOOL_SCRIPT=$(NNTOOL_SCRIPT) MODEL_L2_MEMORY=$(MODEL_L2_MEMORY) > $@

check: $(EMUL) $(GVSOC)
	python3 $(TEST_DIR)/parseout.py $^ $(MODEL_PREFIX) $(TEST_DIR)/out.txt

clean:
	rm $(TEST_DIR)/$(MODEL_PREFIX)*.txt

clean_all:
	rm $(TEST_DIR)/*.txt
