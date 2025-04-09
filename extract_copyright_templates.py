"""
Extract PD-like templates from Wikimedia Commons files in 'Media from Delpher' category
=======================================================================================

Overview:
---------
This script identifies and extracts potentially Public Domain (PD) or PD-like licensing templates
from files hosted on Wikimedia Commons, specifically those categorized under:

    - Category:Media from Delpher
    - But excluding: Category:Scans from the Internet Archive

The goal is to help detect files with licensing metadata that suggest they are in the public domain,
but which are not explicitly tagged using standard Internet Archive or PD templates.

How it works:
-------------
1. **File Discovery**
   Uses the MediaWiki API to query Commons for files in the target category (`Media from Delpher`)
   while excluding those in a known-safe PD category (`Scans from the Internet Archive`).

2. **Wikitext Retrieval**
   For each matching file, the script fetches the raw wikitext (template code, metadata, and fields).

3. **Template Extraction**
   The script identifies templates from two sources:
   - Top-level templates (directly used on the file page)
   - Templates embedded within the `|permission=` or `|date=` fields of wrapper templates like:
     `{{Information}}`, `{{Book}}`, `{{Photograph}}`, or `{{Artwork}}`

   Templates are filtered using several exclusion rules:
   - Known irrelevant or decorative templates (see `EXCLUDED_TEMPLATES`)
   - Templates with namespaced prefixes (e.g., `User:`, `Creator:`)
   - Language-tagging templates like `{{en}}`, `{{nl}}`, etc.
   - Utility templates like `{{DEFAULTSORT}}` or `{{ucfirst}}`

4. **Date Extraction**
   Attempts to derive a simplified creation or publication date from template metadata:
   - Recognizes formats like `{{circa|1930}}`, `{{other date|between|1920|1935}}`, or `1935-06-01`
   - If no date is available, leaves field blank or as `"Unknown"`

5. **Output**
   - Console output: File URL, parsed date, detected template names with links
   - Excel file: A table with rows per file and columns for:
     - File URL
     - Parsed date
     - Number of templates
     - Each template name and a link to its documentation page

Configuration & Customization:
------------------------------
- To change which files are analyzed, modify:
    `include_term = "Media from Delpher"`
    `exclude_term = "Scans from the Internet Archive"`

- Output is saved as:
    `Media_from_Delpher_commons_templates_output_<DATE>.xlsx`

- You can limit the number of processed files for testing by modifying:
    `limit=20` in the `search_files_from_category_excluding_term()` function call.

Requirements:
-------------
- Python 3.7+
- `requests`
- `pandas`
- `openpyxl` (for Excel export)

Author:
-------
- Olaf Janssen, Wikimedia coordinator @KB national library of the Netherlands (via ChatGPT)
- Last updated: 9 April 2025
- User-Agent: OlafJanssenBot/1.0

License:
--------
This script is released into the public domain. You may freely use, adapt, and redistribute it.
"""


import requests
import re
import urllib.parse
import pandas as pd
import datetime
import openpyxl

