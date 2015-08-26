from __future__ import print_function

import parser

papers = parser.parse_bibfile("papers.bib")

current_year = 3000
first = True

for p in papers:
    if p.year < current_year:
        if not first:
            print ("</dl>\n")
        else:
            first = False

        print ("<p><h2>{}</h2>\n".format(p.year))
        print ("<dl>\n")

        current_year = p.year

    t, o, l = p.jstring()
    print ("<dt>{} <a href='{}'>[link]</a></dt>\n".format(t, l))
    print ("<dd>{}</dd>\n".format(o))







