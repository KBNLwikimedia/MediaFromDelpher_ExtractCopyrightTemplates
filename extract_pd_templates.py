"""
Extracting  public domain (PD)-like templates from Wikimedia Commons Files (for files in Category:Media from Delpher)

This script processes files on Wikimedia Commons that are categorized as
"Category:Media from Delpher" but not part of "Category:Scans from the Internet Archive"
(as files in this latter category can be safely regarded to be in the PD)

It extracts relevant top-level templates from the wikitext of each file, including templates embedded in "|permission=" fields
of known Commmons templates/wrappers like {{Information}}, {{Photograph}}, {{Artwork}}, or {{Book}}.

It excludes known irrelevant templates and writes results to an Excel file and prints
them to the terminal.

It performs the following steps:
- Uses the MediaWiki API to find and fetch relevant files.
- Retrieves the raw wikitext content of each file.
- Extracts top-level and embedded templates (excluding known irrelevant ones).
- Attempts to parse a simplified creation date from template metadata.
- Outputs the results to both the console and an Excel spreadsheet.

The final Excel file includes:
- The file URL
- Number of detected templates
- Parsed creation date
- Each template name and a link to its corresponding template page

Author: Olaf Janssen (via ChatGPT)
Latest update: 4 april 2025
User-Agent: OlafJanssenBot/1.0
Output: commons_templates_output.xlsx
"""

import requests
import re
import urllib.parse
import pandas as pd
import datetime

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
    'taken on'
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

import re

def extract_year_from_date_string(date_str):
    """
    Extracts a simplified date (typically a 4-digit year or a century) from a wikitext date string.

    This function handles:
    - {{complex date|century|20|adj1=early}} → 'Early 20th century'
    - {{circa|1939}} → '1939'
    - {{Other date|century|16}} or {{other date|century|16}} → '16th century'
    - {{other date|?}} → 'Unknown'
    - {{Taken on|1918-12-21}} → '1918'
    - {{other date|between|1555|1600}} → '1600'
    - {{ucfirst: {{other date|between|1555|1600}} }} → '1600'
    - Any 4-digit year in the string → that year
    - Fallback → stripped original string

    Args:
        date_str (str): The raw date string potentially containing Wikimedia templates.

    Returns:
        str: A human-readable date such as '1939', '20th century', or the stripped original string.
    """
    try:
        # Normalize for lowercase
        lower = date_str.lower()

        # Handle nested ucfirst wrapping: {{ucfirst: {{other date|between|1555|1600}} }}
        nested_match = re.search(r'\{\{ucfirst:\s*(\{\{.*?\}\})\s*\}\}', date_str, re.IGNORECASE)
        if nested_match:
            date_str = nested_match.group(1)  # Strip outer ucfirst and retry

        # Handle {{complex date|century|20|adj1=early}} → Early 20th century
        if '{{complex date' in lower:
            century_match = re.search(r'\|\s*century\s*\|\s*(\d{1,2})', date_str, re.IGNORECASE)
            adj_match = re.search(r'\|\s*adj1\s*=\s*(\w+)', date_str, re.IGNORECASE)
            if century_match:
                century = int(century_match.group(1))
                adjective = adj_match.group(1).capitalize() + ' ' if adj_match else ''
                return f"{adjective}{century}th century"

        # Handle {{circa|1939}} → 1939
        circa_match = re.search(r'\{\{circa\|(\d{4})\}\}', date_str, re.IGNORECASE)
        if circa_match:
            return circa_match.group(1)

        # Handle {{other date|century|16}} → 16th century
        century_match = re.search(r'\{\{\s*other date\s*\|\s*century\s*\|\s*(\d{1,2})', date_str, re.IGNORECASE)
        if century_match:
            return f"{century_match.group(1)}th century"

        # Handle {{other date|?}} → Unknown
        if re.search(r'\{\{\s*other date\s*\|\s*\?\s*\}\}', date_str, re.IGNORECASE):
            return "Unknown"

        # Handle {{Taken on|1918-12-21}} → 1918
        taken_on_match = re.search(r'\{\{\s*taken on\s*\|\s*(\d{4})-\d{2}-\d{2}', date_str, re.IGNORECASE)
        if taken_on_match:
            return taken_on_match.group(1)

        # Handle {{other date|between|1555|1600}} → 1600
        between_match = re.search(r'\{\{\s*other date\s*\|\s*between\s*\|\s*(\d{4})\s*\|\s*(\d{4})\s*\}\}', date_str, re.IGNORECASE)
        if between_match:
            return between_match.group(2)  # Return the later date

        # Catch any 4-digit year
        year_match = re.search(r'(\d{4})', date_str)
        if year_match:
            return year_match.group(1)

        # Fallback
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


