#!/usr/bin/env python3

import csv
import sys
import sqlite3
import re
import subprocess
import os.path

import pypandoc
import psycopg2
import psycopg2.extras
import requests
from PIL import Image

def md2tex_old(md):
    # guillemets
    t = md.replace('%', '\\%').replace('$', '\\$').replace('{', '\\{')
    t = t.replace('&#x27;',"'").replace('&quot;','"')
    t = t.replace('}', '\\}').replace('&', '\\&')
    t = t.replace(' ',' ').replace(' ',' ').replace('’',"'")
    t = re.sub(r'__(.*?)__', r'\\underline{\1}', t)
    #t = re.sub(r'_(.*?)_', r'\\emph{\1}', t)
    t = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', t)
    t = re.sub(r'\*(.*?)\*', r'\\textbf{\1}', t)
    t = re.sub('^#*', '', t)
    t = t.replace('#', '\\#').replace('_', '\\_')
    t = t.replace('°', '\\degree{}').replace('€', '\\euro{}').replace('²', '\\textsuperscript{2}')
    t = t.replace('➞','\\ding{219}').replace('Φ','\\textPhi ').replace('λ','\\textlambda ')
    t = t.replace('',"'").replace('',"'")
    t = t.replace('«', ' \\og ').replace('»', ' \\fg ')
    t = t.replace('\n','\\\\'+crlf)
    # markdown links
    t = re.sub(r'\[(.*?)\]\((http.*?)\)', r'\\href{\2}{\1}',t)
    t = re.sub(r'\[(http.*?)\]', r'\\href{\1}{\1}',t)
    t = re.sub(r'\[(.*?)\]', r'\1',t)
    return(t)


def md2tex(md):
    if not md:
        return ''
    md = md.replace('&#x27;',"'").replace('&quot;','"')
    md = md.replace('°', '\\degree{}').replace('€', '\\euro{}').replace('²', '\\textsuperscript{2}')
    # ajout liens manquants
    md = re.sub(r'(^|[^(])(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)($|[^)])',r'[\2](\2)',md)
    # suppression des images du code markdown
    md = re.sub(re.compile('!(\[|\().*?\)', re.MULTILINE), r'', md.replace('\n]',']'))
    md = pypandoc.convert_text(md, 'tex', format='md').replace('\\tightlist','')
    return md


