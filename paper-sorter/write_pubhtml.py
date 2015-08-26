import parser

papers = parser.parse_bibfile("papers.bib")

current_year = 3000

for p in papers:
    if p.year < current_year:
        print "\n{}\n".format(p.year)
        current_year = p.year

    t, o, l = p.jstring()
    print "{}\n{}\n{}\n".format(t, o, l)




