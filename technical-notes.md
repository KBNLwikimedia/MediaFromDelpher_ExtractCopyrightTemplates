# Technical notes (under construction)

*Latest update*: xx May 2025

Work on this: 
This page gives more info about 
1. The scripts 'extract_copyright_templates.py' and 'template_usage_summary.py' and 
2 The data files in the data folder
3. The datavisualisation from datawrapper, created via the datawrapper API
4. ...xxx 

## Key Features of script 'template_usage_summary.py':
TO ADD

## Key Features of script 'extract_copyright_templates.py':

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

<!-- 

==============================

-----------FROM GLAMOROUS.HTML--------- 

## Repository structure and functional descriptions

What are the main files and folders in this repo, and what do they do?

### Main folder

* [GLAMorousToHTML.py](GLAMorousToHTML.py) : The main script  
* [GLAMorousToHTML_functions.py](GLAMorousToHTML_functions.py): 

[category_logo_dict.json](category_logo_dict.json)
[category_logo_dict_nde.json](category_logo_dict_nde.json)

[build_html.py](build_html.py)

[build_excel.py](build_excel.py)

[analytics.py](analytics.py)

* [add_wikidata.py](add_wikidata.py)
* [wikidata_functions.py](wikidata_functions.py): 
* 
* [general.py](general.py)
* [generate_report_markup.py](generate_report_markup.py)

* [geolocations.py](geolocations.py)
* [geolocations_functions.py](geolocations_functions.py)
* [geo_map.html](geo_map.html)

* [pob_pod_map.py](pob_pod_map.py)
* [pob_pod_map_functions.py](pob_pod_map_functions.py)
* [pod_pob_map.html](pod_pob_map.html)

[wikidata_cache.json](wikidata_cache.json)


[README.md](README.md) - this file

[pagetemplate.html](pagetemplate.html)

[GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_10012024.html](GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_10012024.html)

### Subfolders
* [site](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/site) : 
  * site/nde : 
  * site/logos : 
  * site/flags : 

* [data](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/data) : 
  * data/nde : 
  * data/nde/aggregated : 
* [reports](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/reports) : 
* [stories](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/stories) : 

------------------------------
--> 




