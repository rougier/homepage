import bibtexparser
from bibtexparser.bwriter import BibTexWriter
import re
from collections import defaultdict
from datetime import datetime

def transform_bib(input_file, output_file):
    with open(input_file) as bibtex_file:
        db = bibtexparser.load(bibtex_file)

    # Dictionary to group entries by their base key
    # Key: base_id, Value: list of entry objects
    groups = defaultdict(list)
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    
    priority_order = [
        'title', 'author', 'year', 'month',
        'journal', 'booktitle', 'series', 'volume', 'number', 'pages',
        'publisher', 'organization', 'address',
        'doi', 'url', 'pdf', 'hal_id', 
        'keywords', 'tags', 'annote', 'note'
    ]

    # --- PASS 1: GENERATE BASE KEYS & GROUP ---
    # Sort chronologically so that group[0] is the oldest, group[1] is next, etc.
    db.entries.sort(key=lambda x: x.get('year', '0000'))

    for entry in db.entries:
        # Heuristics
        kw_lower = (entry.get('keywords', '') + " " + entry.get('tags', '')).lower()
        note_lower = (entry.get('note', '') + " " + entry.get('annote', '')).lower()
        how_lower = entry.get('howpublished', '').lower()
        book_lower = entry.get('booktitle', '').lower()
        title_lower = entry.get('title', '').lower()
        
        is_media = any(x in book_lower or x in note_lower or x in how_lower for x in ['charlie hebdo', 'le parisien', 'usbek', 'reporterre', 'transmitter', 'radio'])
        is_outreach = any(x in kw_lower or x in note_lower or x in book_lower for x in ['popular', 'public', 'cap sciences', 'village des sciences'])
        b_type = "MEDIA" if is_media else ("OUTREACH" if is_outreach else "ACADEMIC")
        is_invited = 'invited' in kw_lower or 'invited' in entry['ID'].lower()
        
        # Category
        category = "ARTICLE" 
        if 'preprint' in kw_lower or 'biorxiv' in entry.get('journal', '').lower(): category = "PREPRINT"
        elif 'thesis' in kw_lower or entry['ENTRYTYPE'].lower() == 'phdthesis': category = "THESIS"
        elif 'chapter' in kw_lower or entry['ENTRYTYPE'].lower() == 'inbook': category = "CHAPTER"
        elif 'book' in kw_lower or entry['ENTRYTYPE'].lower() == 'book': category = "BOOK"
        elif 'poster' in kw_lower: category = "POSTER"
        elif any(x in kw_lower or x in title_lower for x in ['lecture', 'tutorial', 'matplotlib']): category = "TUTORIAL"
        elif 'interview' in note_lower or is_media: category = "INTERVIEW"
        elif 'discussion' in note_lower: category = "DISCUSSION"
        elif 'talk' in kw_lower or 'presentation' in kw_lower: category = "TALK"
        elif 'conf' in kw_lower or entry['ENTRYTYPE'].lower() == 'inproceedings': category = "CONFERENCE"

        # BibTeX EntryType Mapping
        type_map = {
            "ARTICLE": "article", "PREPRINT": "article", "THESIS": "phdthesis",
            "CHAPTER": "inbook", "BOOK": "book", "POSTER": "misc",
            "TUTORIAL": "misc", "INTERVIEW": "misc", "TALK": "unpublished",
            "DISCUSSION": "unpublished"
        }
        if category == "CONFERENCE":
            entry['ENTRYTYPE'] = 'unpublished' if is_invited else 'inproceedings'
        else:
            entry['ENTRYTYPE'] = type_map.get(category, 'article')

        # Construct Base Key (without letter)
        venue_raw = entry.get('journal', entry.get('booktitle', entry.get('howpublished', 'UNKNOWN')))
        venue_clean = re.sub(r'\W+', '', venue_raw.split()[0].replace('{', '').replace('}', '')).upper()
        year = entry.get('year', '0000')
        invited_seg = ":INVITED" if is_invited else ""
        
        base_key = f"ROUGIER:{year}:{b_type}{invited_seg}:{category}:{venue_clean}"
        groups[base_key].append(entry)

        # Keyword Update
        existing_kws = [k.strip() for k in entry.get('keywords', '').split(',') if k.strip()]
        new_tags = [b_type.lower(), category.lower()]
        if is_invited: new_tags.append('invited')
        entry['keywords'] = ", ".join(list(set(existing_kws + new_tags)))

    # --- PASS 2: ASSIGN FINAL IDS WITH HYPHEN SUFFIX ---
    for base_key, entries in groups.items():
        if len(entries) == 1:
            entries[0]['ID'] = base_key
        else:
            for i, entry in enumerate(entries):
                letter = alphabet[i] if i < len(alphabet) else f"z{i}"
                entry['ID'] = f"{base_key}-{letter}"

    # 3. FINAL SORT (Newest First)
    db.entries.sort(key=lambda x: x['ID'], reverse=True)

    # 4. WRITE PRESERVING HEADER AND ORDER
    writer = BibTexWriter()
    writer.indent = '  '
    
    with open(output_file, 'w') as f:
        header = f"% Nicolas Rougier bibliography\n% Last update: {datetime.now().strftime('%d %B %Y')}\n%\n"
        f.write(header)
        for entry in db.entries:
            current_fields = list(entry.keys())
            ordered_fields = [f for f in priority_order if f in current_fields]
            remaining_fields = sorted([f for f in current_fields if f not in priority_order and f not in ['ID', 'ENTRYTYPE']])
            writer.display_order = ordered_fields + remaining_fields
            
            tmp_db = bibtexparser.bibdatabase.BibDatabase()
            tmp_db.entries = [entry]
            f.write(writer.write(tmp_db))

if __name__ == "__main__":
    transform_bib('rougier.bib', 'rougier-cleaned.bib')
    
