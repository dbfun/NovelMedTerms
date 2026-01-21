#!/usr/bin/bash

##########################################################################################################
#
# Группировка результатов в каталоги.
#
##########################################################################################################


###########################################
#
# Cancer breast calcification за 20 лет
#
###########################################

mkdir -p 'сравнение/Cancer breast calcification за 20 лет/statistics'
mkdir -p 'сравнение/Cancer breast calcification за 20 лет/Динамика POS-структур по годам, кроме униграмм'
mkdir -p 'сравнение/Cancer breast calcification за 20 лет/Динамика покрытия извлеченных терминов словарями'
mkdir -p 'сравнение/Cancer breast calcification за 20 лет/Доля POS-структур по годам, кроме униграмм'
mkdir -p 'сравнение/Cancer breast calcification за 20 лет/Количество POS-структур по годам, кроме униграмм'
mkdir -p 'сравнение/Cancer breast calcification за 20 лет/Количество извлеченных терминов их покрытие словарями'
mkdir -p 'сравнение/Cancer breast calcification за 20 лет/Облако терминов'

cp 'Cancer breast calcification за 20 лет/PMC_biomedical-ner-all/statistics.xlsx' 'сравнение/Cancer breast calcification за 20 лет/statistics/PMC_biomedical-ner-all.xlsx'
cp 'Cancer breast calcification за 20 лет/PMC_biomedical-ner-all/Динамика POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Динамика POS-структур по годам, кроме униграмм/PMC_biomedical-ner-all.png'
cp 'Cancer breast calcification за 20 лет/PMC_biomedical-ner-all/Динамика покрытия извлеченных терминов словарями.png' 'сравнение/Cancer breast calcification за 20 лет/Динамика покрытия извлеченных терминов словарями/PMC_biomedical-ner-all.png'
cp 'Cancer breast calcification за 20 лет/PMC_biomedical-ner-all/Доля POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Доля POS-структур по годам, кроме униграмм/PMC_biomedical-ner-all.png'
cp 'Cancer breast calcification за 20 лет/PMC_biomedical-ner-all/Количество POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Количество POS-структур по годам, кроме униграмм/PMC_biomedical-ner-all.png'
cp 'Cancer breast calcification за 20 лет/PMC_biomedical-ner-all/Количество извлеченных терминов их покрытие словарями.png' 'сравнение/Cancer breast calcification за 20 лет/Количество извлеченных терминов их покрытие словарями/PMC_biomedical-ner-all.png'
cp 'Cancer breast calcification за 20 лет/PMC_biomedical-ner-all/Облако терминов.csv' 'сравнение/Cancer breast calcification за 20 лет/Облако терминов/PMC_biomedical-ner-all.csv'
cp 'Cancer breast calcification за 20 лет/PMC_biomedical-ner-all/Облако терминов.png' 'сравнение/Cancer breast calcification за 20 лет/Облако терминов/PMC_biomedical-ner-all.png'

###########################################

cp 'Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0/statistics.xlsx' 'сравнение/Cancer breast calcification за 20 лет/statistics/PMC_gliner-biomed-bi-large-v1.0.xlsx'
cp 'Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Динамика POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Динамика POS-структур по годам, кроме униграмм/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Динамика покрытия извлеченных терминов словарями.png' 'сравнение/Cancer breast calcification за 20 лет/Динамика покрытия извлеченных терминов словарями/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Доля POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Доля POS-структур по годам, кроме униграмм/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Количество POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Количество POS-структур по годам, кроме униграмм/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Количество извлеченных терминов их покрытие словарями.png' 'сравнение/Cancer breast calcification за 20 лет/Количество извлеченных терминов их покрытие словарями/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Облако терминов.csv' 'сравнение/Cancer breast calcification за 20 лет/Облако терминов/PMC_gliner-biomed-bi-large-v1.0.csv'
cp 'Cancer breast calcification за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Облако терминов.png' 'сравнение/Cancer breast calcification за 20 лет/Облако терминов/PMC_gliner-biomed-bi-large-v1.0.png'

###########################################

cp 'Cancer breast calcification за 20 лет/PMC_OpenBioNER/statistics.xlsx' 'сравнение/Cancer breast calcification за 20 лет/statistics/PMC_OpenBioNER.xlsx'
cp 'Cancer breast calcification за 20 лет/PMC_OpenBioNER/Динамика POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Динамика POS-структур по годам, кроме униграмм/PMC_OpenBioNER.png'
cp 'Cancer breast calcification за 20 лет/PMC_OpenBioNER/Динамика покрытия извлеченных терминов словарями.png' 'сравнение/Cancer breast calcification за 20 лет/Динамика покрытия извлеченных терминов словарями/PMC_OpenBioNER.png'
cp 'Cancer breast calcification за 20 лет/PMC_OpenBioNER/Доля POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Доля POS-структур по годам, кроме униграмм/PMC_OpenBioNER.png'
cp 'Cancer breast calcification за 20 лет/PMC_OpenBioNER/Количество POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Количество POS-структур по годам, кроме униграмм/PMC_OpenBioNER.png'
cp 'Cancer breast calcification за 20 лет/PMC_OpenBioNER/Количество извлеченных терминов их покрытие словарями.png' 'сравнение/Cancer breast calcification за 20 лет/Количество извлеченных терминов их покрытие словарями/PMC_OpenBioNER.png'
cp 'Cancer breast calcification за 20 лет/PMC_OpenBioNER/Облако терминов.csv' 'сравнение/Cancer breast calcification за 20 лет/Облако терминов/PMC_OpenBioNER.csv'
cp 'Cancer breast calcification за 20 лет/PMC_OpenBioNER/Облако терминов.png' 'сравнение/Cancer breast calcification за 20 лет/Облако терминов/PMC_OpenBioNER.png'