# List of templates to exclude (case-insensitive, supports wildcards for regex filtering)
EXCLUDED_TEMPLATES = {
    '1937',
    '1937 03 17',
    'after',
    'anonymous',
    'author',
    'before',
    'between',
    'bijbelsche kunst',
    'bildindex',
    'boijmansonline',
    'booknavibar',
    'border is intentional',
    'chefs d\'oeuvre de la collection d.g. van beuningen',
    'cite news',
    'circa',
    'collective work',
    'complex date',
    'creator',
    'crop for wikidata',
    'date',
    'dead link',
    'de collectie verrijkt',
    'de jérôme bosch à rembrandt, peintures et dessins du musée boymans de rotterdam',
    'de minimis',
    'deminimis',
    'delpher',
    'djvu',
    'daumier register',
    'dutch art 1450–1900',
    'extracted',
    'extracted from',
    'fop-pakistan',
    'fourcaud (1)',
    'fraenger',
    'friedländer',
    'haverman, hendrik johannes',
    'het wonder, miracula christi',
    'hieronymus bosch, the complete paintings and drawings',
    'hieronymus bosch, visions of genius',
    'honderd jaar museum boymans, rotterdam, meesterwerken uit de verzameling d.g. van beuningen',
    'image extracted',
    'imagenote',
    'imagenoteend',
    'insignia',
    'jeroen bosch, noord-nederlandsche primitieven',
    'jérôme bosch (fierens-vevaert)',
    'jheronimus bosch (1967)',
    'jheronimus bosch (2001)',
    'jheronimus bosch alle schilderijen en tekeningen',
    'kersttentoonstelling (1927-1928)',
    'kik-irpa',
    'kunstschatten uit nederlandse verzamelingen',
    'la collection goudstikker (june 1927)',
    'langswitch',
    'les primitifs flamands',
    'location',
    'marijnissen',
    'object location',
    'onze afgevaardigden 1909',
    'onze afgevaardigden 1913',
    'onze musici',
    'onze musici (1923)',
    'original',
    'original caption',
    'original description',
    'original description page',
    'other date',
    'otherdate',
    'otherversion',
    'other version',
    'p-page',
    'pd-algorithm',
    'provenanceevent',
    'retouched',
    'retouchedpicture',
    'retouched picture',
    'rijksmonument',
    'rkdimages',
    'see more images',
    'size',
    'superseded',
    'taken on',
    'technique',
    'tentoonstelling hieronymus bosch (1930)',
    'tentoonstelling van oude kunst door de vereeniging van handelaren in oude kunst in nederland',
    'tolnay',
    'transferred from',
    'ucfirst',
    'uncategorized',
    'uploaded from mobile',
    'uploaded with derivativefx',
    'user',
    'van eyck to bruegel, 1400-1550',
    'verzameling f. koenigs',
    'vlaamsche kunst',
    'wga'
}

WRAPPER_TEMPLATES = ['Information', 'information','Photograph','photograph', 'Artwork', 'artwork', 'Art Photo','Art photo','Book','book']

LANGUAGE_TEMPLATE_PATTERN = re.compile(r'^[a-z]{2,3}$', re.IGNORECASE)
ONZE_PATTERN = re.compile(r'^onze afgevaardigden.*$', re.IGNORECASE)
DEFAULTSORT_PATTERN = re.compile(r'^defaultsort[: ]', re.IGNORECASE)
COLON_TEMPLATE_PATTERN = re.compile(r'^.*:.*$') #{{Creator:Hendrik Jan Bulthuis}}, {{User:Wdwdbot}}, {{ucfirst: {{Anonymous}} or {{Template:Something}}

def extract_year_from_date_string(date_str):
    """
    Parses a date string from Commons wikitext and extracts a simplified year or century.

    Handles:
    - {{circa|1939}}, {{taken on|1918-12-21}}, {{other date|between|...}}
    - Numeric formats like "19350601", "1935-06", etc.
    - Templates wrapped in {{ucfirst:...}} and similar

    Returns:
        str: A human-readable date (e.g., "1939", "20th century", "Unknown")
    """
    try:
        lower = date_str.lower()

        # Strip nested ucfirst template
        nested_match = re.search(r'\{\{[Uu][Cc]first:\s*(\{\{.*?\}\})\s*\}\}', date_str, re.IGNORECASE)
        if nested_match:
            date_str = nested_match.group(1)

        # Existing special templates
        if '{{complex date' in lower:
            century_match = re.search(r'\|\s*century\s*\|\s*(\d{1,2})', date_str, re.IGNORECASE)
            adj_match = re.search(r'\|\s*adj1\s*=\s*(\w+)', date_str, re.IGNORECASE)
            if century_match:
                century = int(century_match.group(1))
                adjective = adj_match.group(1).capitalize() + ' ' if adj_match else ''
                return f"{adjective}{century}th century"

        circa_match = re.search(r'\{\{[Cc]irca\|(\d{4})\}\}', date_str, re.IGNORECASE)
        if circa_match:
            return circa_match.group(1)

        century_match = re.search(r'\{\{\s*[Oo]ther date\s*\|\s*century\s*\|\s*(\d{1,2})', date_str, re.IGNORECASE)
        if century_match:
            return f"{century_match.group(1)}th century"

        if re.search(r'\{\{\s*[Oo]ther date\s*\|\s*\?\s*\}\}', date_str, re.IGNORECASE):
            return "Unknown"

        taken_on_match = re.search(r'\{\{\s*[Tt]aken on\s*\|\s*(\d{4})-\d{2}-\d{2}', date_str, re.IGNORECASE)
        if taken_on_match:
            return taken_on_match.group(1)

        between_match = re.search(r'\{\{\s*[Oo]ther date\s*\|\s*between\s*\|\s*(\d{4})\s*\|\s*(\d{4})\s*\}\}', date_str, re.IGNORECASE)
        if between_match:
            return between_match.group(2)

        # NEW: handle full or partial numeric formats
        compact_date = re.match(r'(\d{4})[-/]?\d{0,4}', date_str)
        if compact_date:
            return compact_date.group(1)

        # Fallback: any 4-digit year
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            return year_match.group(1)

        return date_str.strip()

    except Exception as e:
        print(f"Error extracting year from date: {e}")
        return date_str.strip()



