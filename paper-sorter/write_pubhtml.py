from __future__ import print_function

import parser

papers = parser.parse_bibfile("papers.bib")


# sorted by date
tf = open("pub_template.html", "r")
dh = open("pub_year.html", "w")

current_year = 3000
first = True

ostr = ""

# by year
for p in papers:
    if p.year < current_year:
        if not first:
            ostr += "</dl>\n"
        else:
            first = False

        ostr += "<p><h2>{}</h2>\n".format(p.year)
        ostr += "<dl>\n"

        current_year = p.year

    t, o, l = p.jstring()
    if not l == "":
        ostr += "<dt>{} <a href='{}'>[link]</a></dt>\n".format(t, l)
    else:
        ostr += "<dt>{}</dt>\n".format(t)

    ostr += "<dd>{}</dd>\n".format(o)

ostr += "</dl>\n"

for line in tf:
    dh.write(line.replace("@@pub-list@@", ostr))

dh.close()
tf.close()

# by subject
tf = open("pub_template.html", "r")
dh = open("pub_subj.html", "w")

papers_by_subj = {}

for p in papers:
    subj = p.subject
    if not subj in papers_by_subj.keys():
        papers_by_subj[subj] = [p]
    else:
        papers_by_subj[subj].append(p)

# now loop over subject
ostr = ""
for s in sorted(papers_by_subj, key=str.lower):
    ps = papers_by_subj[s]
    ps.sort(reverse=True)

    ostr += "<p><h2>{}</h2>\n".format(s)
    ostr += "<dl>\n"

    for p in ps:

        t, o, l = p.jstring()
        if not l == "":
            ostr += "<dt>{} <a href='{}'>[link]</a></dt>\n".format(t, l)
        else:
            ostr += "<dt>{}</dt>\n".format(t)

        ostr += "<dd>{}</dd>\n".format(o)

    ostr += "</dl>\n"

for line in tf:
    dh.write(line.replace("@@pub-list@@", ostr))

dh.close()
tf.close()

