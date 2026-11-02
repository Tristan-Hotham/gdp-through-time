# The Wealth of Nations, Mapped

The world economy on one interactive map, from 10,000 BC to 2024. Before AD 1 only world totals exist (population and output per head, mostly reconstruction); from AD 1 to 1820 Angus Maddison's own regional estimates are drawn as striped regions; and for 169 countries the Maddison Project Database 2023 gives GDP, GDP per head, share of world GDP and growth, with a timeline, a ranking of the fifteen largest beside the map, a full series for every country and side-by-side comparison. Years without an estimate are hatched.

Interactive page: https://maps.tristanhotham.com/gdp-through-time/
Paper: https://doi.org/10.5281/zenodo.23899403
Blog post: https://blog.tristanhotham.com/2026/10/31/gdp-through-time/

## Headline results

- China and India made 45.2% of world output in 1820 (China 28.6%, India 16.6% from its 1821 estimate), 9.4% in 1950, 8.3% in 1973 and 30.2% in 2024. China's share was lowest in 1961 (4.2%), India's in 1979 (3.0%).
- Western Europe and the Western offshoots rose from 27.4% of world output in 1820 to 59.2% in 1913 and fell back to 30.2% in 2024.
- The US economy passed Britain's in 1862 and stayed ahead; US GDP per head passed Britain's in 1880 and for good in 1935. The US was larger than China by 1887 (no estimate for China between 1870 and 1887); China passed the US again, in purchasing power terms, in 2014. The US share of world output peaked at 29.7% in 1944; Britain's at 9.3% in 1870.
- Take-offs: Japan's GDP per head rose 6.0 times from 1950 to 1973 and passed Britain's in 1980; South Korea's rose 28 times from 1960 to 2024, passing Japan in 2019 and Britain in 2020; China's rose 12.2 times from 1978.
- Richest over poorest country by GDP per head (a million people or more): 5.2 times in 1820, 11.6 in 1913, 29.5 in 1950, 251 in 2024 (Qatar and the Central African Republic). The 90th over the 10th percentile country: 3.0 in 1820, 28.1 in 2000, 26.3 in 2024.
- Before the nations: world population was about 4.4 million in 10,000 BC (HYDE 3.2.1 central); for 3000 BC HYDE's range is 7.8 to 81.2 million. De Long's world GDP per head grows only 2.1 times from 10,000 BC to 1800, against 15.5 times since 1820. In Maddison's 2010 regional figures the Indian subcontinent and China made 57% of world output in AD 1, but 7 of his 11 regions sit at assumed round values of GDP per head.
- Coverage: 21,366 country-year estimates of GDP per head, but only 4,387 before 1820 (for 35 countries); 14 countries in AD 1, 11 in 1500, 55 in 1820, 146 in 1950.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; results embedded, map data fetched from `data/`). |
| `header.png` | Social card, 1200 x 630. |
| `data/panel.csv` | One row per country and year with an estimate of GDP per head: GDP per head (2011 int. $), population, whether population was interpolated, GDP, growth, source (Maddison or IMF extension) and IMF estimate flag. |
| `data/world.csv` | World GDP, population and GDP per head, 1820 to 2024, with how each year was obtained. |
| `data/world_longrun.csv` | World population (HYDE 3.2.1 central, low, high; McEvedy and Jones) and world GDP and GDP per head (De Long 1998; Maddison 2010), 10,000 BC to 1820, in 2011 dollars linked at 1820. |
| `data/regions_maddison2010.csv` | Maddison's (2010) 11 regions at AD 1, 1000, 1500, 1600, 1700 and 1820: GDP, population, GDP per head (1990 and linked 2011 dollars), share of the world. |
| `data/countries.csv` | Maddison units with display names, regions, first and last estimate. |
| `data/results.json` | Every number quoted on the page, in the paper, blog, collage and post. |
| `data/site.json`, `data/map_countries.geojson`, `data/map_regions_maddison2010.geojson` | Page data: compact series, simplified Natural Earth borders (with dissolved USSR, Yugoslavia and Czechoslovakia) and Maddison's regions. |
| `data/hist/` | Borders of the time: 52 simplified snapshots from historical-basemaps (GPL-3.0, licence file included). |
| `code/` | Scripts, run in order; page, paper and blog templates; `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, `wealth_of_nations.png`) and post text. |

## Method in brief

- National series: Maddison Project Database 2023 ("Full data"), GDP per head in 2011 international dollars and population, for present-day territories; the USSR, Yugoslavia and Czechoslovakia are shown whole until they broke up. Checked against a second copy of the release.
- 2022 to 2024: each series carried forward with IMF World Economic Outlook (October 2025) growth of real GDP per head at PPP and population (166 units; Cuba, North Korea and Syria held at 2022 in world totals).
- Total GDP = GDP per head x population; population interpolated log-linearly over gaps of up to 30 years (409 country-years).
- World GDP: Maddison's world estimates at benchmark years, interpolated between them before 1950; from 1950 the sum of countries scaled to Maddison's totals (scaling 0.9972 to 1.0043).
- Growth: average yearly change in GDP per head since the estimate closest to ten years earlier (5 to 15 years back).
- Map: a country without an estimate shows its nearest estimate up to 10 years away (dotted, can be switched off), otherwise hatched. Overtakes are judged only on years where both countries have their own estimate.
- Before 1820: world series from De Long (1998), HYDE 3.2.1 and McEvedy and Jones (1978), and Maddison's (2010) regions, all as transcribed by Roodman (2020); 1990-dollar series rescaled by one factor (1.694) to meet the 2023 database in 1820. Greenland, in Maddison's Western Europe, is not drawn.
- Caveats: estimates before 1820, and for much of the world before 1950, rest on thin evidence; before AD 1 they are largely assumption. PPP comparisons over centuries are approximate; GDP is not well-being; present-day borders are not historical states; database releases revise the past.

## How to rerun

Needs Python 3 with pandas, numpy, shapely, geopandas, pyproj, matplotlib, Pillow and fontTools, openpyxl, mapshaper (npm) for the map geometry, xelatex and pdftotext; node with Playwright for `code/qa.js`. Raw inputs and where they came from are listed in `code/common.py`.

```
python3 code/01_data.py        # Maddison 2023 + IMF extension: data/panel.csv, world.csv
python3 code/01b_longrun.py    # world before 1820 and Maddison 2010 regions
python3 code/02_results.py     # data/results.json
python3 code/03_geo.py         # borders, regions, historical snapshots (needs mapshaper)
python3 code/04_site_data.py   # data/site.json
python3 code/05_build_site.py  # index.html (and the checks of every worded claim)
python3 code/06_figures.py     # header, blog and paper figures
python3 code/07_paper.py       # paper PDF
python3 reddit/collage.py      # collage
python3 code/08_readme.py      # README, LICENSE, Reddit post
python3 code/09_release.py     # blog post, Zenodo files
```

## Sources and licences

- Maddison Project Database, version 2023. Bolt, J. and van Zanden, J. L. (2024), "Maddison style estimates of the evolution of the world economy: a new 2023 update", Journal of Economic Surveys. DataverseNL, https://doi.org/10.34894/INZBF2. CC BY 4.0. The paper lists the original studies behind the countries charted, as the database asks.
- IMF World Economic Outlook database, October 2025 (growth rates for 2023 to 2024 only).
- De Long, J. B. (1998), Estimates of world GDP, one million B.C. to present; Klein Goldewijk, K. et al. (2017), HYDE 3.2, Earth System Science Data 9; McEvedy, C. and Jones, R. (1978), Atlas of World Population History; Maddison, A. (2010), Historical Statistics of the World Economy 1 to 2008 AD; all as compiled by Roodman, D. (2020), "Modeling the Human Trajectory" (https://github.com/droodman/Modeling-Human-Trajectory). Only the published figures are used and credited.
- historical-basemaps, Andre Ourednik and contributors (https://github.com/aourednik/historical-basemaps), GPL-3.0; the simplified copies in `data/hist/` keep that licence.
- Natural Earth (public domain). Leaflet (BSD-2). Optional base maps on the page: Esri.

Code: MIT. Text, figures and derived data: CC BY 4.0. `data/hist/`: GPL-3.0.

## Citation

Hotham, T. (2026) The Wealth of Nations, Mapped: national output, output per head and shares of the world economy on an interactive map, with world estimates from 10,000 BC. Zenodo. https://doi.org/10.5281/zenodo.23899403

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
