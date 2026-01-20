#!/usr/bin/bash

##########################################################################################################
#
# Последовательный запуск экспериментов.
#
##########################################################################################################

echo "=============================================="
time python workflow.py 'workflows/samples/Cancer breast calcification за 20 лет/PMC_biomedical-ner-all.yaml'

echo "=============================================="
time python workflow.py 'workflows/samples/Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0.yaml'

echo "=============================================="
time python workflow.py 'workflows/samples/Cancer breast calcification за 20 лет/PMC_OpenBioNER.yaml'

echo "=============================================="
time python workflow.py 'workflows/samples/Cancer breast calcification за 20 лет/PMC_pos-based-hybrid.yaml'
