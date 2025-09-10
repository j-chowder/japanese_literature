# Text Classification of Japanese Literature

### Goal:
Complete an end-to-end data science project to answer the question: <br>

<div align="center"><h3>How can I shape 20th century Japanese literature into a text classification task?</h3></div>
<br>

**Subgoals**
1. **Collect all my data** without the use of easily accessible datasets (e.g. Kaggle)
2. Rather than just using predefined classes, like genres, **utilize text classification technology** to classify each work into various defined topics.
3. **Build and train classification models** that can accurately classify a work to a topic without the text. Instead, using metadata (author age and gender, character types and count, etc.) and contextual data (education rates).
4. Use SHAP values to gain **insights on what features are most significant** in determining topic assignment
5. **Investigate misclassifications** to be able to understand what features caused it.


### Data Collection

- `literary` data was obtained from [Aozora Bunko](https://www.aozora.gr.jp/). Missing features, like inception year and the actual text, were obtained with `Beautiful Soup`.
     - `id` - primary key
     - `title` - title of the work
     - `inception` - year that the work was originally written
     - `author_id` -  foreign key to the `author_id` in the `author` table.
     - `author_age` - age of the author during the inception of the work
     - `book_category`  - the [Nippon Decimal Classification](https://en.wikipedia.org/wiki/Nippon_Decimal_Classification)
     - `char_type`  - character types (e.g. [shinjitai](https://en.wikipedia.org/wiki/Shinjitai))
     - `char_count` - the character count of the work
     - `length_type` - bin based off of `char_count`
         - `flash` - $[1,1000]$
         - `shortshort` - $(1000, 3000]$ 
         - `short`- $(3000, 6000]$
         - `novelette` - $(6000, 14000]$
         - `novel` - $(14000, \infty)$
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
- `education` data was obtained from [Japan educational attainment dataset](#acknowledgements)
- `vital` data was obtained from [Vital Statistics of Japan](#acknowledgements)
- `urbanization` data was obtained from [Japan - Urban Population (% of total population)](#acknowledgements)
- `gdp` data. All values are in U.S. dollars adjusted for inflation to the year 2011
    - `year` - year
    - `max` - the highest GDPpc global
    - `jp` - Japan's GDPpc
    - `percentage` - `jp` / `max` * 100
- `WPI` [(Wholesale Price Index](https://en.wikipedia.org/wiki/Wholesale_price_index)) data is based on year 1945 = 100.
    - `year` - year
    - `WPI` - WPI

### Topic Modeling
> See `topic_modeling.ipynb` for the source code

>[!NOTE]
>Throughout, it was necessary for me to do things in a roundabout way or suboptimally as I prioritized memory management. BERTopic is very expensive :(. Whether it was embedding in batches, or saving each step to disk, note that this is _not required_, but was personally necessary.

#### Preprocessing

- Removed all punctuation
- Standardized all japanese characters (see 全角 vs 半角)
- Removed outliers in terms of character count (defined as Q3 + 1.5 * IQR)
- Removed all english from the text (often just gibberish or romaji)
- Removed all entries without a recorded inception date.

This resulted in 17370 entries --> 9742 entries.

#### Embedding
> Embedding is needed for algorithms to be able to work with text. Text embeddings convert text into numerical data that machines and models can understand.

As the documents were very large (and since BERTopic is intended for sentence level documents), I realized that I had to chunk each document into several tokens then feed that into BERTopic, else I lose a lot of semantic details as BERTopic just truncates anything past the max token count.

- Chunk the documents into individual chunks that each fit inside the tokenization limit
- Map those "mini documents" to the larger document to reference later, but proceed with the rest of the BERTopic process using those mini documents.

> My chunk embeddings can be found in the `./saved_steps/chunk_embeddings.dat` file.

#### Dimension Reduction
> Embeddings are very high dimensional (in this case, 111208 x 384). Dimension reduction denoises this data, and makes it infinitely easier for clustering algorithms to work effectively.

For UMAP, I didn't have enough memory to fit it on all of my embeddings. So, I 
1. performed stratified sampling
2. fit UMAP on that representative sample
3. transformed the rest of the data.

> Stratified sampling ensured my subset includes a proportional representation of the actual population

#### Clustering

Why HDBSCAN?
- Clusters are defined as dense areas in the data space, not by global shape assumptions.
- Can discover both large clusters and small clusters simultaneously
- Outlier documents become noise instead of being forced into a dissimilar cluster.
- Synergises well with UMAP.

#### Tokenization
> extracting topics from the clusters defined in HDBSCAN

This is the step that actually makes the topics interpretable to us.

I used [fugashi](https://github.com/polm/fugashi) as the tokenizer, which is specifically made for japanese text.

#### Representations

I used [ginza](https://github.com/megagonlabs/ginza) for the PartOfSpeech model.

#### Hyperparameter Tuning

Metrics:
- $c_v$ coherence value
    - global (mean)
    - spread and distribution of the individual topic $c_v$ values.
- word diversity
- number of topics
- distribution of documents per topic (are most docs just clustered in one singular large topic?)
- outlier rate (% of documents are treated as outliers (-1))

I tuned these parameters:
- UMAP `n_neighbors`
- HDBSCAN `min_samples`
- HDBSCAN `min_cluster_size`

I was able to increase $c_v$, without sacrificing the other metrics too much, from `0.13` --> `0.38`
<img width="586" height="433" alt="image" src="https://github.com/user-attachments/assets/ceb579ba-db37-40ac-965f-eed4a70a196f" />

> While $c_v$ could go higher below 9 topics, it sacrificed too much of the other metrics (outlier rate, distribution of documents per topic)

 #### Assigning original documents to topics
> Recall that due to the large size of the original documents, I had chunked them into smaller documents for the purpose of BERTopic.

1. locate topic centroids
2. compute euclidian distance of each document from each centroid
3. calculate the probabilities using softmax adjusted with a cool temperature to distinguish outputs further apart.
4. averaged all chunks of a work to get the aggregated probabilities for each topic for each work
5. hard classified each work to the topic with the highest probability.

<img width="698" height="547" alt="image" src="https://github.com/user-attachments/assets/c931281d-f93d-429c-82ad-badb15b77239" />

#### So what are the topics?

| Topic Number | Keywords | Interpretation |
|:---|:---|:---|
| -1 | 修養 (self-improvement) 描く (to draw) 繪 (drawing/painting) 學生 (student) 部 ((school) club) 希望 (hope, aspiration) 欲望 (desire)   | Youth Aspirations |
| 0 | 藝術 (the arts) 外見 (appearance) 面 (face, surface) 裝 & 服 (clothing) 音 (sound) 物 (stuff) 事 (things) | Aesthetics and Appearance |
| 1 | 革新 (innovation) 専門 (specialization) 獨逸 (Germany) 立派 (splendid, praiseworthy) 識者 (intellectual) 目的 (goal) | Westernization of Japan |
| 2 | 雅 ([Miyabi](https://en.wikipedia.org/wiki/Miyabi)) 魂 (soul) 亡くなる (to pass away) 危篤 (verge of death) 息 (breathing) 枕許曲 (bedside) 失 (loss) 海 (sea) | Death |     
| 3 | 技能 (technical skill) 力強く (strong) 武士 (samurai) 死 (death) 清く (noble, pure) 稽古 (training) 美しい (beautiful) 人格 (character/personality)  | Self Cultivation |
| 4 | 世間 (society) 階級 (class) 高い/低い (high/low (class)) 意見 (opinion) 相違 (differences) 危險 (danger, risk) | Social Hierarchy  |
| 5 | 文學 (literature) 美術 (fine arts) 生活 (daily life) 一群 & 連中 (group (of people)) 己れ (oneself) 歩 (progress) | Cultural Life |
| 6 | 研究 (research) 感服 (admiration) 先生 (teacher, honorific) 坪内 ([Tsubouchi](https://en.wikipedia.org/wiki/Tsubouchi_Sh%C5%8Dy%C5%8D))  | Scholarly Appreciation |
| 7 | 他人 (other people) 作り上げ (forced (personality, smile, etc.)) 芝居 (acting) 媚びる (to flirt) 態度 (attitude) 眞 (truth, authenticity) 酒 (alcohol)  | Social Behavior and Authenticty |

### EDA
> Refer to my source code --> `eda.ipynb`. This section is just going to be highlights or insights that I felt was interesting to discover.

#### Authors
<img width="570" height="432" alt="image" src="https://github.com/user-attachments/assets/a716567a-7e67-4043-a29f-3032e4e9721a" />

- `female` works are mostly of topics 1, 0, and 2.
- least common `female` works are of topics 3, 6, and 7.

<img width="573" height="432" alt="image" src="https://github.com/user-attachments/assets/afee114f-c07c-4ec8-ac4a-ceda3c7e63df" />

- `female` works are delayed, until 1940s before they are similar to `male` works in terms of frequency.
- `female` works are much more prominent compared to `male` works in the 1980s, but a small sample size could definitely be attributing to that.

- both genders' works follow similar trends (clustered around 1900 - 1950, massive dip during WWII, normal-ish distribution)

<img width="580" height="455" alt="image" src="https://github.com/user-attachments/assets/ab5afb3a-b2eb-40e2-8ba0-e5956a0302bc" />

Interesting that there are so many works in the Showa period relative to authors.
- `Meiji` - 1.26 works / author
- `Taisho` - 3.03 works / author
- `Showa` - 9.48 works / author

<img align="left" width="48%" alt="image" src="https://github.com/user-attachments/assets/49f4f29e-7534-4a52-80b8-34563bf0eb66" /> 
<img align="right" width="48%" alt="image" src="https://github.com/user-attachments/assets/5d89b30d-8ab6-413a-9374-24900ccdd416" />

- Topic 2 and Topic 5 have considerably younger authors compared to the rest.

#### Works Metadata

<img width="574" height="452" alt="image" src="https://github.com/user-attachments/assets/e2ac1df5-9c0d-4e1b-81f3-a65dc250849b" />

- Topic -1 is predominantly `新字新仮名`
- Topic 0 is predominantly `新字新仮名`, with some `旧字旧仮名` -- it is the largest proportion of topic in a character type.
- Topic 1 is predominantly `新字新仮名` and `新字旧仮名`
- Topic 2 is mostly `新字旧仮名`, with a considerable amount of `旧字旧仮名`
- Topic 3 is pretty balanced
- Topic 4 is almost all `新字新仮名`
- Topic 5 is mostly `新字新仮名` and `新字旧仮名`
- Topic 6 is almost all `新字新仮名`
- Topic 7 is mostly `新字新仮名` and `新字旧仮名`

<img width="584" height="432" alt="image" src="https://github.com/user-attachments/assets/74c779bf-0f54-40c6-b13a-0aad97c29199" />

- Each book type shares similar trends
   - Drastic increase starting early 1900s, especially after WWI.
   - dip during WWII, with an upsurge following the beginning of U.S. occupation.
   - A very unnatural near-zero count of works during the 1970s.
   - A slight resurge of works during the 1980s.
- `short`s were most prominent between 1920s and 1930, after which it drops the most drastically during WWII, leading to other works becoming more prominent.
- `novelette`s and `novel`s were most prominent between 1935 - 1950, which would align with the Great Depression and WWII. `novelette`'s dip during WWII is much less drastic than the others.
- `shortshort` and `flash`'s distribution seem to be similar to one another, with `shortshort` being clustered around 1930 - 1940.

#### Contextual Data

<img width="799" height="677" alt="image" src="https://github.com/user-attachments/assets/7ea0623f-4c34-44cc-8c02-5c6baf65869f" />

- Topic 3 generally has the highest no education rates.
- Topic 1 generally has the lowest no education rates, followed by Topic -1 and 0, all of which are mostly 新字新仮名 (most modern character type).

### Model Building
> [Optuna](https://github.com/optuna/optuna) was used to facilitate hyperparameter tuning.



### Feature Importance
- all values are the corresponding mean(|SHAP value|)

<img width="790" height="700" alt="image" src="https://github.com/user-attachments/assets/387657d5-8342-4d91-b3bf-f855a6a98b23" />


| Topic Number | 1st SHAP | 2nd SHAP | 3rd SHAP | 4th SHAP | 5th SHAP |
|:---|:--:|:--:|:--:|:--:|:--:|
| -1 | `length_type_flash` = 0.61 | `char_type_新字新仮名` = 0.32 | `length_type_novelette` = 0.29 | `authorAge` = 0.25 | `no_education` = 0.19 |
| 0 | `first_work_age` = 0.54 | `char_type_新字新仮名` = 0.45 | `length_type_flash` = 0.34 | `char_type_旧字旧仮名` = 0.18 | `authorAge` = 0.17 |
| 1 | `first_work_age` = 0.48 | `authorAge` = 0.26 | `no_education` = 0.2 | `gender_female` = 0.14 | `length_type_shortshort` = 0.14 |
| 2 | `char_type_新字新仮名` = 0.81 | `authorAge` = 0.43 | `first_work_age` = 0.42 | `length_type_flash` = 0.16 | `char_type_旧字旧仮名` = 0.15 |
| 3 | `authorAge` = 0.59 | `first_work_age` = 0.46 | `no_education` = 0.42 | `char_type_新字新仮名` = 0.29 | `post_secondary` = 0.16 |
| 4 | `char_type_新字新仮名` = 0.49 | `first_work_age` = 0.41 | `authorAge` = 0.28 | `char_type_新字旧仮名` = 0.22 | `no_education` = 0.21 |
| 5 | `length_type_flash` = 1.70 | `length_type_shortshort` = 0.44 | `length_type_short` = 0.29 | `length_type_novelette` = 0.28 | `authorAge` = 0.14 |
| 6 | `authorAge` = 0.31 | `first_work_age` = 0.31 | `char_type_新字新仮名` = 0.24 | `no_education` = 0.24 | `length_type_novelette` = 0.17 | 
| 7 | `first_work_age` = 0.38 | `authorAge` = 0.35 | `char_type_新字新仮名` = 0.28 | `no_education` = 0.24 | `length_type_flash` = 0.17 | 

#### Topic -1

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/2a1d660b-8297-44b0-9147-4579e2a2b3ee" />

- Shorter works
    - novelettes and novels have a negative SHAP value (lowers the probability of being topic -1).
    - flash and shortshort have a positive SHAP value.
- More modern
     - modern character types (新字新仮名) --> positive SHAP
     - lower lack of education rates --> positive SHAP
- Older Authors
    - higher values of author ages --> positive SHAP
    - higher values of author's age at first work --> positive SHAP

#### Topic 0

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/f06761e9-c8fd-48c0-a1ab-164504433835" />

- Author Age
   - Generally higher values of author's age at first work --> positive SHAP

- Longer, newer works
   - flash --> negative
   - novel and novelette --> positive
   - modern character types (新字新仮名) --> positive
   - older character types (旧字旧仮名, 新字旧仮名) --> negative
 
#### Topic 1

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/66c26345-ee26-407a-9406-8d7eb5a05150" />

- All ages
  - high and low values for age at first work exist on both sides of the baseline
  - same for author age, with lower ages generally greater negatives than positives.

- Gender
  - female --> positive

- Shorter, semi-old works
  - shortshort --> positive
  - novels and novelettes --> negative
  - New kanji but old kana (新字旧仮名) --> positive
  
#### Topic 2

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/6c13b1f3-cd73-4d92-8ce6-6b562f774c86" />

- Older books
   - most modern character type (新字新仮名) --> negative
   - oldest character type (旧字旧仮名) --> positive
   - flash --> negative
   - shortshort --> negative

- Younger, female authors
  - generally younger author --> positive
  - generally lower values for age at first work --> positive
  - female --> positive
 
#### Topic 3

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/bd0fa3cd-a8dc-4a43-b5e1-3544fb44583a" />

- Older books
   - most modern character type (新字新仮名) --> negative
   - oldest character type (旧字旧仮名) --> positive
   - flash --> negative

- Old, male authors
    - high author age --> positive
    - high rates of no education --> positive
    - higher rates of post secondary education --> negative
    - male --> positive
    - female --> negative

#### Topic 4

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/5a913a52-5d84-4cec-821c-094383cf4ede" />

- New and relatively short works
    - most modern character type (新字新仮名) --> positive
    - second most modern character type (新字旧仮名) --> negative
    - old character type (旧字旧仮名) --> negative
    - flash --> negative
    - short --> positive
 
#### Topic 5

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/2284a00d-9bb2-4874-b745-41c0783de054" />

- Very short works
  - flash --> positive
  - shortshort --> positive
  - short --> negative
  - novelette -> negative
  - novel -> negative

- Younger female authors
   - lower values for author age --> positive
   - lower values for age at time of first work --> positive
   - female --> positive

#### Topic 6

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/94560182-baa0-4b33-b128-631a35841a40" />

 - Old, male authors
 - modern character type
 - shorter works

#### Topic 7

<img width="835" height="496" alt="image" src="https://github.com/user-attachments/assets/16814c6a-9890-4102-8c8f-5d2a19741a95" />

- high author age
- high rates of no education
- shorter works --> flash and shortshorts
- older character type (新字旧仮名)
   
---
### Investigating misclassifications

<figure>
<img align="left" width="40%" src="https://github.com/user-attachments/assets/5020a721-0900-4868-9df4-d2415f80803b" />
<img align="right" width="40%" src="https://github.com/user-attachments/assets/7cb92a8a-1083-4ec6-9e31-dcbadf2650b3" />
<figcaption> 
     <em>Both plots are of the same misclassified observations (predicted Topic 2, real Topic 1).  
     Left: Topic 2 as the baseline (wrong). Right: Topic 1 as the baseline (right).</em> </figcaption>
</figure>

<div></div><br>

1. Younger authors significantly contribute to the algorithm misclassifying documents as Topic 2.
2. The works not being the 新字新仮名 character type and some being the 旧字旧仮名 character type significantly contributes to the algorithm misclassifying documents as Topic 2 (older works).
3. The works not being flash, not being shortshort, being novelettes, and being novels correlate more with Topic 2 (longer books).
    
---

### Acknowledgements

- Ministry of Health, Labour and Welfare. (n.d.). Vital Statistics of Japan. Portal Site of Official Statistics of Japan (e‑Stat). Retrieved August 6th, 2025, from https://www.e-stat.go.jp/en/stat-search/files?page=1&toukei=00450011&tstat=000001028897
- EDU20C Project. (n.d.). Japan educational attainment dataset (v1.1) EDU20C. Retrieved August 6, 2025, from https://edu20c.org/japan/
- IER Hitotsubashi University. (n.d.). Historical statistics of Japan: Urbanization rates (1920–1960). Hitotsubashi University Research Repository. https://d-repo.ier.hit-u.ac.jp/records/2000597
- Index Mundi. (n.d.). Japan - Urban population (% of total population). https://www.indexmundi.com/facts/japan/indicator/SP.URB.TOTL.IN.ZS
- Bank of Japan. (n.d.). Historical statistics and price indexes. Retrieved August 6, 2025, from https://www.stat-search.boj.or.jp/index_en.html
  
  
