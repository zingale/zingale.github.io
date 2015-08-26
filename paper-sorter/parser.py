from __future__ import print_function

import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *

replace_str = {
    r"$^{4}$": r"<sup>4</sup>"
}


class Paper(object):
    def __init__(self, authors, title, year, journal,
                 month=None, booktitle=None, editors=None,
                 volume=None, pages=None, link=None, note=None, 
                 subject=None):

        self.authors = list(authors)
        self.title = title
        self.year = int(year)
        self.journal = journal
        self.month = month
        self.booktitle = booktitle
        self.editors = editors
        self.volume = volume
        self.pages = pages
        self.link = link
        self.note = note
        self.subject = subject

    def __lt__(self, other):
        if not self.year == other.year:
            return self.year < other.year
        else:
            if not (self.month == None or other.month == None):
                return self.month < other.month
            else:
                return self.year < other.year

    def jstring(self):
        t_str = self.title
        for k, v in replace_str.items():
            t_str = t_str.replace(k,v)

        out_str = name_string(self.authors)


        out_str += "{}, ".format(self.year)

        if not self.journal == None:
            out_str += "{}, ".format(self.journal)

        if not self.booktitle == None:
            out_str += "in {}, ".format(self.booktitle)

        if not self.editors == None:
            out_str += "ed. {}, ".format(name_string(self.editors))

        if not self.volume == None:
            out_str += "{}, ".format(self.volume)

        if not self.pages == None:
            out_str += "p. {}, ".format(self.pages)

        if not self.note == None:
            out_str += "{}, ".format(self.note)

        out_str = out_str.strip()

        if len(out_str) > 0:
            if out_str[len(out_str)-1] == ",":
                out_str = out_str[:len(out_str)-1]

        if not self.link == None:
            l_str = "{}".format(self.link)
        else:
            l_str = ""

        return t_str, out_str, l_str


def name_string(names):
    nm_str = ""
    if len(names) == 1:
        nm_str = "{}".format(names[0])
    else:
        for n, a in enumerate(names):
            if n < len(names)-1:
                astr = "{}, "
            else:
                astr = "&amp; {}"
            nm_str += astr.format(a)
    return nm_str

def get_item(dict, name):
    if name in dict.keys():
        return dict[name]
    else:
        return None

def translate_journal(j):
    if j == None:
        return None
    else:
        jn = j["name"].strip()
        if jn.lower() == r"\apj":
            return "ApJ"
        elif jn.lower() == r"\apjs":
            return "ApJS"
        else:
            return jn

def fix_pages(p):
    if p == None:
        return None
    else:
        return p.replace("--","&ndash;")

def clean_names(a):
    if a == None:
        return None
    else:
        a_new = []
        for name in a:
            a_new.append(name.replace("{","").replace("}","").replace("~"," "))
        return a_new

def clean_ednames(a):
    if a == None:
        return None
    else:
        a_new = []
        for ed_dict in a:
            a_new.append(ed_dict["name"].replace("{","").replace("}","").replace("~"," "))
        return a_new

def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record

    """
    record = convert_to_unicode(record)
    record = type(record)    # lowercase
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page_double_hyphen(record)
    record = doi(record)
    return record

def parse_bibfile(bibfile):

    with open(bibfile) as bibtex_file:
        parser = BibTexParser()
        parser.customization = customizations
        bib_database = bibtexparser.load(bibtex_file, parser=parser)

        papers = []

        for e in bib_database.entries:
            if not "title" in e.keys():
                print( "no title: ", e)
                continue
            else:
                title = e["title"]

            if not "author" in e.keys():
                print( "no author: ", e)
                continue
            else:
                authors = e["author"]

            authors = clean_names(authors)

            volume = get_item(e, "volume")
            journal = translate_journal(get_item(e, "journal"))
            year = get_item(e, "year")
            month = get_item(e, "month")
            editors = clean_ednames(get_item(e, "editor"))
            booktitle = get_item(e, "booktitle")
            pages = fix_pages(get_item(e, "pages"))
            note = get_item(e, "note")
            subject = get_item(e, "subject")

            if "adsurl" in e.keys():
                link = get_item(e, "adsurl")
            else:
                l = get_item(e, "link")
                if not l == None:
                    link = l[0]["url"]
                else:
                    link = None

            papers.append(Paper(authors, title, year, journal,
                                month=month, editors=editors,
                                booktitle=booktitle,
                                volume=volume, pages=pages,
                                link=link, note=note, subject=subject))


    papers.sort(reverse=True)

    return papers
