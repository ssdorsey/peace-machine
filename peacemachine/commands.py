import click

from pymongo import MongoClient

# package imports
from peacemachine.translate import translate_pipe
from peacemachine.translate import Translator
from peacemachine.scrape_gdelt import gdelt_download
from peacemachine.scrape_wayback import WaybackDownloader
from peacemachine.classify_events import EventClassifier
from peacemachine import scrape_ccnews
# uri = 'mongodb://ml4pAdmin:ml4peace@192.168.176.240'

# -------------------------
# Manage command line
# -------------------------
@click.command()
# Computation settings
@click.option('-u', '--uri', required=True, help="MongoDB uri in the format mongodb://USERNAME:PASSWORD@ADDRESS") # MDB uri
@click.option('-b', '--batch-size', default=128, help="The default batch size for the selected operation")
@click.option('-nc', '--num-cpus', default=0.5, help="The number of cpus to use for processing data. Use an integer to set a specific number or a float to set a proportion")
@click.option('-ng', '--num-gpus', default=1, help="The number of gpus to use for processing data.")

@click.option('-d', '--domains', default="all", help="Domains to check on, default to 'all'")
# Scraping flags
@click.option('-g', '--gdelt', is_flag=True, help="Flag to run a gdelt check/scrape")
@click.option('-c', '--ccnews', is_flag=True, help="Flag to run a ccnews check/scrape")
@click.option('-w', '--wayback', is_flag=True, help="Flag to run a wayback check/scrape")
@click.option('-s', '--scrape-direct', is_flag=True, help="Flag to run a direct check/scrape on the sources")
# Translation flag
@click.option('-t', '--translate', default="all", help="Call a translation pass on the articles collection, specify language or it will default to all")
# Article processing flags
@click.option('-e', '--events', help="Name the model to use in classifying events")
@click.option('-ml', '--model-location', help="Directory to find the named model")
@click.option('-srl', '--srl', default="", help="Name the model to use for semantic role labelling")
@click.option('-a', '--actors', is_flag=True, help="Flag to run the actor extraction")
@click.option('-l', '--locations', is_flag=True, help="Flag to run location extraction")
@click.option('-dates', '--dates', is_flag=True, help="Flag to run date extraction")
# flag to train a new model
# TODO implement this
# @click.option('-train', '--train, help="Name the new model to train")

def cli(
    uri,
    batch_size,
    num_cpus,
    num_gpus,
    domains,
    gdelt,
    ccnews,
    wayback,
    scrape_direct,
    translate,
    events,
    model_location,
    actors,
    srl,
    locations,
    dates
):
    """Example script"""
    
    # first check for any scraping to be done
    if gdelt:
        gdelt_download(uri, num_cpus)

    if ccnews:
        scrape_ccnews.main(uri, num_cpus)

    if wayback:
        wb_downloader = WaybackDownloader(uri)
        wb_downloader.run(domains)

    if scrape_direct:
        # TODO: implement direct scrape
        # create config/sitelist automatically
        # execute command
        pass

    # then check for any translation to be done
    if translate:
        translate_pipe(uri, translate, batch_size)
        
    # finally, classify and process the stories
    if events:
        ec = EventClassifier(uri, events, model_location, batch_size)    
        ec.run()

    if actors:
        pass

    if srl:
        pass

    if locations:
        pass

    if dates:
        pass
