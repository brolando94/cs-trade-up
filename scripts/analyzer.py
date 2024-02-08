from requests import get
import json
import pandas as pd


class RatingObj:
    def __init__(self, value, wear, count):
        self.value = value
        self.wear = wear
        self.count = count


class CollectionObj:
    def __init__(self, collection, value, wear, count):
        self.collection = collection
        self.value = value
        self.wear = wear
        self.count = count


limit_ten = True

profile_id = input("Enter Your Profile Id: ").strip()

url = f"http://steamcommunity.com/inventory/{profile_id}/730/2?l=english&count=1000"
response = get(url)
resp_json = json.loads(response.text)
rating_list = []
collection_list = []
rating_list_light = []
collection_list_light = []
skip_list = ['covert', 'music kit', 'base grade graffiti', 'extraordinary collectible', 'extraordinary gloves']

rarity_wear_df = pd.DataFrame()
rarity_light_df = pd.DataFrame()
collection_df = pd.DataFrame()
collection_light_df = pd.DataFrame()

for item in resp_json['descriptions']:
    wear_rating = item['descriptions'][0]['value'].replace('Exterior: ', '')
    try:
        case_collection = item['descriptions'][-2]['value']
        if case_collection == ' ':
            case_collection = item['descriptions'][-3]['value']
    except IndexError:
        case_collection = 'Unknown'
    value_rating = item['type']
    value_rating = value_rating.replace(' Sniper Rifle', '')
    value_rating = value_rating.replace(' Machinegun', '')
    value_rating = value_rating.replace(' Pistol', '')
    value_rating = value_rating.replace(' Rifle', '')
    value_rating = value_rating.replace(' SMG', '')
    value_rating = value_rating.replace(' Shotgun', '')
    value_rating = value_rating.replace('™', '')
    # skip list
    if any(i in value_rating.lower() for i in skip_list):
        continue

    # case collection aggregate
    found = False
    for collection_obj in collection_list:
        if collection_obj.collection == case_collection \
                and collection_obj.wear == wear_rating \
                and collection_obj.value == value_rating:
            found = True
            collection_obj.count = collection_obj.count + 1
            break

    if not found:
        insert_obj = CollectionObj(collection=case_collection, wear=wear_rating, value=value_rating, count=1)
        collection_list.append(insert_obj)

    # case collection aggregate light
    found = False
    for collection_obj in collection_list_light:
        if collection_obj.collection == case_collection and collection_obj.value == value_rating:
            found = True
            collection_obj.count = collection_obj.count + 1
            break

    if not found:
        insert_obj = CollectionObj(collection=case_collection, wear=None, value=value_rating, count=1)
        collection_list_light.append(insert_obj)

    # wear rating aggregate
    found = False
    for rating_obj in rating_list:
        if rating_obj.wear == wear_rating and rating_obj.value == value_rating:
            found = True
            rating_obj.count = rating_obj.count + 1
            break

    if not found:
        insert_obj = RatingObj(wear=wear_rating, value=value_rating, count=1)
        rating_list.append(insert_obj)

    # wear rating aggregate light
    found = False
    for rating_obj in rating_list_light:
        if rating_obj.value == value_rating:
            found = True
            rating_obj.count = rating_obj.count + 1
            break

    if not found:
        insert_obj = RatingObj(wear=None, value=value_rating, count=1)
        rating_list_light.append(insert_obj)

# build the data frames for easy json output
for obj in rating_list:
    if limit_ten and obj.count < 10:
        continue
    rarity_wear_df = pd.concat([rarity_wear_df, pd.DataFrame([[
        obj.value,
        obj.wear,
        obj.count
    ]], columns=['Rarity', 'Wear', 'Count'])])

for obj in rating_list_light:
    if limit_ten and obj.count < 10:
        continue
    rarity_light_df = pd.concat([rarity_light_df, pd.DataFrame([[
        obj.value,
        obj.count
    ]], columns=['Rarity', 'Count'])])

for obj in collection_list:
    if limit_ten and obj.count < 10:
        continue
    collection_df = pd.concat([collection_df, pd.DataFrame([[
        obj.collection,
        obj.value,
        obj.wear,
        obj.count
    ]], columns=['Collection', 'Rarity', 'Wear', 'Count'])])

for obj in collection_list_light:
    if limit_ten and obj.count < 10:
        continue
    collection_light_df = pd.concat([collection_light_df, pd.DataFrame([[
        obj.collection,
        obj.value,
        obj.count
    ]], columns=['Collection', 'Rarity', 'Count'])])

while True:
    print("Group By:\n1. Rarity\n2. Rarity + Wear\n3. Rarity + Collection\n4. Rarity + Collection + Wear\n0. Exit")
    choice = input("Please Enter Your Selection Number: ").strip()
    match choice:
        case '0':
            exit(0)
        case '1':
            print(json.dumps(json.loads(rarity_light_df.to_json(orient='records')), indent=4))
        case '2':
            print(json.dumps(json.loads(rarity_wear_df.to_json(orient='records')), indent=4))
        case '3':
            print(json.dumps(json.loads(collection_light_df.to_json(orient='records')), indent=4))
        case '4':
            print(json.dumps(json.loads(collection_df.to_json(orient='records')), indent=4))
        case _:
            print("Please Enter A Value 1-4 Or 0 To Exit")
