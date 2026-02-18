import re
import os
import sys
import bibtexparser
from bibtexparser.bwriter import BibTexWriter
from bibtexparser.bibdatabase import BibDatabase

def get_sort_key(entry):
    # Extract year, default to 0 if missing
    # We use regex to extract digits in case year is "{2024}" or "2024ish"
    year_val = entry.get('year', '0')
    year_match = re.search(r'\d{4}', str(year_val))
    year = int(year_match.group()) if year_match else 0
    return year

def split_bib(input_file, output_dir):
    base_prefix = os.path.splitext(os.path.basename(input_file))[0]
    
    # Ensure the directory exists
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(input_file, encoding='utf-8') as bibtex_file:
        db = bibtexparser.load(bibtex_file)

    def get_keywords(entry):
        keywords = entry.get('keywords', entry.get('keyword', '')).lower()
        return [x.strip() for x in keywords.split(',')]

    configs = [
        ('media-podcasts',        lambda k, t: 'podcast' in k),
        ('media-coverage',        lambda k, t: 'coverage' in k),
        ('media-interviews',      lambda k, t: 'interview' in k),
        ('academic-correspondences', lambda k, t: t == 'article' and 'correspondence' in k),
        ('outreach-shows',        lambda k, t: 'show' in k),
        ('outreach-articles',     lambda k, t: t in ['article', 'book', 'inbook'] and 'outreach' in k),
        ('outreach-conferences',  lambda k, t: t == 'unpublished' and 'outreach' in k),
        ('academic-thesis',       lambda k, t: t == 'phdthesis'),
        ('academic-posters',      lambda k, t: 'poster' in k),
        ('academic-tutorials',    lambda k, t: t == 'unpublished' and 'tutorial' in k),
        ('academic-articles',     lambda k, t: t == 'article' and 'article' in k),
        ('academic-chapters',     lambda k, t: t == 'inbook' and 'academic' in k),
        ('academic-preprints',    lambda k, t: t == 'article' and 'preprint' in k),
        ('academic-conferences',  lambda k, t: t == 'inproceedings' and 'academic' in k),
        ('academic-books',        lambda k, t: t == 'book'),
        ('academic-lectures',     lambda k, t: t == 'unpublished' and 'lecture' in k and 'international' in k),
        ('academic-invited-int',  lambda k, t: t == 'unpublished' and 'academic' in k and 'international' in k),
        ('academic-invited-nat',  lambda k, t: t == 'unpublished' and 'academic' in k and 'national' in k),
    ]

    results = {name: [] for name, _ in configs}
    results['misc'] = []

    for entry in db.entries:
        kw = get_keywords(entry)
        etype = entry.get('ENTRYTYPE').lower()
        matched = False
        for name, logic in configs:
            if logic(kw, etype):
                results[name].append(entry)
                matched = True
                break
        if not matched:
            results['misc'].append(entry)

    writer = BibTexWriter()
    writer.indent = '  '
    writer.order_entries_by = None
    
    for name, entries in results.items():
        if entries:
            entries.sort(key=get_sort_key, reverse=True)
            out_db = BibDatabase()
            out_db.entries = entries
            output_filename = os.path.join(output_dir, f"{base_prefix}-{name}.bib")
            with open(output_filename, 'w', encoding='utf-8') as f:
                f.write(writer.write(out_db))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 split-bibliography.py <input.bib> <output_dir>")
    else:
        split_bib(sys.argv[1], sys.argv[2])
