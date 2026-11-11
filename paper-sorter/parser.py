"""
This is a general parser that will take ADS bibtex listings for
papers and output a list of Paper objects that contain the
bibliographic information in convenient form.  This can then be used
to write a webpage listing of papers.

It optionally supports a list of ADS URLs, and will fetch the bibtex
for each paper.
"""

from __future__ import print_function

import re
import urllib.request

import bibtexparser
from bibtexparser.middlewares import (
    BlockMiddleware, MergeNameParts, MonthAbbreviationMiddleware,
    SeparateCoAuthors, SplitNameParts,
)
from bibtexparser.model import DuplicateBlockKeyBlock, Entry
from pylatexenc.latex2text import LatexNodes2Text

_months = ["", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]

replace_str = {
    r"$^{4}$": r"<sup>4</sup>"
}

mdash1 = "-{2,3}"

class Paper(object):
    """a single paper (or bibtex item)"""

    def __init__(self, entry_type, authors, title, year, journal_in,
                 month=None, booktitle=None, editors=None,
                 volume=None, number=None, pages=None, link=None, note=None,
                 subject=None, address=None, organization=None):

        self.entry_type = entry_type
        self.authors = list(authors)
        self.title = title
        self.year = int(year)
        self.journal = journal_in
        self.month = month
        self.booktitle = booktitle
        self.editors = editors
        self.volume = volume
        self.number = number
        self.pages = pages
        self.link = link
        self.note = note
        self.subject = subject
        self.organization = organization
        self.address = address

        if self.month is None:
            self.month = ""

    def __lt__(self, other):
        if not self.year == other.year:
            return self.year < other.year

        if not (self.month is None or other.month is None):
            smonth = _months.index(self.month.lower())
            omonth = _months.index(other.month.lower())

            return smonth < omonth

        return self.year < other.year

    def jstring(self, et_al_len=20):
        """return the string used to cite the paper"""
        t_str = self.title
        for k, v in replace_str.items():
            t_str = t_str.replace(k, v)
        t_str = re.sub(mdash1, "&mdash;", t_str)

        if len(self.authors) < et_al_len and not self.authors[min(1, len(self.authors)-1)].startswith("others"): 
            out_str = name_string(self.authors) + " "
        else:
            out_str = self.authors[0] + " et al. "

        if self.entry_type == "presentation":
            out_str += "{} {}, ".format(self.month, self.year)
        else:
            out_str += "{}, ".format(self.year)

        if not self.journal is None:
            out_str += "{}, ".format(self.journal)

        if not self.booktitle is None:
            out_str += "in {}, ".format(self.booktitle)

        if not self.editors is None:
            out_str += "ed. {}, ".format(name_string(self.editors))

        if not self.volume is None:
            out_str += "{}, ".format(self.volume)

        if not self.number is None:
            out_str += "{}, ".format(self.number)

        if not self.pages is None:
            out_str += "p. {}, ".format(self.pages)

        if not self.note is None:
            out_str += "{}, ".format(self.note)

        if self.entry_type == "presentation":
            out_str += "{}, {}".format(self.organization, self.address)

        out_str = out_str.strip()

        if len(out_str) > 0:
            if out_str[len(out_str)-1] == ",":
                out_str = out_str[:len(out_str)-1]

        if not self.link is None:
            l_str = "{}".format(self.link)
        else:
            l_str = ""

        return t_str, out_str, l_str

    def __str__(self):
        return self.title


def name_string(names):
    """string together the authors into a single string"""
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

def get_item(in_dict, name):
    """query for an item, and if it doesn't exist, return None"""
    if name in in_dict.keys():
        return in_dict[name]

    return None

def translate_journal(j):
    """replace some common journal latx commands"""
    if j is None:
        return None

    jn = j.strip()
    if jn.lower() == r"\apj":
        return "ApJ"
    elif jn.lower() == r"\apjs":
        return "ApJS"
    elif jn.lower() == r"\mnras":
        return "MNRAS"

    return jn

def fix_pages(p):
    """update the hyphenation between page ranges"""
    if p is None:
        return None

    return re.sub(r"[-–—]+", "&ndash;", p)

def clean_names(a):
    """remove braces and tildes from names"""
    if a is None:
        return None

    a_new = []
    for name in a:
        _nm = name.replace("{", "").replace("}", "").replace("~", " ")

        # special case
        if _nm == "Team, AMReX-Astro Microphysics":
            _nm = "AMReX-Astro Microphysics Team"

        a_new.append(_nm)

    return a_new

