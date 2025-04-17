## Extract and analyse PD-like templates from Wikimedia Commons files in 'Media from Delpher' category

### Purpose:
This script identifies potentially public domain (PD) or PD-like license templates
in Wikimedia Commons files categorized under:

* Category:Media from Delpher
* Excluding: Category:Scans from the Internet Archive

These templates are often indicative of public domain status, but not explicitly
tagged as such. The script extracts them, alongside simplified creation/publication
dates, for review and documentation purposes.

### Background:

### What this story aims to do

### What this story does NOT aim to do

### Key Features:

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
     - Excel file (`*_commons_templates_output_<date>-cleaned.xlsx`) is a munually
       cleaned version of the first file, where any non-copyright templates, incorrect dates and other 'noise' that we did not manage to get filtered out by the Python script have been manually removed as a post-processing step.

### Output:
- File URL
- Number of detected templates
- Simplified creation or publication date
- Template names and links to their Commons documentation pages

### Dependencies:
- Python 3.7+
- `requests`, `re`, `pandas`, `openpyxl`

### See also
* Same code as notebook on PAWS: https://hub-paws.wmcloud.org/user/OlafJanssen/lab/tree/MediaFromDelpher_ExtractCopyrightTemplates/extract_copyright_templates.ipynb

### Author:
- Olaf Janssen, Wikimedia coordinator @KB national library of the Netherlands (via ChatGPT)
- Last updated: 9 April 2025
- User-Agent: OlafJanssenBot/1.0

### License:
This script is CC0, so released into the public domain. You may freely use, adapt, and redistribute it.
