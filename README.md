## Extracting  public domain (PD)-like templates from Wikimedia Commons Files (for files in Category:Media from Delpher)

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
Output: Media_from_Delpher_commons_templates_output_04042025-raw.xlsx