def is_excluded_template(name):
    """
    Determines whether a template name should be excluded based on known irrelevant, generic,
    or colon-containing patterns (e.g., {{User:...}}, {{Creator:...}}, {{ucfirst:...}}).

    This function checks if the given template name:
    - Is in the predefined `EXCLUDED_TEMPLATES` set (case-insensitive)
    - Matches known patterns like {{DEFAULTSORT}}, {{onze afgevaardigden...}}, or language codes (e.g., "en", "nl")
    - Contains a colon (used for namespaced or nested templates)

    Args:
        name (str): The name of the template to check.

    Returns:
        bool: True if the template should be excluded, False otherwise.
    """
    try:
        name_lc = name.lower()
        return (
            name_lc in EXCLUDED_TEMPLATES
            or DEFAULTSORT_PATTERN.match(name_lc)
            or ONZE_PATTERN.match(name_lc)
            or LANGUAGE_TEMPLATE_PATTERN.match(name_lc)
            or COLON_TEMPLATE_PATTERN.match(name)
        )
    except Exception as e:
        print(f"Error checking if template is excluded ({name}): {e}")
        return False


def get_wikitext(title):
    """
    Retrieves the raw wikitext of a Wikimedia Commons page by its title.

    Uses the MediaWiki API (`action=parse`) to fetch the 'wikitext' property of the specified page.
    If the request fails or the expected response format is missing, returns an empty string.

    Args:
        title (str): The title of the Wikimedia Commons page (e.g., "File:Example.jpg").

    Returns:
        str: The raw wikitext of the page, or an empty string if an error occurs.
    """
    try:
        url = 'https://commons.wikimedia.org/w/api.php'
        params = {
            'action': 'parse',
            'page': title,
            'prop': 'wikitext',
            'format': 'json'
        }
        headers = {"User-Agent": "OlafJanssenBot/1.0 (https://commons.wikimedia.org/wiki/User:OlafJanssenBot; Python script)"}
        response = requests.get(url, params=params, headers=headers).json()
        return response['parse']['wikitext']['*']
    except Exception as e:
        print(f"Error fetching wikitext for {title}: {e}")
        return ''



