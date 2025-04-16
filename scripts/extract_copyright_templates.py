"""
Extracting public domain (PD)-like templates from Wikimedia Commons files
========================================================================

Purpose:
--------
This script identifies potentially public domain (PD) or PD-like license templates
in Wikimedia Commons files categorized under:

    - Category:Media from Delpher
    - Excluding: Category:Scans from the Internet Archive

These templates are often indicative of public domain status, but not explicitly
tagged as such. The script extracts them, alongside simplified creation/publication
dates, for review and documentation purposes.

Key Features:
-------------
- Uses the MediaWiki API to search for Commons files in the desired category.
- Fetches the raw wikitext of each file page.
- Isolates wrapper templates like {{Information}}, {{Photograph}}, {{Artwork}}, and {{Book}}.
- Extracts relevant templates from top-level usage or embedded fields like:
  - |permission=
  - |date=
  - |publication date=
- Handles multiline and nested template values reliably.
- Extracts a simplified creation date from various formats:
  - {{circa|1930}}, {{taken on|1918-12-21}}, {{other date|between|1890|1900}}, etc.
- Supports date formats: YYYY, YYYY-MM, YYYY-MM-DD
- Returns the most recent valid year if multiple are present.
- Excludes known irrelevant templates via a robust filtering system.
- Outputs results to:
  - Console (one line per file with all extracted info)
  - Excel file (`*_commons_templates_output_<date>.xlsx`) with URLs and linked templates

Output:
-------
- File URL
- Number of detected templates
- Simplified creation or publication date
- Template names and links to their Commons documentation pages

Dependencies:
-------------
- Python 3.7+
- `requests`, `re`, `pandas`, `openpyxl`

Author:
-------
- Olaf Janssen, Wikimedia coordinator @KB national library of the Netherlands (via ChatGPT)
- Last updated: 9 April 2025
- User-Agent: OlafJanssenBot/1.0

License:
--------
This script is released into the public domain (CC0-style). Free to reuse, adapt, and distribute.
"""

