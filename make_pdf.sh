./make_latex.py \
&& cat includes/header.tex datagouv.tex includes/footer.tex > final.tex \
&& xelatex final.tex  \
&& xelatex final.tex 

