# Daily yojijukugo to use in conversations
- Extract yoji from 4jword file
- Distribute yoji over days
- Add some usage info (suru-verbs, na-adjectives, etc.)
- Add English translations from Tatoeba.org
- Add link to yoji-jukugo.com if exists
- Add link to wikipedia if exists, get list from https://dumps.wikimedia.org/jawiki/latest/jawiki-latest-all-titles-in-ns0.gz
- ~~Scrape set of buddhist yoji from Jisho.org~~
- Create API
- Create webfrontend (and others through Apache Cordova?)
- Add license information
- Add solar term?

## Relevant licenses
- ~~https://www.edrdg.org/edrdg/licence.html which is the source of Jisho~~
- CC BY 2.0 FR for Tatoeba sentences
- Kanji Haitani for the 4jword3 file
  Four-Character Idiomatic Compounds         Yojijukugo   2005   v.3.11   
  英訳四字熟語辞典    第３版    (2005年）
  Copyright  2005  Kanji Haitani
- Cite wikipedia for solar term translations https://en.wikipedia.org/wiki/Solar_term#Multilingual_list

## Improvements
- [ ] Add deepdive option with info on the four kanji
- [ ] Add LLM explanations?
- [ ] Switch to using httpx module instead of requests (for async requests)
- [ ] Update example sentences through users (they make the Tatoeba API request and send results back to db)
- [ ] Add voting on example sentences to make ranking for usefulness



