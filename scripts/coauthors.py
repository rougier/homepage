import bibtexparser
from bibtexparser.customization import author

def format_name(name_str):
    """Converts 'First Last' or 'Last, First' to 'F. Last'"""
    # Remove LaTeX braces
    name_str = name_str.replace('{', '').replace('}', '').strip()
    
    if ',' in name_str:
        # Format: Last, First
        parts = name_str.split(',')
        last = parts[0].strip()
        first = parts[1].strip()
    else:
        # Format: First Last
        parts = name_str.rsplit(' ', 1)
        if len(parts) > 1:
            first = parts[0].strip()
            last = parts[1].strip()
        else:
            return name_str # Just a single name

    # Get initial (handle middle names by taking the first character of the string)
    initial = f"{first[0]}." if first else ""
    return f"{initial} {last}"

def extract_coauthors(bib_file, my_name="Rougier"):
    with open(bib_file, encoding='utf-8') as f:
        parser = bibtexparser.bparser.BibTexParser(common_strings=True)
        parser.customization = author
        bib_database = bibtexparser.load(f, parser=parser)

    unique_authors = set()

    for entry in bib_database.entries:
        if 'author' in entry:
            for name in entry['author']:
                if my_name.lower() not in name.lower():
                    # Format as 'F. Last' before adding to set
                    formatted = format_name(name)
                    unique_authors.add(formatted)

    sorted_authors = sorted(list(unique_authors), key=lambda x: x.split()[-1])
    
    print(f"## Co-authors (n={len(sorted_authors)})")
    print(", ".join(sorted_authors))


if __name__ == "__main__":
    extract_coauthors("../_data/rougier.bib")
