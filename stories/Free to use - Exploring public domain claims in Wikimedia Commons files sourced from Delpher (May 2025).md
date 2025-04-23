# Free to use? Exploring public domain claims in Wikimedia Commons files sourced from Delpher (May 2025)
<sup>Olaf Janssen, xx May 2025</sup>

This article is also [available as PDF](ongithub.pdf).

<img src="../media/wmc-logo.jpg" align="right" width="110" hspace="20" alt="Logo Wikimedia Commons"/>

<img src="../media/delpher_logo_new.png" align="right" width="170" hspace="20" alt="Logo Delpher"/>

_**[Delpher](https://www.delpher.nl)** offers access to millions of digitized pages from Dutch historical newspapers, books, and magazines — a valuable resource frequently used on Wikimedia Commons. In the first part of this data story, we examine how the Wikimedia community has assigned public domain status to Commons files that have been [sourced from Delpher](https://commons.wikimedia.org/wiki/Category:Media_from_Delpher). In the second part, we explore the validity of these claims and assess whether they align with the actual copyright status of these works._

----------------

Much of the historical content from Delpher falls into the public domain due to its age and can therefore be uploaded to Wikimedia Commons without concern. At the same time, the KB — being the operator of Delpher — has a contractual obligation towards authors and publishers to monitor potential copyright infringements and to prevent them as much as possible, including Delpher content that has been uploaded to Wikimedia Commons.

For this reason, the KB wants to gain a better understanding of which newspaper articles, books, magazines and other materials from Delpher have been uploaded to Wikimedia Commons, and how public domain claims to those files have been assigned by the Wikimedia community. In doing so, it is important to emphasize that the KB has absolutely **no** intention to act as a copyright police force. The goal is to work together with the Wikimedia community to handle copyright matters responsibly, with respect for both creators and users.

## Key figures and findings
The most important key figures and findings of this story are:
* kf 1
* kf 2
* kf 3
* 

### What this article aims to do
1. Provide a **practical case study** of how public domain claims are applied in a real-world environment — specifically, how Wikimedia Commons contributors handle copyright claims for [files sourced from Delpher](https://commons.wikimedia.org/wiki/Category:Media_from_Delpher).
2. Offer insight into the **complexity and messiness** of public domain claims on Wikimedia Commons — even for the relatively simple case where a single source of digitized materials (Delpher) comes from a single country (the Netherlands).
3. Explore **how accurately the Wikimedia community applies public domain claims**, and assess to what extent potential copyright violations may occur — including whether serious violations are present.
4. Share a **practical data story** of how to machine-analyze and visualize copyright claims for files in (subsets of) Wikimedia Commons using data analysis and visualization techniques.  

### What this article does <u>not</u> aim to do
1. Provide a **comprehensive overview of all public domain claims** on Wikimedia Commons. This article focuses specifically on files sourced from Delpher, which is a manageable subset of the total number of files in Commons.
2. Provide a **formal and/or detailed legal analysis** of every public domain claim for these files — such an approach would be far too extensive for the scope of this data story.
3. XXXXXXXXX **Identify and flag every potential copyright infringement** — aside from highlighting a few obvious and illustrative cases mentioned later in this story. XXXXXXXXXXXX (besides the 5 obvious cases mention below)
4. Offer **recommendations or proposals on how to simplify public domain claims** on Wikimedia Commons. This article takes the current public domain landscape "as is," observing how it functions in practice without suggesting reform.

## Copyrights templates in Wikimedia Commons

Wikimedia Commons is one of the largest open-access media repositories in the world, used daily by Wikipedia and countless other businesses and projects. To protect the open and reusable nature of its content, strict legal rules must be followed for files that are uploaded to Commons:  

1) All uploaded files must either be:  
   - Out of copyright — meaning they are in the public domain, either passively [because copyrights have expired](https://gowlingwlg.com/en/insights-resources/articles/2024/public-domain-what-happens-when-copyright-expires), or because the rights holder has waived any copyrights on the files, actively releasing them into the public domain, for instance by using a [CC0 license](https://creativecommons.org/public-domain/cc0/).  
   - Freely licensed — under licenses that allow reuse and modification, most commonly [CC-BY](https://creativecommons.org/licenses/by/4.0/), [CC-BY-SA](https://creativecommons.org/licenses/by-sa/4.0/), or equivalent.

2) These copyright claims must be explicitly and unambiguously added to the file description page.
See for instance the [public domain claim](https://commons.wikimedia.org/w/index.php?title=File:1923_Jos._Schrijnen_%E2%80%94_MMKB02_000118508_00004_image_(cropped).jpg&action=edit&section=2) stated in [this portrait](https://commons.wikimedia.org/wiki/File:1923_Jos._Schrijnen_%E2%80%94_MMKB02_000118508_00004_image_(cropped).jpg) made by the Dutch photograhper [Toni Arens-Tepe](https://nl.wikipedia.org/wiki/Toni_Arens-Tepe) (1883–1947).
 
3) These claims are typically expressed through standardized copyright templates (also known as *license tags*). These templates are meant to ensure clarity, uniformity and standardization when declaring copyright status of files. Templates on Commons can be recognized by the double curly brackets they are called by, for instance 
   - [\{\{PD-old-70\}\}](https://commons.wikimedia.org/wiki/Template:PD-old-70) — The file is in the public domain because the creator of the underlying work died more than 70 years ago.  
   - [\{\{CC-BY-SA-4.0\}\}](https://commons.wikimedia.org/wiki/Template:Cc-by-sa-4.0) — Creative Commons Attribution-ShareAlike 4.0 license.  
   - [\{\{PD-ineligible\}\}](https://commons.wikimedia.org/wiki/Template:PD-ineligible) — The file is in the public domain because it (and/or its underlying work) lacks sufficient originality to be eligible for copyright protection. 

### The copyright template jungle   

But here’s the problem: although the purpose of these templates is to provide a clear and standardized way to declare copyright status, the practical reality is that the license tagging system — built over the years by the international Wikimedia community — has become very complex. The number of different copyright templates in use on Commons is enormous.

To get a sense of this complexity, take a look at [this summary of the most common template types](https://commons.wikimedia.org/wiki/Commons:Copyright_tags) or explore this nested [overview of several thousands(!) of copyright templates](https://commons.wikimedia.org/wiki/Category:License_tags) being used on Commons.

Both insiders and outsiders will struggle to find their ways in this system, it can feel like working through a jungle of overlapping licensing options and confusing terminology, undermining the intended simplicity and standardization.

However, this complexity is not entirely surprising. Wikimedia Commons accepts media from any country and any historical period, and must therefore be able to handle the copyright rules and exceptions from dozens of legal systems worldwide. This elaborate system is necessary because Wikimedia Commons is a global, evolving platform. Templates are regularly added or updated as contributors find new sources for uploads or as local copyright regulations change.

=============================

## Zooming in: public domain templates in Wikimedia Commons
Even if we narrow the scope and look only at public domain templates, things remain pretty complicated. And even if we only cionsider public domain templates, the variety and numbers are still pretty large.

https://commons.wikimedia.org/wiki/Commons:Copyright_tags/General_public_domain - give a ioverview of over 70  General public domain templates

The comlexity becomwes 
https://commons.wikimedia.org/wiki/Category:PD_license_tags and its subcategpries, whetrw amny [country specigfic pd templas](https://commons.wikimedia.org/wiki/Commons:Copyright_tags/Country-specific_tags) (reflecting local copyright law) are listed. 

In addition to all these couintry specigid, an extra layer of complexity is added:
Every file on Wikimedia Commons must include a U.S. public domain justification**  
 because the Commons servers are located in the United States, and U.S. copyright law applies.
To add to the complexity, becausee Wikimedia servers are in the US, all fies stored there must also compy to US copyright and public domain regulations, which [can be very complicatred](https://guides.library.cornell.edu/copyright/publicdomain/) and different from the jursdixctins in the country of origin.

In practice This means that for many Commons files, multiple templates are required:  
- One (or more) template(s) describing the copyright situation in the country of origin;  
- And an additional template confirming the public domain status in the United States.

<a href="../media/wmc-pd-templates-sample.png"><img src="../media/wmc-pd-templates-sample.png" align="left" width="100%" vspace="5" alt="A non-exhaustive collage of screenshots of public domain template description pages used in Wikimedia Commons files that have been sourced from Delpher."/></a>
<br clear="all"/><sub>*A collage of screenshots of public domain template description pages, as used in Wikimedia Commons [files that have been sourced from Delpher](https://commons.wikimedia.org/wiki/Category:Media_from_Delpher) (Click to enlarge).<br/>Image license: <a href="https://creativecommons.org/licenses/by-sa/4.0/deed.nl" target="_blank">CC-BY-SA 4.0</a> / Olaf Janssen, KB national library of the Netherlands.*</sub>

===============================================

##  Zooming in further: licensing templates used in Delpher fioles

1 Expla nthat all files have been brohju together in the Caterogy Mdioa from depher

2 xpln how the sxcrit you made helped in trackuing doan all templated that are used in the 62oo files in Cat:media fronm Depher

date: 9 april 2025

Expln that I wot a Franenstein Puthin script that extracted the copyright templaat and dataOfCreation from the files in that categorty. see the technical notes for more detaiols 

3 Expan tha files from the IA are excluided fronm the sanayses - https://commons.wikimedia.org/wiki/File:%27s_Gravenhaagsche_courant_02-09-1822_(IA_ddd_010124645_mpeg21).pdf . 
https://commons.wikimedia.org/wiki/Category:Scans_from_the_Internet_Archive
- all the files have the {{PD-old-70-expired}} template

Fromn the total of 6496 files in this cat dd 9-4-2025 https://petscan.wmcloud.org/?templates_any=&language=commons&combination=subset&search_max_results=500&langs_labels_yes=&cb_labels_no_l=1&negcats=Scans+from+the+Internet+Archive&format=html&project=wikimedia&cb_labels_yes_l=1&pagepile=&before=20250409&active_tab=tab_pageprops&links_to_all=&min_sitelink_count=&interface_language=en&min_redlink_count=1&only_new=on&ns%5B6%5D=1&sitelinks_any=&categories=Media+from+Delpher&cb_labels_any_l=1&wikidata_source_sites=&rxp_filter=&langs_labels_any=&manual_list_wiki=&doit=
ecluding the IA scans**

we were able to tretrioeve 6,248 distinct filies, that had both template information as well as a date of creation 

Dd 09 May 2025 thi category 


## Section 2: Tracking the copyright templates in Wikimedia Commons, for Media from Delpher Delpher
Zoom in on Categortry: Media from Delpher Delpher


## Section 3 

<div style="min-height:839px" id="datawrapper-vis-gZqMt"><script type="text/javascript" defer src="https://datawrapper.dwcdn.net/gZqMt/embed.js" charset="utf-8" data-target="#datawrapper-vis-gZqMt"></script><noscript><img src="https://datawrapper.dwcdn.net/gZqMt/full.png" alt="This donut chart shows the reasons why media files that were sourced from Delpher are out of copyright, according to  Wikimedia Commons. For instance, the 6,191 files in the blue sector are in the public domain because the historical newspapers, books and magazines they were sourced from, are too old to carry copyrights. One file can contain multiple out-of-copyright claims. All such claims are taken &quot;as observed&quot;. Data as of 9 April 2025." /></noscript></div>


After having done the scan, from the Excel, we could quite ealiy look for opublications that possibly did copyvio, based on the yerar of publication. We looked for files that were published in the last 70 years, and that were not marked as public domain. We found 5 files that were published in the last 70 years, and that were not marked as public domain.
Example of delted file: artiocle in Telgraaf from 1985
In total 5 deletion trequerst due to copyvio, all of which were granted and the fielswere deleted very quicly. 

* https://commons.wikimedia.org/w/index.php?title=File:Newspaper_article_-_De_Telegraaf_-_Date_09-07-1985_-_Bank_robbery_-_Rob_Kaman_-_Kickboxing.jpg&action=edit&redlink=1
* https://commons.wikimedia.org/w/index.php?title=File:Advertentie_Pottenbakkerij_Henk_en_Lieske_Potters_in_Trouw_dd_22_maart_1974.jpg&action=edit&redlink=1
* https://commons.wikimedia.org/w/index.php?title=File:Ad_25_6_1966.jpg&action=edit&redlink=1
* https://commons.wikimedia.org/w/index.php?title=File:Een_oproep_van_Duco_Sickinghe_(1888-1983)_in_dagblad_Het_Binnenhof_en_Het_Vaderland_(1956).jpg&action=edit&redlink=1
* https://commons.wikimedia.org/w/index.php?title=File:Een_oproep_van_Duco_Sickinghe_(1888-1983)_in_dagblad_Het_Binnenhof_en_Het_Vaderland_(1956).jpg&action=edit&redlink=1

><big><b><em>Quote 1</em></b></big>

><big><b><em>Quote 2</em></b></big>

### Section 2.1 



Explan which templates have been found

<div style="min-height:766px" id="datawrapper-vis-PJ96v"><script type="text/javascript" defer src="https://datawrapper.dwcdn.net/PJ96v/embed.js" charset="utf-8" data-target="#datawrapper-vis-PJ96v"></script><noscript><img src="https://datawrapper.dwcdn.net/PJ96v/full.png" alt="This table explains the 39 distinct copyright templates that are used in Wikimedia Commons media files that were sourced from Delpher.The templates are sorted and color-coded by the main reason why they categorize files into the public domain. The template usage is taken &quot;as observed&quot; Data as of 9 April 2025." /></noscript></div>



<div style="min-height:1665px" id="datawrapper-vis-UewJt"><script type="text/javascript" defer src="https://datawrapper.dwcdn.net/UewJt/embed.js" charset="utf-8" data-target="#datawrapper-vis-UewJt"></script><noscript><img src="https://datawrapper.dwcdn.net/UewJt/full.png" alt="This chart shows how often which copyright templates are used in Wikimedia Commons media files that were sourced from Delpher. The bars are grouped by the main reason why the files are in the public domain. The template usage is taken \&quot;as observed\&quot;. The 3 key figures are: 1) Total number of distinct media files: 6,248. 2) Total number of template usages: 6,329 (one file can contain multiple copyright templates). 3) Total number of distinct templates used: 39. Data as of 9 April 2025." /></noscript></div>


<!-- <a href="../media/media-from-delpher-in-wikimedia-commons-usage-of-copyright-templates-grouped-by-reason.png" target="_blank"><img src="../media/media-from-delpher-in-wikimedia-commons-usage-of-copyright-templates-grouped-by-reason.png" border="1" align="left" width="90%" hspace="30" alt="This chart shows how often which copyright templates are used in Wikimedia Commons media files that were sourced from Delpher. The bars are grouped by the main reason why the files are in the public domain. The template usage is taken \&quot;as observed\&quot;. The 3 key figures are: 1) Total number of distinct media files: 6,248. 2) Total number of template usages: 6,329 (one file can contain multiple copyright templates). 3) Total number of distinct templates used: 39. Data as of 9 April 2025."/></a>
<br clear="all"/> -->

### Section 2.1 - Zooming in on copyrights expired because of age 

Next., lets';s zoom in on the copyright templates that are used for files that are in the public domain because of age. The blue colors.
 In total theis comprises 24 templates 6191 used in xx distinct files


## Section 3 

## Raw data
All data used for the visualisations and analytics in this article is [available on Github](https://github.com/KBNLwikimedia/xxxx). You can also [download the main Excel file directly](https://kbnlwikimedia.github.io/xxxx.xlsx).

## About the authors
<img align="left" src="../media/389px-Olaf_Janssen_at_GLAM_WIKI_Tel_Aviv_Conference_2018.JPG" width="50" hspace="5" alt="Portrait of Olaf Janssen in 2018."/>

<img src="../media/kblogo.png" align="right" hspace="20" width="150" alt="Logo of the KB, the national library of the Netherlands"/>

Olaf Janssen is the [Wikimedia coördinator](https://www.kb.nl/over-ons/experts/olaf-janssen) of the KB, the national library of the Netherlands. He contributes to [Wikipedia](https://nl.wikipedia.org/wiki/Wikipedia:GLAM/Koninklijke_Bibliotheek_en_Nationaal_Archief), [Wikimedia Commons](https://commons.wikimedia.org/wiki/Commons:Koninklijke_Bibliotheek) and [Wikidata](https://www.wikidata.org/wiki/Wikidata:GLAM/Koninklijke_Bibliotheek_Nederland) as [User:OlafJanssen](https://commons.wikimedia.org/wiki/User:OlafJanssen). ORCID: [0000-0002-9058-9941](https://orcid.org/0000-0002-9058-9941).

## Reusing this article 
The text and data visualisations of this article have been released under [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/deed.en) CC-BY 4.0 license.<br/> 
<img src="../media/cc-by.png" width="120" hspace="20" align="right" alt="Logo of the CC-BY license"/>

*Citation*: Janssen, O.D. (2025). ‘xxxxxx. [https://doi.org/10.5281/zenodo.xxxx](https://doi.org/10.5281/zenodo.xxxx).<br/> 

Attribution: *KB, national library of the Netherlands / Olaf Janssen, CC-BY 4.0*

Raw data: CC0, so released into the public domain. You may freely use, adapt, and redistribute it.

## Identifiers and URLs of this article
Persistent:
* DOI (Zenodo): [https://doi.org/10.5281/zenodo.xxx](https://doi.org/10.5281/zenodo.xxxxx)
* Wikimedia Commons: [https://commons.wikimedia.org/entity/xxxx](https://commons.wikimedia.org/entity/xxxx)

Non-persistent: 
* Github: [https://kbnlwikimedia.github.io/xxxx.html](https://kbnlwikimedia.github.io/xxxxx.html)