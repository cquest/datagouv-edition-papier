rm -f datagouv.* \
&& ./make_latex.py \
&& xelatex datagouv.tex > log \
&& xelatex datagouv.tex > log

