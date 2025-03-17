#!/bin/sh

conda create -n cgal_env python==3.9 && \
conda activate cgal_env && \
conda install -c conda-forge cgal && \
conda install -c fredboudon -c conda-forge pyqglviewer