def search_files_from_category_excluding_term(include_term, exclude_term, limit=500):
    """
    Searches Wikimedia Commons for files in one category while excluding files from another.

    Uses the MediaWiki search API to find files (namespace 6) that are in the `include_term` category
    but not in the `exclude_term` category. Fetches results in batches using pagination.

    Args:
        include_term (str): The name of the category to include (e.g., "Media from Delpher").
        exclude_term (str): The name of the category to exclude (e.g., "Scans from the Internet Archive").
        limit (int): The number of results to retrieve per API call (max 500).

    Returns:
        list[str]: A list of file titles (e.g., "File:Example.jpg"). Empty if the request fails.
    """
    print(f"🔍 Fetching files in category '{include_term}' excluding '{exclude_term}'...")
    try:
        SEARCH_URL = "https://commons.wikimedia.org/w/api.php"
        offset = 0
        all_titles = []

        while True:
            params = {
                "action": "query",
                "format": "json",
                "list": "search",
                "srsearch": f"incategory:\"{include_term}\" -incategory:\"{exclude_term}\"",
                "srlimit": limit,
                "srnamespace": 6,
                "sroffset": offset
            }
            headers = {"User-Agent": "OlafJanssenBot/1.0 (https://commons.wikimedia.org/wiki/User:OlafJanssenBot; Python script)"}
            response = requests.get(SEARCH_URL, params=params, headers=headers).json()
            results = response.get("query", {}).get("search", [])
            all_titles.extend(["File:" + r["title"].replace("File:", "") for r in results])

            if "continue" in response:
                offset = response["continue"]["sroffset"]
            else:
                break

        return all_titles
    except Exception as e:
        print(f"Error during search API call: {e}")
        return []


def extract_balanced_template(wikitext, template_name):
    """
    Extracts the full, balanced content of a template (e.g., {{Information}}), including nested templates and multiline fields.

    Args:
        wikitext (str): The full wikitext of a Commons file.
        template_name (str): The name of the wrapper template to extract.

    Returns:
        str: The full matched template block, or empty string if not found.
    """
    start = wikitext.lower().find(f'{{{{{template_name.lower()}')
    if start == -1:
        return ''

    depth = 0
    i = start
    while i < len(wikitext) - 1:
        if wikitext[i:i + 2] == '{{':
            depth += 1
            i += 2
        elif wikitext[i:i + 2] == '}}':
            depth -= 1
            i += 2
            if depth == 0:
                return wikitext[start:i]
        else:
            i += 1
    return ''


def extract_templates_and_date(wikitext):
    """
    Extracts all relevant templates and a simplified creation date from the given wikitext.

    Supports:
    - Wrapper templates like {{Information}}, {{Book}}, etc.
    - Date fields like |date= and |publication date=
    - Embedded permission-related templates

    Returns:
        tuple:
            list[str]: A sorted list of relevant template names (e.g., ["{{PD-old}}", "{{Anonymous-EU}}"])
            str: Parsed creation date (e.g., "1930", "Early 20th century", "Unknown")
    """
    try:
        all_templates = set()
        creation_date = ''

        for wrapper in WRAPPER_TEMPLATES:
            wrapper_block = extract_balanced_template(wikitext, wrapper)
            if wrapper_block:

                # Extract |date= field (case-insensitive, allow spaces around =)
                date_match = re.search(r'\|\s*[Dd]ate\s*=\s*(.+)', wrapper_block, re.IGNORECASE)
                if date_match:
                    raw_date = date_match.group(1).strip()
                    date_for_parsing = raw_date.split('{{')[0].strip()
                    creation_date = extract_year_from_date_string(date_for_parsing)

                    # Also capture embedded templates in date
                    embedded_templates = re.findall(r'\{\{([^\|\}\n]+)', raw_date)
                    for dt in embedded_templates:
                        clean = f"{{{{{dt.strip()}}}}}"
                        if not is_excluded_template(dt):
                            all_templates.add(clean)

                # If no creation_date yet, look for |publication date=
                if not creation_date:
                    pubdate_match = re.search(r'\|\s*[Pp]ublication\s+date\s*=\s*(.+)', wrapper_block, re.IGNORECASE)
                    if pubdate_match:
                        raw_pubdate = pubdate_match.group(1).strip()
                        pubdate_for_parsing = raw_pubdate.split('{{')[0].strip()
                        creation_date = extract_year_from_date_string(pubdate_for_parsing)

                        embedded_pub_templates = re.findall(r'\{\{([^\|\}\n]+)', raw_pubdate)
                        for dt in embedded_pub_templates:
                            clean = f"{{{{{dt.strip()}}}}}"
                            if not is_excluded_template(dt):
                                all_templates.add(clean)

                # Extract templates from |permission= field
                permission_match = re.search(r'\|\s*[Pp]ermission\s*=\s*(.+?)(?=\n\||\n*$)', wrapper_block, re.IGNORECASE | re.DOTALL)
                if permission_match:
                    permission_content = permission_match.group(1).strip()
                    embedded_templates = re.findall(r'\{\{([^\|\}\n]+)', permission_content)
                    for t in embedded_templates:
                        clean = f"{{{{{t.strip()}}}}}"
                        if not is_excluded_template(t):
                            all_templates.add(clean)

        # Top-level templates (outside of wrappers)
        top_level_matches = re.findall(r'^\s*\{\{([^\|\}\n]+)', wikitext, re.MULTILINE)
        for t in top_level_matches:
            clean = t.strip()
            if not is_excluded_template(clean) and clean not in WRAPPER_TEMPLATES:
                all_templates.add(f"{{{{{clean}}}}}")

        return sorted(all_templates), creation_date

    except Exception as e:
        print(f"Error extracting templates/date: {e}")
        return [], ''


