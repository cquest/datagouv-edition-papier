#!/usr/bin/env python3


import csv
import sys

import qrcode
import qrcode.image.svg

out = open('out.asciidoc','w')
crlf = '\x0d\x0a'
out.write("""= data.gouv.fr
data.gouv.fr <info@data.gouv.fr>
v20190401, 2019-04-01
:homepage: https://www.data.gouv.fr
:toc:
:imagesdir: images
:lang: fr
:sectnumlevels: 2

Edition papier du portail unique interministériel destiné à rassembler et à mettre à disposition librement l'ensemble des informations publiques de l'Etat, de ses établissements publics administratifs et, si elles le souhaitent, des collectivités territoriales et des personnes de droit public ou de droit privé chargées d'une mission de service public.
(décret 2011-194 du 21 février 2011)

<<<

== Jeux de données

Cette section liste les jeux de données par producteur.



"""+crlf)
csv.field_size_limit(1000000)
datagouv = csv.DictReader(open(sys.argv[1], 'r'), delimiter=';')
n=0
crlf='\x0d\x0a'
for data in datagouv:
    # génération du QRcode
    # img = qrcode.make(data['url'],
    #                   image_factory=qrcode.image.svg.SvgImage)
    # print(img)
    print(data['id'])
    out.write("<<<"+crlf+crlf)
    out.write(':sectnums!:'+crlf+'=== '+data['title']+crlf+crlf)
    out.write("'''"+crlf)
    out.write(data['url']+crlf+crlf)
    out.write(data['description']+crlf+crlf)
    out.write('Licence : *%s*' % (data['license'],)+crlf+crlf)
    out.write('Mots-clé : *%s*' % (data['tags'].replace(',',', ',))+crlf+crlf)
    n=n+1
    if n > 1:
        exit()
