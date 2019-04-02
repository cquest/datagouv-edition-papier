#!/usr/bin/env python3

import re
import os.path

import pypandoc
import psycopg2
import psycopg2.extras
import requests
from PIL import Image


crlf = '\x0d\x0a'
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
        'bimonthly': 'bi-mesnsuelle'
        }
gran = {'fr:commune': 'à la commune',
        'country': 'au pays',
        'fr:departement': 'au département',
        'fr:epci': "à l'EPCI",
        'fr:region': 'à la région',
        'poi': "au point d'intérêt",
        'fr:canton': 'au canton',
        'fr:iris': "à l'IRIS INSEE",
        'fr:collectivite': 'à la collectivité'
        }
max_orga = '3'


def capitale(text):
    return text[0].upper() + text[1:]


def md2tex(md, markdown=True):
    if not md:
        return ''
    md = md.replace('&#x27;', "'").replace('&quot;', '"')
    md = md.replace('°', '\\degree{}').replace('€', '\\euro{}')
    md = md.replace('²', '\\textsuperscript{2}')
    md = re.sub('(^|\n)#+ ','',md)
    if markdown:
        # ajout liens manquants
        md = re.sub(r'(^|[^(])(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)($|[^)])',r'[\2](\2)',md)
        # suppression des images du code markdown
        md = re.sub(re.compile('!(\[|\().*?\)', re.MULTILINE), r'', md.replace('\n]', ']'))
        md = pypandoc.convert_text(md, 'tex', format='md')
        md = md.replace('\\tightlist', '')
    else:
        md = md.replace('&', '\\&{}').replace('#', '\\#{}').replace('_', '\\_').replace('%', '\\%')
    return md


def getlogo(data, path):
    logo = None
    if data['logo'] != '':
        logo = data['logo'].replace('https://static.data.gouv.fr/avatars/', '')
        logo = logo.replace('/', '_')
        logo = 'images/orga/' + logo
        if not os.path.isfile(logo):
            r = requests.get(data['logo'])
            print('GET', data['logo'], logo)
            if r.status_code == 200:
                if logo:
                    with open(logo, 'wb') as fd:
                        for chunk in r.iter_content(chunk_size=1024):
                            fd.write(chunk)
                    if r.headers['content-type'] == 'image/gif':
                        gif = Image.open(logo)
                        logo = logo.replace('.gif', '.png')
                        gif.save(logo)
            else:
                logo = None
        else:
            logo = logo.replace('.gif', '.png')
    return logo


def data2tex(datagouv, orga=True):
    org = ''
    for data in datagouv:
        # nouveau producteur
        if orga and org != data['name']:
            moredata(org)
            out.write("""
\\clearpage
\\section{%(name)s}
""" % {'name': md2tex(data['name'], markdown=False)} )
            # changement d'organisation
            org = data['name']
            print(org)
            logo = getlogo(data, 'images/orga/')

            # ajout du logo
            if logo:
                out.write(crlf+"""
\\begin{center}
  \\includegraphics[width=%(width)s]{%(logo)s}
\\end{center}
""" % {'width': '3cm',
       'logo': logo,
       'qr': 'https://data.gouv.fr/organization/'+data['organization_id']}
                         )

            # texte de description du producteur
            if data['description_org'] != '':
                out.write(crlf+"""
%(description)s

\\vspace{0.5cm}

""" % {'description': md2tex(data['description_org'])})


        # jeu de données
        # génération du QRcode
        out.write("\\needspace{12\\baselineskip}"+crlf)
        if orga:
            #  out.write('\\addcontentsline{toc}{subsection}{%s}' % (capitale(md2tex(data['title'])), ) + crlf)
            out.write('\\subsection*{%s}' % (capitale(md2tex(data['title'])), ))
        else:
            out.write('\\clearpage\\section{%s}' % (capitale(md2tex(data['title'])), ))

        # pour datasets SPD on affiche le logo du producteur
        if not orga:
            logo = getlogo(data, 'images/orga/')
            # ajout du logo
            if logo:
                out.write(crlf+"""
\\begin{center}
  \\includegraphics[width=%(width)s]{%(logo)s}
\\end{center}
""" % {'width': '3cm',
       'logo': logo,
       'qr': 'https://data.gouv.fr/organization/'+data['organization_id']}
                         )

        if data['tags']:
            for mot in data['tags'].split(','):
                out.write('\\index{%s}' % (mot.replace('-','!'),))
        out.write("""
  \\begin{wrapfigure}{r}{%(width)s}
    \\centering
    \\qrcode[nolink]{%(url)s}
  \\end{wrapfigure}
""" % {'width': qrcode_width, 'url': "https://data.gouv.fr/dataset/"+data['id']} + crlf)
        out.write('Licence : \\textbf{%s}\\newline' % (md2tex(data['license'].replace(' / Open Licence','') if data['license'] != '' else 'non renseignée'),)+crlf)
        out.write('Créé le : %s\\newline' % (str(data['created_at'])[:10], )+crlf)
        out.write('Modifié le : %s\\newline' % (str(data['last_modified'])[:10], )+crlf)

        if data['temporal_coverage.start'] and data['temporal_coverage.end']:
            out.write('De %s à %s\\newline' % (str(data['temporal_coverage.start'])[:10], str(data['temporal_coverage.end'])[:10])+crlf)
        if data['spatial.granularity'] in gran:
            out.write('Granularité : %s\\newline' % (gran[data['spatial.granularity']], )+crlf)
        if data['frequency'] in freq:
            out.write('Mise à jour : %s\\newline' % (freq[data['frequency']], )+crlf)
        out.write('Popularité : %s %s\\newline' 
                  % (str(data['metric.reuses']) + ' réutilisations, ' if data['metric.reuses']>1 else str(data['metric.reuses']) + ' réutilisation, ',
                     str(data['metric.followers']) + ' suivis' if data['metric.followers']>1 else str(data['metric.followers']) + ' suivi'
                     ) + crlf)
        out.write('Mots-clé : \\emph{%s}\\newline' % (md2tex(data['tags'] if data['tags'] and data['tags'] != '' else 'aucun').replace(',',', ',))+crlf)
        out.write('Permalien : \\url{%s}\\newline' % (site_url+'dataset/'+data['id'], )+crlf)
        out.write("""
\\par
\\noindent
    """)
        out.write(md2tex(data['description'])+crlf)
        out.write("""
\\vspace{0.5cm}
""")
    moredata(org)

