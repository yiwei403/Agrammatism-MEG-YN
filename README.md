# Scripts for Spatiotemporal dynamics of lexical and morphosyntactic planning during language production revealed by magnetoencephalography

[![DOI](https://zenodo.org/badge/944254584.svg)](https://zenodo.org/badge/latestdoi/944254584)

## preprint

[![bioRxiv](https://img.shields.io/badge/bioRxiv-10.64898%2F2026.09.17.752155-B31B1B)](https://doi.org/10.64898/2026.09.17.752155)

## data

[![Zenodo](https://img.shields.io/badge/Zenodo-10.5281%2Fzenodo.22904305-1682D4)](https://doi.org/10.5281/zenodo.22904305)

## 

- `s01_zenodo_pipelineSetup.py`
    - general experiment analysis setup. 
- `s02_zenodo_compare_emg_ICAsource.py`
    - calculated the correlation between the EMG averaged epoch data and each of the first twenty ICA components’ averaged epoch data. 
    - Any ICA components that had a correlation coefficient higher than 0.4 were excluded as arising from speech movement artifacts.
- `s03_zenodo_analysis_surface_source.py`
    - generates Figure 2 & 3
    - generates all the results in section 3.2 and 3.3 
- `s04_zenodo_plot_sig_results_from_surface_source_analysis.py`
    - generates Figure 4 - 12
    - generates table 1-9
    - generates supplementary table S1 - S4
- `s05_zenodo_analysis_surface_source_regression.py`
    - generates supplementary Figure S4
    - generates supplementary Table S5
- `MEGspeechOnsetTimeStats_zenodo.Rmd`
    - generates result in section 3.1
    - geenrates supplementary Figure S3