def data2tex(datagouv):
  org = ''
  for data in datagouv:
    if org != data['name']:
        # changement d'organisation
        org = data['name']
        logo = None
        if data['logo'] != '':
            logo = data['logo'].replace('https://static.data.gouv.fr/avatars/','').replace('/','_')
            logo = 'images/orga/'+ logo
            if not os.path.isfile(logo):
                r = requests.get(data['logo'])
                print('GET',data['logo'],logo)
                if r.status_code == 200:
                    if logo:
                        with open(logo, 'wb') as fd:
                            for chunk in r.iter_content(chunk_size=1024):
                                fd.write(chunk)
                        if r.headers['content-type'] == 'image/gif':
                            gif = Image.open(logo)
                            logo = logo.replace('.gif','.png')
                            gif.save(logo)
                else:
                    logo = None
            else:
                logo = logo.replace('.gif','.png')

        if logo and data['description_org'] != '':
            out.write(crlf+"""
\\clearpage
\\section{%(name)s}
\\fbox{
  \\begin{minipage}{0.95\\textwidth}
    \\begin{wrapfigure}{r}{%(width)s}
      \\centering
      \\includegraphics[width=%(width)s]{%(logo)s}
    \\end{wrapfigure}
  %(description)s
  \\end{minipage}
}

""" % {'name': md2tex(data['name']),
       'width': qrcode_width,
       'description': md2tex(data['description_org']),
       'logo': logo,
       'qr': 'https://data.gouv.fr/organization/'+data['organization_id']}
            )
        elif data['description_org'] != '':
            out.write(crlf+"""
\\clearpage
\\section{%(name)s}
\\fbox{
  \\begin{minipage}{0.95\\textwidth}
  %(description)s
  \\end{minipage}
}
\\vspace{1cm}

""" % {'name': md2tex(data['name']),
       'width': '3cm',
       'description': md2tex(data['description_org']),
       'qr': 'https://data.gouv.fr/organization/'+data['organization_id']}
            )


    # génération du QRcode
    #out.write(crlf+'\\pagebreak'+crlf)
    if data['id']=='z58301bbb88ee3809c3c65bb3':
        print(data)
        m = data['description']
        m = re.sub(re.compile('!(\[|\().*?\)', re.MULTILINE), r'', m.replace('\n]',']'))
        print(m)
        exit()
    out.write('\\addcontentsline{toc}{subsection}{%s}' % (md2tex(data['title'].capitalize()), ) + crlf)
    out.write('\\subsection*{%s}' % (md2tex(data['title'].capitalize(), )) + crlf+crlf)
    if data['tags']:
        for mot in data['tags'].split(','):
            out.write('\\index{%s}' % (mot.replace('-','!'),))
    out.write(crlf+'\\noindent'+crlf)
    out.write(md2tex(data['description'])+crlf)
    out.write("""
\\par
\\noindent
\\hrulefill
\\begin{samepage}
  \\begin{wrapfigure}{r}{%(width)s}
    \\centering
    \\qrcode[nolink]{%(url)s}
  \\end{wrapfigure}
""" % {'width': qrcode_width, 'url': "https://data.gouv.fr/dataset/"+data['id']} + crlf)
    out.write('\\noindent'+crlf)
    out.write('Licence : \\textbf{%s}\\par' % (md2tex(data['license'] if data['license'] != '' else 'non renseignée'),)+crlf+crlf)

    out.write('\\noindent'+crlf)
    out.write('Créé le : %s\\par' % (str(data['created_at'])[:10], )+crlf+crlf)
    out.write('\\noindent'+crlf)
    out.write('Modifié le : %s\\par' % (str(data['last_modified'])[:10], )+crlf+crlf)

    if data['temporal_coverage.start'] and data['temporal_coverage.end']:
        out.write('\\noindent'+crlf)
        out.write('De %s à %s\\par' % (str(data['temporal_coverage.start'])[:10], str(data['temporal_coverage.end'])[:10])+crlf+crlf)
    if data['spatial.granularity'] in gran:
        out.write('\\noindent'+crlf)
        out.write('Granularité : %s\\par' % (gran[data['spatial.granularity']], )+crlf+crlf)
    if data['frequency'] in freq:
        out.write('\\noindent'+crlf)
        out.write('Mise à jour : %s\\par' % (freq[data['frequency']], )+crlf+crlf)
    out.write('\\noindent'+crlf)
    out.write('Mots-clé : \\emph{%s}\\par' % (md2tex(data['tags'] if data['tags'] and data['tags'] != '' else 'aucun').replace(',',', ',))+crlf+crlf)
    out.write('\\noindent'+crlf)
    out.write('Permalien : \\url{%s}\\par' % (site_url+'dataset/'+data['id'], )+crlf)
    out.write("""
\\end{samepage}
\\vspace{0.5cm}
""")


