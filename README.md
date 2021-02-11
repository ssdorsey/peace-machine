# peace-machine

## Setting up the PC (Instructions below assume Ubuntu 18)
1. Install [Anaconda distribution of python 3.8](https://www.anaconda.com/products/individual)
2. Install [awscli](https://linuxhint.com/install_aws_cli_ubuntu/)
3. Install [gcc](https://linuxize.com/post/how-to-install-gcc-compiler-on-ubuntu-18-04/)
4. Install [ruby](https://www.ruby-lang.org/en/documentation/installation/#apt)
5. Install wayback-machine-downloader: ```gem install wayback_machine_downloader```
6. Install NVIDIA GPU drivers(depending on the machine)

## Setting up the Pipeline

### Install the required packages
1. Install peace-machine from github: ```pip install -U git+https://github.com/ssdorsey/peace-machine.git```

### Setup the Mongo Database

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
1. Set up [firewall permissions](https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-18-04)
1. Create known actors collection
1. Set up actors system \[Akanksha\]

## Setup ElasticSearch wikipedia
1. Install [ElasticSearch](https://linuxize.com/post/how-to-install-elasticsearch-on-ubuntu-18-04/)
1. Import [Wikipedia](http://fuzihao.org/blog/2018/01/01/Struggling-in-importing-wikipedia-into-Elasticsearch/)
    * wiki_to_elastic.py
1. Attach whatever [pageview stats](https://dumps.wikipedia.org/other/pageviews/) you want.
    * download_wikimedia_pageviews.py
    * attach_wikipedia_pageviews.py


## Run the Scrapers

### Site-direct scrapers

1. Set up MongoDB (see above)
2. Install the fork of news-please with Mongo integration: ```pip install -U git+https://github.com/ssdorsey/news-please.git```
3. Follow the news-please documentation for initial run / config 
6. Edit the config.cfg and sitelist.hjson created in the above step:
    * sitelist.hjson can be configured automatically using the ```create_sitelist``` function in scrape_direct.py
    * Set the [MongoDB URI](https://docs.mongodb.com/manual/reference/connection-string/)
    * Ensure MongoStorage is in the pipeline at the bottom of the config.cfg file
7. Re-launch the scrapers with: ```news-please -c [CONFIG_LOCATION]```
    * Include -resume flag if the code has been run previously

### CC-News scrapers
1. Set up MongoDB (see above)
2. Check/edit the sitelist ~/DIRECTORY_FOR_STORING_LOGS/config/sitelist.hjson
3. Edit the directory and settings in the scrape_ccnews.py file inside of peace-machine
4. Execute the CC-News parser: ```python scrape_ccnews.py```
    * This will track the .warc files you have already downloaded/parsed. If you add a new domain (and thus need to rerun the files), set ```my_continue_process = False``` in commoncrawl.py
5. Rerun commoncrawl.py whenever you want to collect new data

## Run De-Deuplication and Patch Script
1. Open terminal and got to peace-machine/peacemachine/scripts
2. Run the patch file: ``` python3 patch_tools.py``` <br>
Note: Make sure you run this script before running the locatrion, translation and event extractor pipeline

## Run translation
1. Open a new terminal
2. Run: ```peace-machine -t [ISO2 LANGUAGE CODE]```
    * Ex: ```peace-machine -t es```
    * Other options (such as batch sizing) are available using ```peace-machine --help```
    * Iso2 language code must be in the languages collection of the DB

## Run the Event Extraction
1. Open a new terminal
2. Run the extractor: ```peace-machine -u [MongoDB URI] -e [MODEL NAME] -b [BATCH SIZE] -ml [LOCATION OF MODEL ON DRIVE]```
    * EX: ```peace-machine -u mongodb://username:password@192.168.176.240 -e civic1 -b 768 -ml "/mnt/d/peace-machine/peacemachine/data/finetuned-transformers"```


## Automate
1. [Linux](https://www.howtogeek.com/101288/how-to-schedule-tasks-on-linux-an-introduction-to-crontab-files/)

