import re
import os
import sys

tex_files = []

for tup in os.walk('.'):
    files = tup[2]
    for f in files:
        if f[-4:]=='.tex':
            tex_files.append(tup[0] +'\\'+ f)
for file in tex_files:
    print('\33[1m \33[34m=>\33[0m ' + file)

for file in tex_files:
    with open(file, 'r', encoding='UTF-8') as f:
        print(file, end='\n\33[1m\33[34m---------------------------------------\33[0m\n')
        file_txt = f.read()

# === REGEX ===
# find:    \\(input|include)(\{.*pgf\})
# replace: \includegraphics$2