def extract_templates_and_date(wikitext):
    """
    Extracts relevant templates and the creation date from a Wikimedia Commons file's wikitext.

    The function looks for known wrapper templates (e.g., {{Information}}, {{Artwork}}) and attempts to:
    - Extract the creation date from the |Date= field, parsing embedded templates when applicable.
    - Extract templates from the |Permission= field that may indicate license or source.
    - Identify top-level templates that are not excluded and are not wrapper templates.

    Args:
        wikitext (str): The raw wikitext content of a Wikimedia Commons file.

    Returns:
        tuple:
            - list[str]: A sorted list of unique relevant template names (in {{TemplateName}} format).
            - str: A simplified creation date (e.g., '1939' or 'Early 20th century'), or an empty string if unavailable.
    """
    try:
        all_templates = set()
        creation_date = ''

        for wrapper in WRAPPER_TEMPLATES:
            pattern = re.compile(r'\{\{\s*' + re.escape(wrapper) + r'.*?\n(.*?)\n\}\}', re.DOTALL | re.IGNORECASE)
            wrapper_match = pattern.search(wikitext)
            if wrapper_match:
                wrapper_block = wrapper_match.group(0)

                # Extract |Date= or |date=
                date_match = re.search(r'\s*\|\s*[Dd]ate\s*=\s*(.*)', wrapper_block)
                if date_match:
                    raw_date = date_match.group(1).strip()
                    creation_date = extract_year_from_date_string(raw_date)
                    embedded_date_templates = re.findall(r'\{\{([^\|\}\n]+)', raw_date)
                    for dt in embedded_date_templates:
                        clean = f"{{{{{dt.strip()}}}}}"
                        if not is_excluded_template(dt) and clean not in all_templates:
                            all_templates.add(clean)

                # Extract |Permission=
                permission_match = re.search(r'\s*\|\s*[Pp]ermission\s*=\s*(.*?)\n', wrapper_block, re.DOTALL)
                if permission_match:
                    permission_content = permission_match.group(1).strip()
                    embedded_templates = re.findall(r'\{\{([^\|\}\n]+)', permission_content)
                    for t in embedded_templates:
                        clean_name = t.strip()
                        if not is_excluded_template(clean_name):
                            all_templates.add(f"{{{{{clean_name}}}}}")

        # Top-level templates
        top_level_matches = re.findall(r'^\s*\{\{([^\|\}\n]+)', wikitext, re.MULTILINE)
        for t in top_level_matches:
            clean_name = t.strip()
            if not is_excluded_template(clean_name) and clean_name not in WRAPPER_TEMPLATES:
                all_templates.add(f"{{{{{clean_name}}}}}")

        return sorted(all_templates), creation_date
    except Exception as e:
        print(f"Error extracting templates/date: {e}")
        return [], ''



def process_templates_for_category(include_term, exclude_term):
    """
    Processes Wikimedia Commons files from a specific category and extracts relevant metadata.

    This function:
    - Searches for files in the "Media from Delpher" category, excluding those in
      "Scans from the Internet Archive".
    - Fetches the wikitext of each file.
    - Extracts relevant top-level and embedded templates (excluding known irrelevant ones).
    - Attempts to parse and simplify the creation date from the file's metadata.
    - Prints the results to the console in a readable format.
    - Saves all processed data into an Excel file called 'commons_templates_output.xlsx'.

    The Excel file includes:
    - File URL
    - Number of detected templates
    - Date of creation (if found)
    - Each template and its corresponding Wikimedia URL

    Returns:
        None
    """
    try:
        file_titles = search_files_from_category_excluding_term(include_term, exclude_term)
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
        timestamp = datetime.datetime.now().strftime("%d%m%Y-%H%M%S")
        filename = f"{safe_category}_commons_templates_output_{timestamp}.xlsx"
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