out = open('datagouv.tex','w')
crlf = '\x0d\x0a'
out.write("""\\documentclass[a4paper, 12pt]{book}
\\usepackage[utf8]{inputenc}
\\usepackage[T1]{fontenc}
\\usepackage[frenchb]{babel}
\\usepackage{makeidx}
\\usepackage{hyperref}
\\usepackage{gensymb}
\\usepackage{eurosym}
\\usepackage{pifont}
\\usepackage{textgreek}
\\usepackage{imakeidx}
\\usepackage{wrapfig}
\\usepackage{graphicx}

\\usepackage{qrcode}

\\makeindex[intoc]

\\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    filecolor=magenta,      
    urlcolor=blue,
}
\\title{data.gouv.fr}
\\author{Etalab}
\\date{2019-04-01} 

\\begin{document}

\\frontmatter

\\section*{Préface}

\\paragraph{}
\\emph{data.gouv.fr} est le portail unique interministériel destiné à rassembler et à mettre à disposition librement l'ensemble des informations publiques de l'Etat, de ses établissements publics administratifs et, si elles le souhaitent, des collectivités territoriales et des personnes de droit public ou de droit privé chargées d'une mission de service public.
(décret n\\degree 2011-194 du 21 février 2011)
\\begin{center} 
Vous avez entre les main la toute première édition papier de \\emph{data.gouv.fr}\\\\
Elle a été produite par \\emph{Etalab \\& Alumni}, avec le langage \\LaTeX.
\\end{center}

\\tableofcontents

\\mainmatter

\\chapter{Données de référence}

Ce chapitre liste les jeux de données de référence définis par le \\href{https://www.legifrance.gouv.fr/affichTexte.do?cidTexte=JORFTEXT000034194946&categorieLien=id}{décret n\\degree 2017-331} du 14 mars 2017 relatif au service public de mise à disposition des données de référence codifié dans l'\\href{https://www.legifrance.gouv.fr/affichCodeArticle.do;jsessionid=19672D71250ADD261EC92AD65C5FE97B.tplgfr36s_3?cidTexte=LEGITEXT000031366350&idArticle=LEGIARTI000034196073&categorieLien=id#LEGIARTI000034196073}{article R321-5 et suivants du Code des Relations entre le Public et l'Administration}.
\\par
\\noindent
Voir aussi \\url{https://www.data.gouv.fr/fr/reference}

\\clearpage

\\chapter{Données des services publics certifiés}

Ce chapitre liste les jeux de données produits par les services publics répertoriés sur le portail national \\href{https://data.gouv.fr/}{data.gouv.fr}.

\\clearpage

"""+crlf)


site_url = 'https://data.gouv.fr/'
qrcode_width = '2.5cm'
freq = {'annual': 'annuelle',
        'punctual': 'ponctuelle',
        'irregular': 'irrégulière',
        'monthly': 'mensuelle',
        'quarterly': 'trimestrielle',
        'continue': 'continue',
        'semiannual': 'semestrielle',
        'daily': 'quotienne',
        'weekly': 'hebdomadaire',
        'biweekly': 'bi-hebdomadaire',
        'bimonthly': 'bi-mesnsuelle' }
gran = {'fr:commune': 'à la commune',
        'country': 'au pays',
        'fr:departement': 'au département',
        'fr:epci': "à l'EPCI",
        'fr:region': 'à la région',
        'poi': "au point d'intérêt",
        'fr:canton': 'au canton',
        'fr:iris': "à l'IRIS INSEE",
        'fr:collectivite': 'à la collectivité' }
crlf='\x0d\x0a'



if len(sys.argv)>1:
    csv.field_size_limit(250000)
    datagouv = csv.DictReader(open(sys.argv[1], 'r'))
else:
    pg = psycopg2.connect("dbname=datagouv")
    db = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)
    db.execute("""select * from datagouv_data where badges ~ 'certified' order by name,title limit 100""")
    datagouv = db.fetchall()

data2tex(datagouv)

out.write("""

\\clearpage

\\chapter{Autres jeux de données}

Ce chapitre liste les autres jeux de données disponibles sur \\emph{data.gouv.fr}.
""")

if len(sys.argv)<2:
    pg = psycopg2.connect("dbname=datagouv")
    db = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)
    db.execute("""select * from datagouv_data where badges !~ 'certified' order by name,title limit 100""")
    datagouv = db.fetchall()

data2tex(datagouv)

out.write("""
\\backmatter

\\printindex

\\end{document}
""")
