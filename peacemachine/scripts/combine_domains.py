import os
import json

def get_domains():
    """
    get a list of the domains from the individual files I have
    """
    file_names = [ff for ff in os.listdir('../data/domains') if ff.startswith('domains_')]

    all_domains = []

    for fn in file_names:
        with open(f'../data/domains/{fn}', 'r') as _file:
            domains = _file.readlines()
            all_domains += domains

    all_domains = [dd.strip() for dd in all_domains]

    return all_domains


def write_sitelist(domains, output_file):
    """
    writes an hjson sitelist of the domains with each having a sitemap and recursive scraper
    """
    master = {'base_urls': []}

    for dd in domains:
        master['base_urls'].append({'url': f'http://www.{dd}', 'crawler':'RecursiveSitemapCrawler'})

    with open(output_file, 'w') as _file:
        json.dump(master, _file)


domains = get_domains()
write_sitelist(domains, '/home/devlab/Dropbox/news-please-mongo/sitelist.hjson')
write_sitelist(domains, '/media/devlab/HDD0/news-please-repo/config/sitelist.hjson')
