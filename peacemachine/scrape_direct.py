# import packages
import json
from pymongo import MongoClient

from peacemachine.helpers import regex_from_list
# create the config file


# create the sitelist file
def create_sitelist(uri, config_location):
    """
    creates the sitelist.hjson for scraping
    :param url: the url 
    """
    # connect to the db
    db = MongoClient(uri).ml4p
    # create a holding list
    site_list = []
    # pull all the data from the db
    for source in db.sources.find():
        if source.get('blacklist_url_patterns'):
            black_regex = regex_from_list(source.get('blacklist_url_patterns'), compile=False)
            s_dict_rec = {
                'url': source.get('full_domain'),
                'crawler': 'RecursiveSitemapCrawler',
                'ignore_regex': black_regex
            }
            s_dict_rss = {
                'url': source.get('full_domain'),
                'crawler': 'RssCrawler',
                'ignore_regex': black_regex
            }
        else: 
            s_dict_rec = {
                'url': source.get('full_domain'),
                'crawler': 'RecursiveSitemapCrawler',
            }
            s_dict_rss = {
                'url': source.get('full_domain'),
                'crawler': 'RssCrawler'
            }
        
        # append
        site_list.append(s_dict_rec)
        site_list.append(s_dict_rss)

    # create the final form
    main_dict = {'base_urls': site_list}

    # write the file
    if not config_location.endswith('/'):
        config_location = config_location + '/'

    with open(config_location + 'sitelist.hjson', 'w') as file:
        file.write(json.dumps(main_dict, indent=4))


def scrape_direct(uri, config_location):
    """
    directly scrapes the sites in the db from 
    """
    pass


# run the scraper