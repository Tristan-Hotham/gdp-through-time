"""README.md, LICENSE and reddit/post.md, with numbers from data/results.json. https://doi.org/10.5281/zenodo.23899403 and https://blog.tristanhotham.com/2026/10/31/gdp-through-time/ stay as placeholders."""
from common import *

R = jload(f"{DATA}/results.json")
D, S, O, T, G, LR = R["data"], R["share"], R["overtake"], R["takeoff"], R["gap"], R["longrun"]
ci, ws = R["china_india"], R["west_share"]
L = LAST
pc = lambda v: f"{v:.1f}%"

readme = f"""# The Wealth of Nations, Mapped

The world economy on one interactive map, from 10,000 BC to {L}. Before AD 1 only world totals exist (population and output per head, mostly reconstruction); from AD 1 to 1820 Angus Maddison's own regional estimates are drawn as striped regions; and for {D['countries']} countries the Maddison Project Database 2023 gives GDP, GDP per head, share of world GDP and growth, with a timeline, a ranking of the fifteen largest beside the map, a full series for every country and side-by-side comparison. Years without an estimate are hatched.

Interactive page: https://maps.tristanhotham.com/gdp-through-time/
Paper: {{https://doi.org/10.5281/zenodo.23899403}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/gdp-through-time/}}

## Headline results

- China and India made {pc(ci['1820'])} of world output in 1820 (China {pc(S['CHN']['1820'])}, India {pc(S['IND']['1820'])} from its 1821 estimate), {pc(ci['1950'])} in 1950, {pc(ci['1973'])} in 1973 and {pc(ci[str(L)])} in {L}. China's share was lowest in {S['CHN']['low']['year']} ({pc(S['CHN']['low']['pct'])}), India's in {S['IND']['low']['year']} ({pc(S['IND']['low']['pct'])}).
- Western Europe and the Western offshoots rose from {pc(ws['1820'])} of world output in 1820 to {pc(ws['1913'])} in 1913 and fell back to {pc(ws[str(L)])} in {L}.
- The US economy passed Britain's in {O['usa_gbr_gdp']['first']} and stayed ahead; US GDP per head passed Britain's in {O['usa_gbr_pc']['first']} and for good in {O['usa_gbr_pc']['for_good']}. The US was larger than China by {O['usa_chn_gdp']['first']} (no estimate for China between {O['usa_chn_gdp']['china_prev_estimate']} and {O['usa_chn_gdp']['first']}); China passed the US again, in purchasing power terms, in {O['chn_usa_gdp']['first']}. The US share of world output peaked at {pc(S['USA']['peak']['pct'])} in {S['USA']['peak']['year']}; Britain's at {pc(S['GBR']['peak']['pct'])} in {S['GBR']['peak']['year']}.
- Take-offs: Japan's GDP per head rose {T['jpn']['x_50_73']:.1f} times from 1950 to 1973 and passed Britain's in {O['jpn_gbr_pc']['first']}; South Korea's rose {T['kor']['x_60_last']:.0f} times from 1960 to {L}, passing Japan in {O['kor_jpn_pc']['first']} and Britain in {O['kor_gbr_pc']['first']}; China's rose {T['chn']['x_78_last']:.1f} times from 1978.
- Richest over poorest country by GDP per head (a million people or more): {G['1820']['ratio']:.1f} times in 1820, {G['1913']['ratio']:.1f} in 1913, {G['1950']['ratio']:.1f} in 1950, {G[str(L)]['ratio']:.0f} in {L} ({G[str(L)]['richest']} and the {G[str(L)]['poorest']}). The 90th over the 10th percentile country: {G['1820']['p90_p10']:.1f} in 1820, {G['2000']['p90_p10']:.1f} in 2000, {G[str(L)]['p90_p10']:.1f} in {L}.
- Before the nations: world population was about {LR['pop']['-10000']['hyde']} million in 10,000 BC (HYDE 3.2.1 central); for 3000 BC HYDE's range is {LR['pop']['-3000']['lo']} to {LR['pop']['-3000']['hi']} million. De Long's world GDP per head grows only {LR['pc_x_delong']} times from 10,000 BC to 1800, against {LR['pc_x_since_1820']} times since 1820. In Maddison's 2010 regional figures the Indian subcontinent and China made {LR['ci_ad1']:.0f}% of world output in AD 1, but {LR['assumed_ad1']} of his {LR['n_regions']} regions sit at assumed round values of GDP per head.
- Coverage: {D['estimates']:,} country-year estimates of GDP per head, but only {D['pre1820']:,} before 1820 (for {D['pre1820_countries']} countries); {D['ad1_n']} countries in AD 1, {D['y1500_n']} in 1500, {D['y1820_n']} in 1820, {D['y1950_n']} in 1950.

## Files

| File | What it is |
|---|---|
| `index.html` | The interactive page (built by `code/05_build_site.py`; results embedded, map data fetched from `data/`). |
| `header.png` | Social card, 1200 x 630. |
| `data/panel.csv` | One row per country and year with an estimate of GDP per head: GDP per head (2011 int. $), population, whether population was interpolated, GDP, growth, source (Maddison or IMF extension) and IMF estimate flag. |
| `data/world.csv` | World GDP, population and GDP per head, 1820 to {L}, with how each year was obtained. |
| `data/world_longrun.csv` | World population (HYDE 3.2.1 central, low, high; McEvedy and Jones) and world GDP and GDP per head (De Long 1998; Maddison 2010), 10,000 BC to 1820, in 2011 dollars linked at 1820. |
| `data/regions_maddison2010.csv` | Maddison's (2010) {LR['n_regions']} regions at AD 1, 1000, 1500, 1600, 1700 and 1820: GDP, population, GDP per head (1990 and linked 2011 dollars), share of the world. |
| `data/countries.csv` | Maddison units with display names, regions, first and last estimate. |
| `data/results.json` | Every number quoted on the page, in the paper, blog, collage and post. |
| `data/site.json`, `data/map_countries.geojson`, `data/map_regions_maddison2010.geojson` | Page data: compact series, simplified Natural Earth borders (with dissolved USSR, Yugoslavia and Czechoslovakia) and Maddison's regions. |
| `data/hist/` | Borders of the time: {R['hist_n']} simplified snapshots from historical-basemaps (GPL-3.0, licence file included). |
| `code/` | Scripts, run in order; page, paper and blog templates; `qa.js`. |
| `release/` | Paper (`paper/`), blog post and figures (`blog/`), Zenodo files (`zenodo/`). |
| `reddit/` | Collage (`collage.py`, `wealth_of_nations.png`) and post text. |

## Method in brief

- National series: Maddison Project Database 2023 ("Full data"), GDP per head in 2011 international dollars and population, for present-day territories; the USSR, Yugoslavia and Czechoslovakia are shown whole until they broke up. Checked against a second copy of the release.
- {LAST_MPD} to {L}: each series carried forward with IMF World Economic Outlook (October 2025) growth of real GDP per head at PPP and population ({D['ext_countries']} units; Cuba, North Korea and Syria held at {LAST_MPD} in world totals).
- Total GDP = GDP per head x population; population interpolated log-linearly over gaps of up to {POP_GAP} years ({D['pop_interp']} country-years).
- World GDP: Maddison's world estimates at benchmark years, interpolated between them before 1950; from 1950 the sum of countries scaled to Maddison's totals (scaling {D['world_ratio_min']} to {D['world_ratio_max']}).
- Growth: average yearly change in GDP per head since the estimate closest to ten years earlier (5 to 15 years back).
- Map: a country without an estimate shows its nearest estimate up to {CARRY} years away (dotted, can be switched off), otherwise hatched. Overtakes are judged only on years where both countries have their own estimate.
- Before 1820: world series from De Long (1998), HYDE 3.2.1 and McEvedy and Jones (1978), and Maddison's (2010) regions, all as transcribed by Roodman (2020); 1990-dollar series rescaled by one factor ({LR['link']}) to meet the 2023 database in 1820. Greenland, in Maddison's Western Europe, is not drawn.
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
- IMF World Economic Outlook database, October 2025 (growth rates for {LAST_MPD + 1} to {L} only).
- De Long, J. B. (1998), Estimates of world GDP, one million B.C. to present; Klein Goldewijk, K. et al. (2017), HYDE 3.2, Earth System Science Data 9; McEvedy, C. and Jones, R. (1978), Atlas of World Population History; Maddison, A. (2010), Historical Statistics of the World Economy 1 to 2008 AD; all as compiled by Roodman, D. (2020), "Modeling the Human Trajectory" (https://github.com/droodman/Modeling-Human-Trajectory). Only the published figures are used and credited.
- historical-basemaps, Andre Ourednik and contributors (https://github.com/aourednik/historical-basemaps), GPL-3.0; the simplified copies in `data/hist/` keep that licence.
- Natural Earth (public domain). Leaflet (BSD-2). Optional base maps on the page: Esri.

Code: MIT. Text, figures and derived data: CC BY 4.0. `data/hist/`: GPL-3.0.

## Citation

Hotham, T. (2026) The Wealth of Nations, Mapped: national output, output per head and shares of the world economy on an interactive map, with world estimates from 10,000 BC. Zenodo. {{https://doi.org/10.5281/zenodo.23899403}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
lic = """MIT License (code)

