# peace-machine

# Setting up the Pipeline

## Install the required packages
1. Install peace-machine from github: ```pip install -U git+https://github.com/ssdorsey/peace-machine.git```

## Setup the Mongo Database

1. Download + Install [MongoDB Server](https://www.mongodb.com/download-center/community)
1. (Optional) Set local database base in mongod.conf file
1. In Command Prompt / Terminal, start server with ```mongod```
    * If you want to start the server on a specific drive (ex: D:/): ```mongod --dbpath D:/``` OR:
        * Make sure you're starting the database in a path with the following folders /data/db/ 
        * Change your directory: ```cd D:```
        * Launch the server: ```mongod```
1. Create database and collection:
    * In a new Terminal, enter the mongo shell: ```mongo```
    * Create the database (this one named "ml4p"): ```use ml4p```
    * Create a new collection (this one named "articles"): ```db.createCollection('articles')```
    * Create an index for the collection on the "url" field: ```db.articles.createIndex({'url':1}, {unique: true})```
        * This is so duplicate url's aren't inserted and we can do quick searches on the url
1. Set up [access control](https://docs.mongodb.com/manual/tutorial/enable-authentication/)
1. Create known actors collection
1. Create locations collection
    * Download/unzip GADM in GeoPackage format: https://gadm.org/download_world.html
    * Install gadl: ```conda install -c conda-forge gdal```

## Setup ElasticSearch wikipedia
1. Install [ElasticSearch](https://linuxize.com/post/how-to-install-elasticsearch-on-ubuntu-18-04/)
1. Download wikipedia content and index
    * Go to a recent page on [here](https://dumps.wikimedia.org/other/cirrussearch/)
    * Download something that looks like "enwiki-20200427-cirrussearch-content.json.gz" (numbers will be different)
1. [Import into ElasticSearch](https://stackoverflow.com/questions/33630222/indexing-wikipedia-dump-to-elasticsearch-gets-xml-document-structures-must-start)
    * Fetch the current mapping: ```curl https://en.wikipedia.org/w/api.php?action=cirrus-mapping-dump&format=json > mapping.json```
    * Feed that mapping into elasticsearch: ```jq .content < mapping.json | curl -XPUT localhost:9200/enwiki_content --data @-```
    * Load the dump: ```zcat enwiki-20200427-cirrussearch-general.json.gz | parallel --pipe -L 2 -N 2000 -j3 'curl -s http://localhost:9200/enwiki_content/_bulk --data-binary @- > /dev/null'```


## Run the Scrapers

### Site-direct scrapers

1. Set up MongoDB
1. Open new Command Prompt / Terminal
1. Change directory: ```cd ~/peace-machine/news-please-mongo/newsplease/```
1. Do initial launch / set the directory: ```python __main__.py -c DIRECTORY_FOR_STORING_LOGS```
1. After 5 seconds or so, cancel the inital run with ```CTRL/CMD + C```
1. Edit the config.cfg and sitelist.hjson files in the directory you set during the launch as necessary
    * If the MongoDB is using access control, edit the "uri" line under the [MongoDB] section
    * [Info on MongoDB URI](https://docs.mongodb.com/manual/reference/connection-string/)
1. Re-launch the scrapers with: ```python __main__.py -c DIRECTORY_FOR_STORING_LOGS```
    * For all future launches use: ```python __main__.py -c DIRECTORY_FOR_STORING_LOGS --resume``` 

### CC-News scrapers
1. Set up MongoDB
1. Do initial setup on the Site-direct scrapers
1. Check/edit the sitelist ~/DIRECTORY_FOR_STORING_LOGS/config/sitelist.hjson
1. Execute the CC-News parser: ```python commoncrawl.py```
    * This will track the .warc files you have already downloaded/parsed. If you add a new domain (and thus need to rerun the files), set ```my_continue_process = False``` in commoncrawl.py
1. Rerun commoncrawl.py whenever you want to collect new data


## Run the Event Extraction
1. Set up MongoDB
1. Get some stories in the MongoDB
1. Open a new Terminal
1. Change directory: ```cd ~/peace-machine/peacemachine/```
1. Run the extractor: ```python event_extractor.py```


## Automate
1. [Linux](https://www.howtogeek.com/101288/how-to-schedule-tasks-on-linux-an-introduction-to-crontab-files/)


# Training Process

## Event coder
1. Get training data
1. Run train_event_classifier.py

## Custom spaCy NER model
1. Get [Phoenix agents, actors, etc ](https://github.com/openeventdata/Dictionaries)
1. Run convert_phoenix.py
1. Use the resulting model wherever you want NER

## Translation 
1. Install OpenNMT-py
1. Run opennmt-py_preprocess.py
1. Run opennmt-py_transformers_preprocess.sh
1. Run opennmt-py_transformers_train.sh (probably should be done on the cloud. need ~16gb VRAM, 8GPU helps with speed)
