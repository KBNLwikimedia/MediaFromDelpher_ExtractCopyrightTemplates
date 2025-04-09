## Extract PD-like templates from Wikimedia Commons files in 'Media from Delpher' category

### Overview
This script identifies and extracts potentially Public Domain (PD) or PD-like licensing templates from files hosted on Wikimedia Commons, specifically those categorized under:

* Category:Media from Delpher
* But excluding: Category:Scans from the Internet Archive

The goal is to help detect files with licensing metadata that suggest they are in the public domain, but which are not explicitly tagged using standard Internet Archive or PD templates.

### How it works:
1. **File Discovery**
Uses the MediaWiki API to query Commons for files in the target category (`Media from Delpher`)
   while excluding those in a known-safe PD category (`Scans from the Internet Archive`).


2. **Wikitext Retrieval**
For each matching file, the script fetches the raw wikitext (template code, metadata, and fields).


3. **Template Extraction**
The script identifies templates from two sources:
 * Top-level templates (directly used on the file page)
 * Templates embedded within the `|permission=` or `|date=` fields of wrapper templates like:
     `{{Information}}`, `{{Book}}`, `{{Photograph}}`, or `{{Artwork}}`
 * Templates are filtered using several exclusion rules:
   - Known irrelevant or decorative templates (see `EXCLUDED_TEMPLATES`)
   - Templates with namespaced prefixes (e.g., `User:`, `Creator:`)
   - Language-tagging templates like `{{en}}`, `{{nl}}`, etc.
   - Utility templates like `{{DEFAULTSORT}}` or `{{ucfirst}}`


4. **Date Extraction**
Attempts to derive a simplified creation or publication date from template metadata:
   - Recognizes formats like `{{circa|1930}}`, `{{other date|between|1920|1935}}`, or `1935-06-01`
   - If no date is available, leaves field blank or as `"Unknown"`


5. **Output**
   * Console output: File URL, parsed date, detected template names with links
   * Excel file: A table with rows per file and columns for:
     - File URL
     - Parsed date
     - Number of templates
     - Each template name and a link to its documentation page

### Configuration & Customization:

- To change which files are analyzed, modify:
  * `include_term = "Media from Delpher"`
  * `exclude_term = "Scans from the Internet Archive"`

- Output is saved as:
  * `Media_from_Delpher_commons_templates_output_<DATE>.xlsx`

- You can limit the number of processed files for testing by modifying:
  *  `limit=20` in the `search_files_from_category_excluding_term()` function call.

### Requirements:
- Python 3.7+
- `requests`
- `pandas`
- `openpyxl` (for Excel export)

### Author:
- Olaf Janssen, Wikimedia coordinator @KB national library of the Netherlands (via ChatGPT)
- Last updated: 9 April 2025
- User-Agent: OlafJanssenBot/1.0

### License:
This script is CC0, so released into the public domain. You may freely use, adapt, and redistribute it.