Copyright (c) 2026 Tristan Hotham

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Text, figures and derived data: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/.
The derived data build on the Maddison Project Database 2023 (Bolt and van Zanden, CC BY 4.0); please credit it as well.
data/hist/ contains simplified copies of historical-basemaps (Andre Ourednik and contributors) and is licensed under the GNU General Public License v3.0 (see data/hist/LICENSE_GPL-3.0.txt).
"""
post = f"""## Title

[OC] China and India made {ci['1820']:.0f}% of the world's output in 1820, {ci['1950']:.0f}% in 1950 and {ci[str(L)]:.0f}% in {L}: two centuries of the world economy on one map

## Body

I put the Maddison Project Database (the long-run GDP estimates that Angus Maddison started) on an interactive map with a slider, and pushed it back as far as the evidence honestly goes. The maps show each country's share of world output on today's borders. In 1820 China and India were the two biggest economies because of their populations, not their wealth (China about ${R['pc1820']['CHN']:,.0f} a head against Britain's ${G['1820']['richest_pc']:,.0f}). Their combined share fell to {ci['1973']:.0f}% by 1973 while Western Europe and its offshoots peaked at {ws['1913']:.0f}% in 1913; today the two blocs are level at about {ci[str(L)]:.0f}% each. The US economy passed Britain's in {O['usa_gbr_gdp']['first']}; China passed the US again (in purchasing power terms) in {O['chn_usa_gdp']['first']}. South Korea's GDP per head is {T['kor']['x_60_last']:.0f} times its 1960 level. The interactive version starts in 10,000 BC with world-only estimates (HYDE population, DeLong's output per head) and shows Maddison's older regional guesses from AD 1 striped. Caveats: before 1820 most of the map has no estimate at all (hatched), and before AD 1 the numbers are largely assumption; values are for present-day territories in 2011 PPP dollars; {LAST_MPD + 1} to {L} are carried forward with IMF growth. Interactive map: https://maps.tristanhotham.com/gdp-through-time/

