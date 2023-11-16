#!/usr/bin/env python3.8

import sys
import shutil

import pdfkit
import pandas as pd
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
import sqlite3
from pypdf import PdfMerger


# function to draw the table from a Dataframe
def _draw_as_table(df, pagesize):
    alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
    alternating_colors = alternating_colors[:len(df)]
    fig, ax = plt.subplots(figsize=pagesize)
    ax.axis('tight')
    ax.axis('off')
    the_table = ax.table(cellText=df.values,
                         rowLabels=df.index,
                         colLabels=df.columns,
                         rowColours=['lightblue'] * len(df),
                         colColours=['lightblue'] * len(df.columns),
                         cellColours=alternating_colors,
                         loc='center')
    return fig


# dataframe to pdf converter function
def dataframe_to_pdf(df, filename, numpages=(1, 1), pagesize=(11, 8.5)):
    with PdfPages(filename) as pdf:
        nh, nv = numpages
        rows_per_page = len(df) // nh
        cols_per_page = len(df.columns) // nv
        for i in range(0, nh):
            for j in range(0, nv):
                page = df.iloc[(i * rows_per_page):min((i + 1) * rows_per_page, len(df)),
                       (j * cols_per_page):min((j + 1) * cols_per_page, len(df.columns))]
                fig = _draw_as_table(page, pagesize)
                if nh > 1 or nv > 1:
                    # Add a part/page number at bottom-center of page
                    fig.text(0.5, 0.5 / pagesize[0],
                             "Part-{}x{}: Page-{}".format(i + 1, j + 1, i * nv + j + 1),
                             ha='center', fontsize=8)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close()


print("start of processing")
input_dir = sys.argv[1]
output_dir = sys.argv[2]

pdf_files = []
directory = os.fsencode(input_dir)
for file in os.listdir(directory):
    filename = os.fsdecode(file)
    if filename.endswith(".csv"):
        path = os.path.join(input_dir, filename)
        df = pd.read_csv(path)
        file_name_csv = os.path.basename(path).split('/')[-1]
        file_name = file_name_csv[:-4] + '.pdf'
        output_file = os.path.join(output_dir, file_name)
        dataframe_to_pdf(df, output_file)
        pdf_files.append(output_file)
        continue
    else:
        continue

merger = PdfMerger()

for pdf in pdf_files:
    merger.append(pdf)

output_file = os.path.join(output_dir, 'merged.pdf')
merger.write(output_file)
merger.close()

print("end of processing")
