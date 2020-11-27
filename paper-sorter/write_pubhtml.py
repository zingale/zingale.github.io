#!/usr/bin/env python

import parser

papers = parser.parse_bibfile("papers.bib")

for p in papers:
    print(p)


# sorted by date
tf = open("pub_template.html", "r")
dh = open("../pub_year.html", "w")

current_year = 3000
first = True

ostr = ""

# by year
years = list(set([p.year for p in papers]))
years.sort(reverse=True)

for p in papers:
    if p.year < current_year:
        if not first:
            ostr += "</dl>\n"
        else:
            first = False

        ostr += "<p><h2><a name='{}'></a>{}</h2>\n\n".format(p.year, p.year)
        ostr += "<dl>\n"

        current_year = p.year

    t, o, l = p.jstring()
    if not l == "":
        ostr += "<dt><a href='{}'>{}</a></dt>\n".format(l, t)
    else:
        ostr += "<dt>{}</dt>\n".format(t)

    ostr += "<dd>{}</dd>\n\n".format(o)

ostr += "</dl>\n\n"

year_index = "<ul>\n"
for n, y in enumerate(years):
    if n % 3 == 0:
        year_index += "<li>"
    else:
        year_index += "&nbsp;&nbsp;&nbsp;"

    year_index += "<a href='#{}'>{}</a>".format(y, y)

    if n % 3 == 2:
        year_index += "</li>\n"

if not len(year_index) % 3 == 0: 
    year_index += "</li>\n"

year_index += "</ul>\n"

for line in tf:
    dh.write(line.replace("@@pub-list@@", ostr).replace("@@year-index@@", year_index).replace("@@sub-index@@", ""))

dh.close()
tf.close()

# by subject
tf = open("pub_template.html", "r")
dh = open("../pub_subj.html", "w")

subs = list(set([p.subject for p in papers]))
subs.sort(key=str.lower)

papers_by_subj = {}

for p in papers:
    subj = p.subject
    if not subj in papers_by_subj.keys():
        papers_by_subj[subj] = [p]
    else:
        papers_by_subj[subj].append(p)

sub_index = "<ul>\n"
for s in subs:
    sub_index += "<li><a href='#{}'>{}</a></li>\n".format(s.replace(" ", "_").replace(":", ""), s)
sub_index += "</ul>\n"


# now loop over subject
ostr = ""
for s in sorted(papers_by_subj, key=str.lower):
    ps = papers_by_subj[s]
    ps.sort(reverse=True)

    ostr += "<p><h2><a name='{}'></a>{}</h2>\n".format(s.replace(" ", "_").replace(":", ""), s)
    ostr += "<dl>\n"

    for p in ps:

        t, o, l = p.jstring()
        if not l == "":
            ostr += "<dt><a href='{}'>{}</a></dt>\n".format(l, t)
        else:
            ostr += "<dt>{}</dt>\n".format(t)

        ostr += "<dd>{}</dd>\n".format(o)

    ostr += "</dl>\n"

for line in tf:
    dh.write(line.replace("@@pub-list@@", ostr).replace("@@year-index@@", "").replace("@@sub-index@@", sub_index))

dh.close()
tf.close()

