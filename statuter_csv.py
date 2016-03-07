from statuter.loader import extract_pages
import os
import argparse
import csv

parser = argparse.ArgumentParser(description='Extract RSC textual data.')
parser.add_argument('input', help='Input RSC xml file')
parser.add_argument('toc', help='Input RSC table of contents CSV file')
parser.add_argument('eng', help='Output English markdown folder')
parser.add_argument('fra', help='Output French markdown folder')

input_args = parser.parse_args()
current_dir = os.path.dirname(os.path.realpath(__file__))

eng = input_args.eng
fra = input_args.fra

if not os.path.isabs(eng):
    eng = os.path.join(current_dir, eng)
if not os.path.isabs(fra):
    fra = os.path.join(current_dir, fra)

if not os.path.exists(eng):
    os.mkdir(eng)
if not os.path.exists(fra):
    os.mkdir(fra)

def page_range(pages):
    pages = pages.split('-')
    pages = [int(page) for page in pages]
    return range(pages[0], pages[1] + 1)

with open(input_args.toc, 'r') as toc_file:
    toc = csv.DictReader(toc_file)
    for act in toc:

        extract_pages(input_args.input, os.path.join(eng, act['Chapter'] + '.md'),
                      os.path.join(fra, act['Chapter'] + '.md'), page_range(act['Pages']))
