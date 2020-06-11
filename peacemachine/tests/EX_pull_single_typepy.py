import pandas as pd
import pymongo
client = pymongo.MongoClient()
db = client.ml4p

events = db.events

# Aug 2019 arrests Tanzania

cursor = events.find(
    {
        'bad_location': 'Tanzania'
        ,'event_type': 'arrest'
        ,'date_publish': {'$regex': '^2019-08'}
    }
)

pulled = []

for ee in cursor:
    pulled.append(ee)

df = pd.DataFrame(pulled)

df = df.drop_duplicates('combined')