class PublicationTextMiddleware(BlockMiddleware):
    """Decode display text while preserving URLs and journal macros."""

    def __init__(self):
        super().__init__()
        self.decoder = LatexNodes2Text(math_mode="verbatim")

    def transform_entry(self, entry, library):
        for field in entry.fields:
            if field.key not in {
                "title", "author", "editor", "journal", "booktitle",
                "note", "subject", "address", "organization",
            }:
                continue
            value = field.value
            if field.key == "journal":
                value = translate_journal(value)
            if isinstance(value, list):
                field.value = [self.decoder.latex_to_text(name) for name in value]
            else:
                field.value = self.decoder.latex_to_text(value)
        return entry


def parsing_middleware():
    """Build a fresh v2 middleware stack for publication formatting."""
    return [
        MonthAbbreviationMiddleware(),
        SeparateCoAuthors(),
        SplitNameParts(),
        MergeNameParts(style="last"),
        PublicationTextMiddleware(),
    ]


def extract_paper_info(e):
    """Take a v2 Entry and make a Paper object from it."""

    entry_type = e.entry_type.lower()
    e = {field.key: field.value for field in e.fields}

    if not "title" in e.keys():
        print("no title: ", e)
        return None
    else:
        title = e["title"]

    if not "author" in e.keys():
        print("no author: ", e)
        return None
    else:
        authors = e["author"]

    authors = clean_names(authors)

    volume = get_item(e, "volume")
    number = get_item(e, "number")
    journal_name = translate_journal(get_item(e, "journal"))
    year = get_item(e, "year")
    month = get_item(e, "month")
    editors = clean_names(get_item(e, "editor"))
    booktitle = get_item(e, "booktitle")
    pages = fix_pages(get_item(e, "pages"))
    note = get_item(e, "note")
    subject = get_item(e, "subject")
    address = get_item(e, "address")
    organization = get_item(e, "organization")

    if "adsurl" in e.keys():
        link_url = get_item(e, "adsurl")
    elif "url" in e.keys():
        link_url = get_item(e, "url")
    else:
        l = get_item(e, "link")
        if not l is None:
            link_url = l.strip().splitlines()[0].split()[0]
        else:
            link_url = None

    return Paper(entry_type, authors, title, year, journal_name,
                 month=month, editors=editors,
                 booktitle=booktitle,
                 volume=volume, number=number, pages=pages,
                 link=link_url, note=note, subject=subject,
                 address=address, organization=organization)


def library_papers(library):
    """Extract papers, retaining entries with duplicate citation keys as in v1."""
    papers = []
    for block in library.blocks:
        if isinstance(block, DuplicateBlockKeyBlock):
            # v2 excludes duplicate keys from library.entries. Parse each such
            # entry independently so existing bibliographies retain all papers.
            duplicate = bibtexparser.parse_string(
                block.raw, append_middleware=parsing_middleware())
            papers.extend(library_papers(duplicate))
        elif isinstance(block, Entry):
            paper = extract_paper_info(block)
            if paper is not None:
                papers.append(paper)
        elif block in library.failed_blocks:
            raise ValueError(f"Could not parse BibTeX at line {block.start_line}: {block.error}")
    return papers


def parse_urlfile(url_file):
    """
    take a file of the form

    category: ads url

    and get the bibtex from the URL and return a list of Paper objects
    with the category stored as the subject

    """

    papers = []

    with open(url_file) as f:

        for line in f:
            if line.startswith("#") or line.strip() == "": continue

            subject, url = line.split(": ")

            # for the ADS bibtex URL, lop off the paper_id
            paper_id = url.strip().split("/")[-1]
            bibtex_url = "http://adsabs.harvard.edu/cgi-bin/nph-bib_query?bibcode={}&data_type=BIBTEX".format(paper_id)

            # get the bibtex in html -- this is a little tricky, since
            # urlopen gives us a byte object that we need to decode
            # into unicode before we can play with it.
            print(bibtex_url)
            with urllib.request.urlopen(bibtex_url) as response:
                bibtex_html = response.read()

            raw_bibtex_html = bibtex_html.splitlines()

            bibtex_string = ""
            for bibline in raw_bibtex_html:
                bibtex_string += "{}\n".format(bibline.decode("utf8"))

            # strip off any header and just leave the bibtex
            found_start = False
            bibtex = ""
            for bibline in bibtex_string:
                if bibline.startswith("@"):
                    found_start = True
                if found_start:
                    bibtex += bibline

            # parse the bibtex string
            library = bibtexparser.parse_string(
                bibtex, append_middleware=parsing_middleware())

            for p in library_papers(library):
                p.subject = subject
                papers.append(p)

    papers.sort(reverse=True)
    return papers


def parse_bibfile(bibfile):
    """given a bibtex .bib file, parse it and return the papers found"""

    library = bibtexparser.parse_file(
        bibfile, append_middleware=parsing_middleware())
    papers = library_papers(library)

    papers.sort(reverse=True)

    return papers