## Source comment

Sources: Maddison Project Database 2023 (Bolt and van Zanden 2024, CC BY 4.0), GDP per head and population in 2011 international dollars; IMF World Economic Outlook (October 2025) growth for {LAST_MPD + 1} to {L}; De Long (1998), HYDE 3.2.1, McEvedy and Jones (1978) and Maddison (2010) via Roodman (2020) for the very long run; Natural Earth borders.

Tools: Python (pandas, geopandas, matplotlib); Leaflet for the interactive map.

Interactive version: https://maps.tristanhotham.com/gdp-through-time/
Paper: {{https://doi.org/10.5281/zenodo.23899403}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/gdp-through-time/}}
"""
assert ci[str(L)] - 2 < ws[str(L)] < ci[str(L)] + 2       # "level at about 30% each"
for t in (readme, lic, post):
    for bad in ("—", "–", "--", "DSIT", "DCMS"):
        assert bad not in t.replace("|---|---|", ""), bad
open(os.path.join(ROOT, "README.md"), "w", encoding="utf-8").write(readme)
open(os.path.join(ROOT, "LICENSE"), "w", encoding="utf-8").write(lic)
open(os.path.join(ROOT, "reddit", "post.md"), "w", encoding="utf-8").write(post)
print("README", len(readme.split()), "words; post", len(post.split()), "words")
