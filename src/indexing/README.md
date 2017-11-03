## How to create an index

First, be sure to install all Python requirements from `requirements.txt` in project root.

Then, run this command to populate data in `data/json` folder:  
`python3 data_extractor.py`

Now you can build the index (will be stored in `data/index`) with:  
`python3 index_builder.py`

To test sanity of constructed index, we propose a manual testing routine, 
where you can insert words and get list of documents where this word occurs:  
`python3 index_reader.py`
