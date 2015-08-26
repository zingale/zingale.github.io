import bibtexparser
from bibtexparser.bparser import BibTexParser
from bibtexparser.customization import *

accent_replace = {
    '\"u', "ue"
}


class Paper(object):
    def __init__(self, authors, title, year, journal, 
                 month=None, booktitle=None, editors=None, 
                 volume=None, pages=None, link=None):

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

    def __cmp__(self, other):
        if not self.year == other.year:
            return cmp(self.year, other.year)
        else:
            if not (self.month == None or other.month == None):
                return cmp(self.month, other.month)
            else:
                return cmp(self.year, other.year)

    def jprint(self):
        print self.title

        
        print name_string(self.authors)

        other_str = ""

        other_str += "{}, ".format(self.year)

        if not self.journal == None:
            other_str += "{}, ".format(self.journal)

        if not self.booktitle == None:
            other_str += "in {}, ".format(self.booktitle)

        if not self.editors == None:
            other_str += "ed. {}, ".format(name_string(self.editors))
            
        if not self.volume == None:
            other_str += "{}, ".format(self.volume)

        if not self.pages == None:
            other_str += "p. {}, ".format(self.pages)

        if not self.link == None:
            other_str += "{}".format(self.link)

        other_str = other_str.strip()

        if len(other_str) > 0:
            if other_str[len(other_str)-1] == ",":
                other_str = other_str[:len(other_str)-1]

        print other_str

        

def name_string(names):
    nm_str = ""
    for n, a in enumerate(names):
        if n < len(names)-1:
            astr = "{}, "
        else:
            astr = " &amp; {}"
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

def customizations(record):
    """Use some functions delivered by the library

    :param record: a record
    :returns: -- customized record

    """
    record = type(record)    # lowercase
    record = author(record)
    record = editor(record)
    record = journal(record)
    record = keyword(record)
    record = link(record)
    record = page_double_hyphen(record)
    record = doi(record)
    return record

with open('papers.bib') as bibtex_file:
    parser = BibTexParser()
    parser.customization = customizations
    bib_database = bibtexparser.load(bibtex_file, parser=parser)

    papers = []

    for e in bib_database.entries:
        if not "title" in e.keys():
            print "no title: ", e
            continue
        else:
            title = e["title"]

        if not "author" in e.keys():
            print "no author: ", e
            continue
        else:
            authors = e["author"]

        authors = clean_names(authors)

        volume = get_item(e, "volume")        
        journal = translate_journal(get_item(e, "journal"))
        year = get_item(e, "year")
        month = get_item(e, "month")
        editors = clean_names(get_item(e, "editors"))
        booktitle = get_item(e, "booktitle")
        pages = fix_pages(get_item(e, "pages"))

        
        if "adsurl" in e.keys():
            link = get_item(e, "adsurl")
        else:
            l = get_item(e, "link")
            if not l == None:
                link = l[0]["url"]
            
        papers.append(Paper(authors, title, year, journal,
                            month=month, editors=editors, booktitle=booktitle,
                            volume=volume, pages=pages, 
                            link=link))


    papers.sort(reverse=True)

    current_year = 3000

    for p in papers:
        if p.year < current_year:
            print "\n{}\n".format(p.year)
            current_year = p.year

        p.jprint()
        print ""


