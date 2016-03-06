from statuter.loader import extract_pages
import os
import argparse

parser = argparse.ArgumentParser(description='Extract RSC textual data.')
parser.add_argument('input', help='Input RSC xml file')
parser.add_argument('eng', help='Output English markdown file')
parser.add_argument('fra', help='Output French markdown file')
parser.add_argument('pages', help='Page numbers in x-y format')

input_args = parser.parse_args()

pages = input_args.pages.split('-')
pages = [int(page) for page in pages]
pages = range(pages[0], pages[1] + 1)

current_dir = os.path.dirname(os.path.realpath(__file__))

eng = input_args.eng
fra = input_args.fra

if not os.path.isabs(eng):
    eng = os.path.join(current_dir, eng)
if not os.path.isabs(fra):
    fra = os.path.join(current_dir, fra)

if not os.path.exists(os.path.dirname(eng)):
    os.mkdir(os.path.dirname(eng))
if not os.path.exists(os.path.dirname(fra)):
    os.mkdir(os.path.dirname(fra))

extract_pages(input_args.input, eng, fra, pages)
