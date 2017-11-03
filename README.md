# FindMyShoes

This is SPb AU Information Retrieval course project. We aim to build a search system that can retrieve highly-relevant e-shop pages. In particular, we focus on shoes in russian e-market.  

There are several caveats when choosing the right shoe model for your feet. Here are several parameters to be aware of (some of them in Russian, because I don't know how to put them in English):
 - size (stated size can be different from "real feelings", there is even a word in Russian for it - "маломерка");
 - подкладка;
 - стелька;
 - высота каблука.
 
Our information retrieval system will reduce time needed to find the right offer.

## Project structure
`src` folder contains source code factored by purpose:
 - `crawler` subfolder contains our crawling scripts. We traverse the Web in breadth-first search manner, starting from some "seed" pages (usually, main pages of e-shops). This gives us data to search from;
 - `indexing` subfolder contains scripts for building an *index*. Index exists for the purpose of performing search queries efficently. In particular, we implement *inverted index*: for each word that occurs in overall dataset, we write a list of documents where this word appears;
 
`data` folder contains data that we search from, in different forms:
 - `raw`: raw HTML-pages and metainformation gathered by our *crawler*. You can check sample data in our repository;
 - `json`: "interesting" information extracted from raw data, like shoe sizes and names. Has loose schema;
 - `index`: search-ready inverted index in binary form.
 
You can obtain `json` and `index` data by using scripts in `indexing` folder.



## Authors
[Mike Koltsov](https://github.com/ItsLastDay)  
[Andrey Kravtsun](https://github.com/kravtsun)
