from multiprocessing import Process,Queue, Pool
import bz2, sys
import xmltodict
from tqdm.auto import tqdm
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from multiprocessing import Pool
import io, os
import json
import time

# ------------------------------
# download and process the data
# ------------------------------
os.system("wget https://dumps.wikimedia.org/enwiki/latest/enwiki-latest-pages-articles-multistream.xml.bz2")
os.system("python -m gensim.scripts.segment_wiki -i -f enwiki-latest-pages-articles-multistream.xml.bz2 -o enwiki-latest-pages-articles-multistream.json.gz -w 100")

# ------------------------------
# script to insert into ES
# ------------------------------

consumer_n = 20
buck_size = 40
wiki = "enwiki-latest-pages-articles-multistream.json.gz"

def import_es(es, lines):
    pages = []
    for line in lines:
        page = json.loads(line)
        for key in page.keys():
            page[key] = json.dumps(page[key])
        if 'interlinks' in page:
            page['entitylinks'] = page.pop('interlinks')
        page['_index'] = 'enwiki'
        page['_type'] = "wiki"
        pages.append(page)
    res = helpers.bulk(es, pages)

pbar = tqdm()

def procducer(q, wikifile, pbar):
    begin_record = False
    cnt = 0
    print("processing...")
    for line in os.popen("zcat %s"%wikifile):
        pbar.update(max(cnt - q.qsize() - pbar.n, 0))
        q.put(line)
        cnt += 1
        pbar.set_description("Queue Remain: %s" % q.qsize())
    print("total pages: %d", cnt)

    for i in range(consumer_n):
        q.put(None)
    while q.qsize() > 0:
        time.sleep(1)
        pbar.update(max(cnt - q.qsize() - pbar.n, 0))
        pbar.set_description("Queue Remain: %s" % q.qsize())
    print("End procducer")


def consumer(q):
    es=Elasticsearch([{'host':'localhost','port':9200}], timeout=50, max_retries=10, retry_on_timeout=True)
    pages = []
    while True:
        res=q.get()
        if res == None or len(pages) >= buck_size:
            import_es(es, pages)
            pages = []
        if res is None:
            break
        pages.append(res)

    print("End consumer")


if __name__ == '__main__':
    q=Queue()
    p=Process(target=procducer,args=(q, wiki, pbar))
    p.start()

    cs = []
    for _ in range(consumer_n):
        c = Process(target=consumer,args=(q,))
        c.start()
        cs.append(c)


    p.join()

    for c in cs:
        c.join()
    pbar.close()

    print('Finish Processing.')