#!/usr/bin/env python3.8

import sys
from contextlib import ExitStack

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import os
from PyPDF2 import PdfWriter


# function to draw the table from a Dataframe
def _draw_as_table(df, pagesize):
    alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
    alternating_colors = alternating_colors[:len(df)]
    fig, ax = plt.subplots(figsize=pagesize)
    ax.axis('tight')
    ax.axis('off')
    # df.style.apply(qc_fail_background, subset=['js_score', 'qc_pass'], axis=1)

    colours = [['white' if not np.issubdtype(type(val), np.number) or val < 0.1 else 'coral' for val in row]
               # for row in df.values]
               # colours = [['coral' if val>0.1 else 'white' for val in row]
               # possible alternative cellColours=alternating_colors
               for row in df.values]
    the_table = ax.table(cellText=df.values,
                         rowLabels=df.index,
                         colLabels=df.columns,

                         rowColours=['lightblue'] * len(df),
                         colColours=['lightblue'] * len(df.columns),
                         cellColours=colours,
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


def merge_pdf(input_files, output_dir):
    merger = PdfWriter()
    # add the first page of input1 document to output
    merger.append(fileobj=input_files[0], pages=(0, 1))

    # add the page 0 to n of input_i document to output in position k
    # merger.merge(position= k , fileobj=input_i, pages=(0, n))

    for i in range(1, len(input_files)):
        # insert the first page of input2 into the output beginning after the second page
        merger.merge(position=i, fileobj=input_files[i], pages=(0, 1))
        # merger.merge(position=i, fileobj=input_files[i]) #entire file

    # Write to an output PDF document
    output_path = os.path.join(output_dir, 'document-output.pdf')
    output = open(output_path, "wb")
    merger.write(output)

    # Close File Descriptors
    merger.close()
    output.close()


def qc_fail_background(row):
    highlight = 'background-color: lightcoral;'
    default = ''

    # must return one string per cell in this row
    if row['js_score'] > 0.1:
        return [highlight, highlight]
    else:
        return [default, default]


def main():
    print("start of processing")
    path = os.path.join(input_dir, 'qc_js_univariate.csv')

    df = pd.read_csv(path)
    file_name_csv = os.path.basename(path).split('/')[-1]
    file_name = file_name_csv[:-4] + '.pdf'
    output_file = os.path.join(output_dir, file_name)
    df.style.apply(qc_fail_background, subset=['js_score', 'qc_pass'], axis=1)
    dataframe_to_pdf(df, output_file)
    input_pdf_files = ['js_1d.pdf', 'js_1d_control.pdf', 'js_CD4.pdf', 'univariate_all.pdf', 'univariate_control.pdf']
    input_pdf_paths = [os.path.join(input_dir, f) for f in input_pdf_files]
    input_files = [output_file]
    with ExitStack() as stack:
        input_files.extend([stack.enter_context(open(pdf, 'rb')) for pdf in input_pdf_paths])
        merge_pdf(input_files, output_dir)
    print("end of processing")


if __name__ == '__main__':
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]
    try:
        main()
    except Exception as e:
        import traceback

        error_log = os.path.join(output_dir, "qcpdf-errors.txt")
        error_message = traceback.format_exc()
        with open(error_log, 'w') as error_log_file:
            print(error_message, file=error_log_file)