import requests
import re
import urllib.parse
import pandas as pd
import datetime
import openpyxl
from pathlib import Path

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
    'i18n/as',
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
    Extracts a simplified year or century from a Wikimedia Commons-style date string.

    Handles:
    - Templates like {{circa|1939}}, {{taken on|YYYY-MM-DD}}, {{other date|...}}
    - Flexible formats: YYYY, YYYY-MM, YYYY-MM-DD
    - Nested templates (e.g. wrapped with {{ucfirst:...}})
    - Returns the most recent valid 4-digit year found (1000 ≤ year ≤ 2100)
    - Ignores metadata like:
        - accessdate=2013, archivedate=2022
        - {{Dead link|date=...}}, {{cite news|date=...}}, etc.

    Args:
        date_str (str): Raw wikitext string from a |date= or |publication date= field

    Returns:
        str: Parsed date (e.g., '1939', '20th century', or 'Unknown')
    """
    try:
        lower = date_str.lower()

        # --- Strip metadata noise that can corrupt fallback year parsing ---
        # Remove citation templates entirely
        date_str = re.sub(r'\{\{\s*cite\s+(news|web|book|journal)[^\}]*\}\}', '', date_str, flags=re.IGNORECASE)
        # Remove known non-creation date fields
        date_str = re.sub(r'\|\s*([Aa]ccessdate|[Aa]ccess-date|[Aa]rchivedate|[Aa]rchive-date)\s*=\s*[^\|\n]+', '', date_str, flags=re.IGNORECASE)
        date_str = re.sub(r'\{\{[Dd]ead link\|date=\w+\s+\d{4}.*?\}\}', '', date_str, flags=re.IGNORECASE)

        # --- Unwrap any ucfirst: {{...}} ---
        nested_match = re.search(r'\{\{[Uu][Cc]first:\s*(\{\{.*?\}\})\s*\}\}', date_str)
        if nested_match:
            date_str = nested_match.group(1)

        # --- {{complex date|century|20|adj1=early}} → Early 20th century ---
        if '{{complex date' in lower:
            century_match = re.search(r'\|\s*century\s*\|\s*(\d{1,2})', date_str)
            adj_match = re.search(r'\|\s*adj1\s*=\s*(\w+)', date_str)
            if century_match:
                century = int(century_match.group(1))
                adjective = adj_match.group(1).capitalize() + ' ' if adj_match else ''
                return f"{adjective}{century}th century"

        # --- {{circa|1939}} → 1939 ---
        circa_match = re.search(r'\{\{\s*[Cc]irca\s*\|\s*(\d{4})\s*\}\}', date_str)
        if circa_match:
            return circa_match.group(1)

        # --- {{other date|century|16}} → 16th century ---
        century_match = re.search(r'\{\{\s*[Oo]ther date\s*\|\s*century\s*\|\s*(\d{1,2})', date_str)
        if century_match:
            return f"{century_match.group(1)}th century"

        # --- {{other date|?|...}} → Unknown ---
        if re.search(r'\{\{\s*[Oo]ther date\s*\|\s*\?\s*\}\}', date_str):
            return "Unknown"

        # --- {{taken on|YYYY-MM-DD}} → YYYY ---
        taken_on_match = re.search(r'\{\{\s*[Tt]aken on\s*\|\s*(\d{4})-\d{2}-\d{2}', date_str)
        if taken_on_match:
            return taken_on_match.group(1)

        # --- Catch all other {{other date|...}} variations and extract latest year ---
        if '{{other date' in lower:
            all_years = re.findall(r'\d{4}', date_str)
            valid_years = [y for y in all_years if 1000 <= int(y) <= 2100]
            if valid_years:
                return max(valid_years)

        # --- Final fallback: any 4-digit year ---
        fallback_years = re.findall(r'\d{4}', date_str)
        valid_years = [y for y in fallback_years if 1000 <= int(y) <= 2100]
        if valid_years:
            return max(valid_years)

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
    Extracts the full content of a wrapper template block (e.g., {{Photograph}}, {{Information}})
    from the given wikitext, including nested templates and multiline fields.

    This function uses brace-depth tracking to ensure the entire balanced template
    is returned even if it contains deeply nested or multi-line sub-templates.

    Args:
        wikitext (str): The full page wikitext.
        template_name (str): The name of the wrapper template to extract.

    Returns:
        str: The full balanced block as a string, or an empty string if not found.
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


def extract_template_field(block, fieldname):
    """
    Extracts a specific |field= value from a wikitext template block (multiline-safe).

    Args:
        block (str): Template content (e.g., full {{Photograph ...}} block)
        fieldname (str): The name of the field (e.g., 'date')

    Returns:
        str: Extracted field value or empty string if not found
    """
    pattern = re.compile(rf'\|\s*{fieldname}\s*=\s*(.+?)(?=\n\||\n*$)', re.IGNORECASE | re.DOTALL)
    match = pattern.search(block)
    return match.group(1).strip() if match else ''


def extract_templates_and_date(wikitext):
    """
    Extracts relevant license/source templates and a simplified creation date from a file's wikitext.

    - Detects wrapper templates (e.g., {{Information}}, {{Photograph}}, {{Book}})
    - Extracts |date= and |publication date= values, even if multiline
    - Extracts embedded templates from |permission=, |date=, etc.
    - Filters out known irrelevant or decorative templates
    - Also finds top-level templates (not nested in wrappers)
    - Date extraction prioritizes the most recent 4-digit year

    Args:
        wikitext (str): The raw wikitext from a Commons file

    Returns:
        tuple:
            list[str]: Sorted list of template names (e.g. ['{{PD-old}}', '{{Anonymous-EU}}'])
            str: Simplified creation date (e.g. '1939', 'Unknown', '20th century')
    """
    try:
        all_templates = set()
        creation_date = ''

        for wrapper in WRAPPER_TEMPLATES:
            wrapper_block = extract_balanced_template(wikitext, wrapper)
            if wrapper_block:
                # --- DATE ---
                raw_date = extract_template_field(wrapper_block, 'date')
                if raw_date:
                    creation_date = extract_year_from_date_string(raw_date)
                    embedded_templates = re.findall(r'\{\{([^\|\}\n]+)', raw_date)
                    for dt in embedded_templates:
                        clean = f"{{{{{dt.strip()}}}}}"
                        if not is_excluded_template(dt):
                            all_templates.add(clean)

                # --- PUBLICATION DATE ---
                if not creation_date:
                    raw_pubdate = extract_template_field(wrapper_block, 'publication date')
                    if raw_pubdate:
                        creation_date = extract_year_from_date_string(raw_pubdate)
                        embedded_templates = re.findall(r'\{\{([^\|\}\n]+)', raw_pubdate)
                        for dt in embedded_templates:
                            clean = f"{{{{{dt.strip()}}}}}"
                            if not is_excluded_template(dt):
                                all_templates.add(clean)

                # --- PERMISSION ---
                raw_permission = extract_template_field(wrapper_block, 'permission')
                if raw_permission:
                    embedded_templates = re.findall(r'\{\{([^\|\}\n]+)', raw_permission)
                    for t in embedded_templates:
                        clean = f"{{{{{t.strip()}}}}}"
                        if not is_excluded_template(t):
                            all_templates.add(clean)

        # --- TOP-LEVEL templates ---
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

        # Define the data folder path (relative to the script location)
        data_folder = Path(__file__).resolve().parent.parent / "data"
        # Ensure the folder exists
        data_folder.mkdir(parents=True, exist_ok=True)
        # Full output path
        output_path = data_folder / filename

        # Write Excel file
        df.to_excel(output_path, index=False)
        print(f"✅ Results written to: {output_path}")


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

