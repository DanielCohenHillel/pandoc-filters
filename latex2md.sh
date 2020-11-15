# mkdir -p gfx/from_pgf

# tmpfile=$(mktemp /tmp/pgf_template.XXXXXX)

# cat pgf_template.tex > "$tmpfile"

# sed -i 's/REPLACE_WITH_PGF_FILE_LOCATION/you daniel/g' "$tmpfile"

# cat "$tmpfile"

# pandoc --toc --standalone --mathjax --atx-headers -f latex -t markdown main.tex -o main.md -F ./newfilter.py
pandoc --toc --standalone --mathjax --atx-headers -f latex -t html main.tex -o csqc.html -F ./newfilter.py