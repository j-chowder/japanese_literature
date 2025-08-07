### Data Collection

- `literary` data was obtained from [Aozora Bunko](https://www.aozora.gr.jp/). Missing features, like inception year and the actual text, were obtained with `Beautiful Soup`.
     - `id` - primary key
     - `title` - title of the work
     - `inception` - year that the work was originally written
     - `author_id` -  foreign key to the `author_id` in the `author` table.
     - `author_age` - age of the author during the inception of the work
     - `book_category`  - the [Nippon Decimal Classification](https://en.wikipedia.org/wiki/Nippon_Decimal_Classification)
     - `char_type`  -
     - `char_count` - the character count of the work
     - `length_type` - bin based off of `char_count`
         - `flash` -
         - `shortshort` - 
         - `short`- 
         - `novelette` - 
         - `novel` -
    - `text` - the webscraped text of the work.
- `author` data was obtained from Aozora Bunko, [Wikipedia](https://www.wikipedia.org/), and [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page).
    - `author_id` - primary key
    - `name` - name of the author
    - `gender` - gender of the author
        - `unknown` if no sufficient evidence exists. (anonymous, pen name, etc.)
        - `N/A` if the author is a group (e.g. ministries)
    - `birthplace`  - birthplace of the author, standardized to prefecture (or country, if outside Japan)
    - `birth_date` - date of birth of the author
    - `death_date` - date of death of the author
    - `first_work_age` - the age of the author at the inception of their first work
- `education` data was obtained from 
- `vital` data was obtained from
- `birth expectancy` data was obtained from
- `urbanization` data was obtained from
- `gdp` data. All values are in U.S. dollars adjusted for inflation to the year 2011
    - `year` - year
    - `max` - the highest GDPpc global
    - `jp` - Japan's GDPpc
    - `percentage` - `jp` / `max` * 100
- `WPI` [(Wholesale Price Index](https://en.wikipedia.org/wiki/Wholesale_price_index)) data is based on year 1945 = 100.
    - `year` - year
    - `WPI` - WPI
    
### Acknowledgements

- Ministry of Health, Labour and Welfare. (n.d.). Vital Statistics of Japan. Portal Site of Official Statistics of Japan (e‑Stat). Retrieved August 6th, 2025, from https://www.e-stat.go.jp/en/stat-search/files?page=1&toukei=00450011&tstat=000001028897
- EDU20C Project. (n.d.). Japan educational attainment dataset (v1.1) EDU20C. Retrieved August 6, 2025, from https://edu20c.org/japan/
- IER Hitotsubashi University. (n.d.). Historical statistics of Japan: Urbanization rates (1920–1960). Hitotsubashi University Research Repository. https://d-repo.ier.hit-u.ac.jp/records/2000597
- Index Mundi. (n.d.). Japan - Urban population (% of total population). https://www.indexmundi.com/facts/japan/indicator/SP.URB.TOTL.IN.ZS
- Bank of Japan. (n.d.). Historical statistics and price indexes. Retrieved August 6, 2025, from https://www.stat-search.boj.or.jp/index_en.html
  
  
