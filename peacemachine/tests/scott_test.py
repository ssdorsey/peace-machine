"""
Script for scott's LAC test
"""
from pymongo import MongoClient

db = MongoClient('mongodb://ml4pAdmin:ml4peace@devlab-server').ml4p

urls = [
    'https://www.nytimes.com/2019/04/24/technology/ecuador-surveillance-cameras-police-government.html',
    'https://www.nytimes.com/2019/04/26/reader-center/ecuador-china-surveillance-spying.html',
    'https://www.nytimes.com/2018/12/24/world/americas/ecuador-china-dam.html',
    'https://www.nytimes.com/2015/07/26/business/international/chinas-global-ambitions-with-loans-and-strings-attached.html',
    'https://www.nytimes.com/2020/01/19/us/politics/south-america-russian-twitter.html',
    'https://www.nytimes.com/2020/06/01/business/coronavirus-poor-countries-debt.html',
    'https://www.theguardian.com/world/2017/mar/19/ecuador-indigenous-shuar-el-tink-mining-land-dispute',
    'https://www.theguardian.com/environment/2014/feb/19/ecuador-oil-china-yasuni',
    'https://www.theguardian.com/world/2013/mar/26/ecuador-chinese-oil-bids-amazon',
    'https://www.theguardian.com/world/2015/jun/02/ecuador-murder-jose-tendetza-el-mirador-mine-project',
    'https://www.theguardian.com/environment/andes-to-the-amazon/2014/may/16/what-good-chinas-green-policies-banks-dont-listen',
    'https://www.theguardian.com/environment/andes-to-the-amazon/2015/may/19/li-keqiang-latin-america-respect-rights-environment',
    'https://www.theguardian.com/environment/andes-to-the-amazon/2017/jan/07/ecuadors-leading-environmental-group-fights-forced-closure',
    'https://www.theguardian.com/world/2015/may/29/200000-shark-fins-seized-by-police-in-ecuador-bound-for-asia-markets',
    'https://www.theguardian.com/world/2018/may/15/julian-assange-ecuador-london-embassy-how-he-became-unwelcome-guest',
    'https://www.theguardian.com/world/2013/jun/23/edward-snowden-gchq',
    'https://www.theguardian.com/world/2013/jun/27/ecuador-us-trade-pact-edward-snowden',
    'https://www.theguardian.com/world/2018/sep/21/julian-assange-russia-ecuador-embassy-london-secret-escape-plan',
    'https://www.theguardian.com/world/2015/dec/04/protests-in-ecuador-as-lawmakers-approve-unlimited-presidential-terms',
    'https://www.reuters.com/article/ecuador-debt-china/ecuador-clinches-900-mln-loan-from-china-moreno-idUSL1N1YH0YJ',
    'http://www.xinhuanet.com/english/2020-04/30/c_139020269.htm',
    'https://www.elcomercio.com/actualidad/tecnologia-movil-5g-ecuador-2020.html',
    'https://www.elcomercio.com/actualidad/huawei-mercado-telefonos-inteligentes-ecuador.html',
    'https://www.elcomercio.com/actualidad/bob-lee-clientes-huawei-ecuador.html',
    'https://www.elcomercio.com/actualidad/china-donacion-ecuador-insumos-medicos.html',
    'https://www.elcomercio.com/actualidad/ecuador-rusia-tratado-extradicion-delincuencia.html'
]

dict(zip(urls, [bool(db.articles.find_one({'url': url})) for url in urls]))

db.lac.find_one({'url': urls[-6]})
