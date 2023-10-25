import pandas as pd
import pycurl as curl # The API can be accessed with the package berserk instead of curl. https://github.com/lichess-org/berserk
from io import BytesIO
user = "AlvinM"
base_url = "https://lichess.org/api/games/user/"
no_games=500
rated ='true'
perfType='blitz'
b_obj = BytesIO()
c = curl.Curl()
c.setopt(c.URL, base_url +user +f"?max={no_games}&rated={rated}&perfType={perfType}")
c.setopt(c.WRITEDATA, b_obj)
c.setopt(c.HTTPHEADER,["Accept: application/x-ndjson"])
c.perform()
c.close()
get_body = b_obj.getvalue()
with open("my_dataset.json",'w') as writer:
    writer.writelines(get_body.decode('utf8'))
raw = pd.read_json("my_dataset.json",orient ='records',lines=True)
raw['time'] = raw.clock.apply(lambda x:x['initial'])
raw['increment'] = raw.clock.apply(lambda x:x['increment'])
raw['duration'] = (raw.lastMoveAt - raw.createdAt) / 1000
raw['color'] = raw.players.apply(lambda x: 'white' if x['white']['user']['name'] == user else 'black')
raw['rating'] = raw.players.apply(lambda x: x['white']['rating'] if x['white']['user']['name'] == user else x['black']['rating'])
raw['opponent'] = raw.players.apply(lambda x: x['black']['user']['name'] if x['white']['user']['name'] == user else x['white']['user']['name'])
raw['opponent_rating'] = raw.players.apply(lambda x: x['black']['rating'] if x['white']['user']['name'] == user else x['white']['rating'])
raw['rating_diff'] = raw.rating - raw.opponent_rating
raw['result'] = raw.apply(lambda x: 0.5 if x['status']=='draw' else int(x['winner']==x['color']),axis=1)
raw['half_moves'] = raw.moves.apply(lambda x: len(x.split(" ")))
raw['push_harry'] = raw.apply(lambda x: int('h4' in x.moves.split(" ")[:40:2]) if x.color == 'white' else int('h5' in x.moves.split(" ")[1:41:2]),axis=1)
raw['opponent_rating_bracket'] = 100*(raw.opponent_rating//100);

for x in raw.status.unique():
    raw[x] = (raw.status ==x).apply(int)
raw = raw.drop(['id','rated','speed','perf','players','variant','clock','createdAt','lastMoveAt','winner','status'],axis=1)
raw.to_csv(f'{user}.csv',index=False)
