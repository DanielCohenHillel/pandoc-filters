#!/usr/bin/python3.8
"""
Pandoc filter to fix math numbering
"""

from panflute import *
import tempfile
import re
import os
import time
import logging
import subprocess
from pathlib import Path

def filter(elem, doc):

    # Make display math with labels be numbered (i.e. \begin{equation}...\end{equation})
    if type(elem) == Math and elem.format == 'DisplayMath' and '\\label' in elem.text:

        # Make labled equations numbered
        if '\\begin' not in elem.text:
            elem.text = '\\begin{equation}\n' + elem.text + '\n \\end{equation}'

        # Convert aligned to align
        if 'aligned' in elem.text or 'align' in elem.text:
            elem.text = elem.text.replace('\\begin{aligned}', '\\begin{align}')\
                .replace('\\end{aligned}', '\\end{align}')

    # Fix links to labeled equation using mathjac links
    if type(elem) == Link and 'reference-type' in elem.attributes:
        if elem.attributes['reference-type']=='eqref':
            return Math(f'\\eqref{{{elem.attributes["reference"]}}}', 'InlineMath')

        if elem.attributes['reference-type']=='ref':
            ref = elem.attributes['reference']
            chap_names = ['chap:', 'appen:', 'sec:']

            if any(name in ref for name in chap_names):
                elem.attributes = {}

            elif 'fig' in ref:
                pass

    if type(elem) == Image:
        fig_loc = (os.getcwd() + '/' + elem.url)
        density = 1000
        output_png = '.'.join(fig_loc.split('.')[:-1]) + '-gen.png'
        output_png_rel = '.'.join(elem.url.split('.')[:-1]) + '-gen.png'
        skip_existing = True

        logging.warning(elem.identifier)
        # elem.attributes = {'style': 'width:5px;'}
        if not os.path.exists(output_png) or not skip_existing:
            if elem.url[-4:] == '.pgf':
                logging.warning('\33[1m 📈 pgf:      \33[35m'+elem.url+'\33[0m')
                with tempfile.NamedTemporaryFile(suffix='.tex') as fp,\
                                tempfile.TemporaryDirectory() as tmp_dir:
                    place_holder = 'REPLACE_WITH_PGF_FILE_LOCATION'

                    template = open('pgf_template.tex', 'r').read().replace(place_holder, fig_loc)

                    with open(fp.name, 'w') as f:
                        f.write(template)

                    subprocess.run(f'pdflatex --output-directory {tmp_dir} {fp.name}',\
                        shell=True, capture_output=True)

                    pdf_file = tmp_dir+ '/' + fp.name.split('/')[-1][:-4] + '.pdf'
                    
                    subprocess.run(['convert', '-trim', '-density', str(density), pdf_file, '-transparent', 'white',
                                    '-quality', '100', '-sharpen', '0x1.0', '-colorspace', 'RGB', output_png], capture_output=True)

                    elem.url = elem.url[:-4] + '-gen.png'

            elif elem.url[-8:] == '.pdf_tex':
                logging.warning('\33[1m 📝 pdf_tex:  \33[34m'+elem.url+'\33[0m')
                with tempfile.NamedTemporaryFile(suffix='.pdf_tex') as fp,\
                                tempfile.TemporaryDirectory() as tmp_dir:
                    place_holder = 'REPLACE_WITH_PGF_FILE_LOCATION'

                    template = open('pgf_template.tex', 'r').read().replace(place_holder, fig_loc)

                    with open(fp.name, 'w') as f:
                        f.write(template)

                    a = subprocess.run(['pdflatex', '--output-directory', tmp_dir, fp.name], capture_output=True)

                    pdf_file = tmp_dir+ '/' + fp.name.split('/')[-1][:-8] + '.pdf'
                    
                    b = subprocess.run(['convert', '-trim', '-density', str(density), pdf_file, '-transparent', 'white',
                                    '-quality', '100', '-sharpen', '0x1.0', '-colorspace', 'RGB', output_png], capture_output=True)
                    if a.returncode or b.returncode:
                        logging.warning(f'\33[1m\33[31m ERROR:\33[0m a={a.returncode}  b={b.returncode}')

                    elem.url = elem.url[:-8] + '-gen.png'

            elif elem.url[-4:] == '.pdf':
                logging.warning('\33[1m 📑 pdf:      \33[33m'+elem.url+'\33[0m')

                if not os.path.exists(output_png) or not skip_existing:
                    subprocess.run(['convert', '-trim', '-density', str(density), fig_loc, '-transparent', 'white',
                                    '-quality', '100', '-sharpen', '0x1.0', '-colorspace', 'RGB', output_png], capture_output=True)
                else:
                    logging.warning('Skipping...')
                
                elem.url = elem.url[:-4] + '-gen.png'
            else:
                logging.warning('\33[1m 📷 Image:    \33[32m'+elem.url+'\33[0m (doing nothing)')
        else:
            elem.url = output_png_rel
            logging.warning('File exists, skipping...')

    # Remove header classes (GFM doesn't support, this is the {.unnumbered} etc...)
    if type(elem) == Header:
        elem.classes = []

def main(doc=None):
    return run_filter(filter, doc=doc)

if __name__ == "__main__":
    main()