###########################################

cp 'Cancer breast calcification за 20 лет/PMC_pos-based-hybrid/statistics.xlsx' 'сравнение/Cancer breast calcification за 20 лет/statistics/PMC_pos-based-hybrid.xlsx'
cp 'Cancer breast calcification за 20 лет/PMC_pos-based-hybrid/Динамика POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Динамика POS-структур по годам, кроме униграмм/PMC_pos-based-hybrid.png'
cp 'Cancer breast calcification за 20 лет/PMC_pos-based-hybrid/Динамика покрытия извлеченных терминов словарями.png' 'сравнение/Cancer breast calcification за 20 лет/Динамика покрытия извлеченных терминов словарями/PMC_pos-based-hybrid.png'
cp 'Cancer breast calcification за 20 лет/PMC_pos-based-hybrid/Доля POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Доля POS-структур по годам, кроме униграмм/PMC_pos-based-hybrid.png'
cp 'Cancer breast calcification за 20 лет/PMC_pos-based-hybrid/Количество POS-структур по годам, кроме униграмм.png' 'сравнение/Cancer breast calcification за 20 лет/Количество POS-структур по годам, кроме униграмм/PMC_pos-based-hybrid.png'
cp 'Cancer breast calcification за 20 лет/PMC_pos-based-hybrid/Количество извлеченных терминов их покрытие словарями.png' 'сравнение/Cancer breast calcification за 20 лет/Количество извлеченных терминов их покрытие словарями/PMC_pos-based-hybrid.png'
cp 'Cancer breast calcification за 20 лет/PMC_pos-based-hybrid/Облако терминов.csv' 'сравнение/Cancer breast calcification за 20 лет/Облако терминов/PMC_pos-based-hybrid.csv'
cp 'Cancer breast calcification за 20 лет/PMC_pos-based-hybrid/Облако терминов.png' 'сравнение/Cancer breast calcification за 20 лет/Облако терминов/PMC_pos-based-hybrid.png'


###########################################
#
# CRISPR gene therapy за 20 лет
#
###########################################

mkdir -p 'сравнение/CRISPR gene therapy за 20 лет/statistics'
mkdir -p 'сравнение/CRISPR gene therapy за 20 лет/Динамика POS-структур по годам, кроме униграмм'
mkdir -p 'сравнение/CRISPR gene therapy за 20 лет/Динамика покрытия извлеченных терминов словарями'
mkdir -p 'сравнение/CRISPR gene therapy за 20 лет/Доля POS-структур по годам, кроме униграмм'
mkdir -p 'сравнение/CRISPR gene therapy за 20 лет/Количество POS-структур по годам, кроме униграмм'
mkdir -p 'сравнение/CRISPR gene therapy за 20 лет/Количество извлеченных терминов их покрытие словарями'
mkdir -p 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов'

cp 'CRISPR gene therapy за 20 лет/PMC_biomedical-ner-all/statistics.xlsx' 'сравнение/CRISPR gene therapy за 20 лет/statistics/PMC_biomedical-ner-all.xlsx'
cp 'CRISPR gene therapy за 20 лет/PMC_biomedical-ner-all/Динамика POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Динамика POS-структур по годам, кроме униграмм/PMC_biomedical-ner-all.png'
cp 'CRISPR gene therapy за 20 лет/PMC_biomedical-ner-all/Динамика покрытия извлеченных терминов словарями.png' 'сравнение/CRISPR gene therapy за 20 лет/Динамика покрытия извлеченных терминов словарями/PMC_biomedical-ner-all.png'
cp 'CRISPR gene therapy за 20 лет/PMC_biomedical-ner-all/Доля POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Доля POS-структур по годам, кроме униграмм/PMC_biomedical-ner-all.png'
cp 'CRISPR gene therapy за 20 лет/PMC_biomedical-ner-all/Количество POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Количество POS-структур по годам, кроме униграмм/PMC_biomedical-ner-all.png'
cp 'CRISPR gene therapy за 20 лет/PMC_biomedical-ner-all/Количество извлеченных терминов их покрытие словарями.png' 'сравнение/CRISPR gene therapy за 20 лет/Количество извлеченных терминов их покрытие словарями/PMC_biomedical-ner-all.png'
cp 'CRISPR gene therapy за 20 лет/PMC_biomedical-ner-all/Облако терминов.csv' 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов/PMC_biomedical-ner-all.csv'
cp 'CRISPR gene therapy за 20 лет/PMC_biomedical-ner-all/Облако терминов.png' 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов/PMC_biomedical-ner-all.png'