def moredata(org):
    if org != '':
        db.execute('SELECT * FROM datagouv_data WHERE "metric.reuses"=0 AND name=%s ORDER BY title', (org,))
        more = db.fetchall()

        if len(more) > 0:
            out.write('\\needspace{3\\baselineskip} \\rule{4cm}{0.25pt}\\newline\\textbf{Aussi disponible du même producteur :}\\begin{itemize}'+crlf)
            n = 0
            for data in more:
                out.write("\\item \\href{%s}{%s}" % (site_url+'dataset/'+data['id'], md2tex(data['title'], markdown=False))+crlf)
                n = n + 1
                if n >= 50:
                    out.write("\\item et %d autres jeux de données" % (len(more) - n,))
                    break
            out.write('\\end{itemize}'+crlf)


# source des données: base postgresql
pg = psycopg2.connect("dbname=datagouv")
db = pg.cursor(cursor_factory=psycopg2.extras.DictCursor)
# sortie: fichier .tex
out = open('datagouv.tex','w')

# sélection des jeux de données du SPD
db.execute("""
select * from datagouv_data where id in (
  '5530fbacc751df5ff937dddb',
  '5862206588ee38254d3f4e5e',
  '58c984b088ee386cdb1261f3',
  '58e5924b88ee3802ca255566',
  '58d8d8a0c751df17537c66be',
  '57343feb88ee3823b0d1b934',
  '58e5842688ee386c65805755',
  '58e53811c751df03df38f42d',
  '58da857388ee384902e505f5') order by title;
""")
datagouv = db.fetchall()
data2tex(datagouv, orga=False)

if True:
    # jeux de données services publics certifiés
    out.write("""
    \\clearpage

    \\chapter{Données des services publics certifiés}

    Ce chapitre liste une sélection des jeux de données produits par les services publics
    répertoriés sur le portail national \\href{https://data.gouv.fr/}{data.gouv.fr}
    ayant fait l'objet d'au moins une réutilisation publiés sous Licence Ouverte ou ODbL.

    \\minitoc

    \\clearpage

    """+crlf)

    # jeu de données avec réutilisation, sous LO ou ODbL
    db.execute("""
    select *
    from datagouv_data 
    where badges ~ 'certified'
        and "metric.reuses">0
        and license ~ '(Licence Ouverte|ODbL)'
    order by name,title
    """)
    datagouv = db.fetchall()
    print(len(datagouv))
    data2tex(datagouv)

    # autres jeux de données
    out.write("""

    \\clearpage

    \\chapter{Autres jeux de données}

    Ce chapitre liste une sélection des autres jeux de données disponibles
    sur \\emph{data.gouv.fr}.
    \\par
    Sont sélectionnés les jeux de données avec au moins une réutilisation et publiés sous une licence libre.

    \\minitoc

    """)

    # jeu de données avec réutilisation sous LO ou ODbL, CC, public
    db.execute("""
    select *
    from datagouv_data 
    where badges !~ 'certified'
        and "metric.reuses">0
        and license ~ '(Ouverte|Commons|Public)'
    order by name,title
    """)

    datagouv = db.fetchall()

    print(len(datagouv))
    data2tex(datagouv)