def process_templates_for_category(include_term, exclude_term):
    """
    Main entry point: fetches Commons files in a target category and extracts template/date metadata.

    Steps:
    - Searches Commons for files in one category (e.g., "Media from Delpher") excluding another (e.g., "Scans from the Internet Archive").
    - For each file, retrieves wikitext and parses relevant templates and creation dates.
    - Outputs to console and saves results as an Excel file with URLs and template links.

    Args:
        include_term (str): Category to include (e.g., "Media from Delpher")
        exclude_term (str): Category to exclude (e.g., "Scans from the Internet Archive")

    Returns:
        None
    """
    try:
        file_titles = search_files_from_category_excluding_term(include_term, exclude_term)
        file_titles = list(set(file_titles))  # Remove duplicates
        records = []

        for title in file_titles:
            wikitext = get_wikitext(title)
            file_url = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(title.replace(' ', '_'))
            templates, creation_date = extract_templates_and_date(wikitext)

            # Create (template, URL) pairs here
            template_links = [
                (tpl, f"https://commons.wikimedia.org/wiki/Template:{tpl.strip('{}').replace(' ', '_')}")
                for tpl in templates
            ]

            # Console output
            template_console = ', '.join([f"{tpl} ({url})" for tpl, url in template_links])
            print(f"{file_url} - {len(template_links)} - Date: {creation_date} - {template_console}")

            # Flatten for Excel: one row with file, date, template-URL pairs
            row = [file_url, len(template_links), creation_date]
            for tpl, url in template_links:
                row.extend([tpl, url])
            records.append(row)

        if not records:
            print("No valid files processed.")
            return

        # Build Excel header
        max_tpls = max((len(r) - 3) // 2 for r in records)  # each template = 2 columns
        columns = ['File URL', 'NumberOfTemplates', 'DateOfCreation']
        for i in range(max_tpls):
            columns.extend([f'Template {i+1}', f'Template {i+1} URL'])

        df = pd.DataFrame(records, columns=columns)

        safe_category = include_term.replace(" ", "_")  # "Media_from_Delpher"
        timestamp = datetime.datetime.now().strftime("%d%m%Y")
        filename = f"{safe_category}-Extracted_copyright_templates-{timestamp}.xlsx"
        df.to_excel(filename, index=False)
        print(f"Results written to {filename}")

    except Exception as e:
        print(f"Error processing category: {e}")


# Entry point for script execution.
# When run directly (not imported), it triggers the main processing workflow
# and catches any unhandled exceptions at the top level.
if __name__ == '__main__':
    try:
        include_term = "Media from Delpher"
        exclude_term = "Scans from the Internet Archive"
        process_templates_for_category(include_term, exclude_term)
    except Exception as e:
        print(f"Unexpected error: {e}")