###########################################

cp 'CRISPR gene therapy за 20 лет/PMC_gliner-biomed-bi-large-v1.0/statistics.xlsx' 'сравнение/CRISPR gene therapy за 20 лет/statistics/PMC_gliner-biomed-bi-large-v1.0.xlsx'
cp 'CRISPR gene therapy за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Динамика POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Динамика POS-структур по годам, кроме униграмм/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'CRISPR gene therapy за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Динамика покрытия извлеченных терминов словарями.png' 'сравнение/CRISPR gene therapy за 20 лет/Динамика покрытия извлеченных терминов словарями/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'CRISPR gene therapy за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Доля POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Доля POS-структур по годам, кроме униграмм/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'CRISPR gene therapy за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Количество POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Количество POS-структур по годам, кроме униграмм/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'CRISPR gene therapy за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Количество извлеченных терминов их покрытие словарями.png' 'сравнение/CRISPR gene therapy за 20 лет/Количество извлеченных терминов их покрытие словарями/PMC_gliner-biomed-bi-large-v1.0.png'
cp 'CRISPR gene therapy за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Облако терминов.csv' 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов/PMC_gliner-biomed-bi-large-v1.0.csv'
cp 'CRISPR gene therapy за 20 лет/PMC_gliner-biomed-bi-large-v1.0/Облако терминов.png' 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов/PMC_gliner-biomed-bi-large-v1.0.png'

###########################################

cp 'CRISPR gene therapy за 20 лет/PMC_OpenBioNER/statistics.xlsx' 'сравнение/CRISPR gene therapy за 20 лет/statistics/PMC_OpenBioNER.xlsx'
cp 'CRISPR gene therapy за 20 лет/PMC_OpenBioNER/Динамика POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Динамика POS-структур по годам, кроме униграмм/PMC_OpenBioNER.png'
cp 'CRISPR gene therapy за 20 лет/PMC_OpenBioNER/Динамика покрытия извлеченных терминов словарями.png' 'сравнение/CRISPR gene therapy за 20 лет/Динамика покрытия извлеченных терминов словарями/PMC_OpenBioNER.png'
cp 'CRISPR gene therapy за 20 лет/PMC_OpenBioNER/Доля POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Доля POS-структур по годам, кроме униграмм/PMC_OpenBioNER.png'
cp 'CRISPR gene therapy за 20 лет/PMC_OpenBioNER/Количество POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Количество POS-структур по годам, кроме униграмм/PMC_OpenBioNER.png'
cp 'CRISPR gene therapy за 20 лет/PMC_OpenBioNER/Количество извлеченных терминов их покрытие словарями.png' 'сравнение/CRISPR gene therapy за 20 лет/Количество извлеченных терминов их покрытие словарями/PMC_OpenBioNER.png'
cp 'CRISPR gene therapy за 20 лет/PMC_OpenBioNER/Облако терминов.csv' 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов/PMC_OpenBioNER.csv'
cp 'CRISPR gene therapy за 20 лет/PMC_OpenBioNER/Облако терминов.png' 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов/PMC_OpenBioNER.png'

###########################################

cp 'CRISPR gene therapy за 20 лет/PMC_pos-based-hybrid/statistics.xlsx' 'сравнение/CRISPR gene therapy за 20 лет/statistics/PMC_pos-based-hybrid.xlsx'
cp 'CRISPR gene therapy за 20 лет/PMC_pos-based-hybrid/Динамика POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Динамика POS-структур по годам, кроме униграмм/PMC_pos-based-hybrid.png'
cp 'CRISPR gene therapy за 20 лет/PMC_pos-based-hybrid/Динамика покрытия извлеченных терминов словарями.png' 'сравнение/CRISPR gene therapy за 20 лет/Динамика покрытия извлеченных терминов словарями/PMC_pos-based-hybrid.png'
cp 'CRISPR gene therapy за 20 лет/PMC_pos-based-hybrid/Доля POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Доля POS-структур по годам, кроме униграмм/PMC_pos-based-hybrid.png'
cp 'CRISPR gene therapy за 20 лет/PMC_pos-based-hybrid/Количество POS-структур по годам, кроме униграмм.png' 'сравнение/CRISPR gene therapy за 20 лет/Количество POS-структур по годам, кроме униграмм/PMC_pos-based-hybrid.png'
cp 'CRISPR gene therapy за 20 лет/PMC_pos-based-hybrid/Количество извлеченных терминов их покрытие словарями.png' 'сравнение/CRISPR gene therapy за 20 лет/Количество извлеченных терминов их покрытие словарями/PMC_pos-based-hybrid.png'
cp 'CRISPR gene therapy за 20 лет/PMC_pos-based-hybrid/Облако терминов.csv' 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов/PMC_pos-based-hybrid.csv'
cp 'CRISPR gene therapy за 20 лет/PMC_pos-based-hybrid/Облако терминов.png' 'сравнение/CRISPR gene therapy за 20 лет/Облако терминов/PMC_pos-based-hybrid.png'

