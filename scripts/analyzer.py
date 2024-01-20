from requests import get
import json
import pandas as pd


class RatingObj:
    def __int__(self, value, wear, count):
        self.value = value
        self.wear = wear
        self.count = count


class CollectionObj:
    def __int__(self, collection, value, wear, count):
        self.collection = collection
        self.value = value
        self.wear = wear
        self.count = count


profile_id = '76561199029580336'
url = f"http://steamcommunity.com/inventory/{profile_id}/730/2?l=english&count=1000"
response = get(url)
resp_json = json.loads(response.text)
rating_list = []
collection_list = []
rating_list_light = []
collection_list_light = []

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
        insert_obj = CollectionObj()
        insert_obj.collection = case_collection
        insert_obj.wear = wear_rating
        insert_obj.value = value_rating
        insert_obj.count = 1
        collection_list.append(insert_obj)

    # case collection aggregate light
    found = False
    for collection_obj in collection_list_light:
        if collection_obj.collection == case_collection and collection_obj.value == value_rating:
            found = True
            collection_obj.count = collection_obj.count + 1
            break

    if not found:
        insert_obj = CollectionObj()
        insert_obj.collection = case_collection
        insert_obj.value = value_rating
        insert_obj.count = 1
        collection_list_light.append(insert_obj)

    # wear rating aggregate
    found = False
    for rating_obj in rating_list:
        if rating_obj.wear == wear_rating and rating_obj.value == value_rating:
            found = True
            rating_obj.count = rating_obj.count + 1
            break

    if not found:
        insert_obj = RatingObj()
        insert_obj.wear = wear_rating
        insert_obj.value = value_rating
        insert_obj.count = 1
        rating_list.append(insert_obj)

    # wear rating aggregate light
    found = False
    for rating_obj in rating_list_light:
        if rating_obj.value == value_rating:
            found = True
            rating_obj.count = rating_obj.count + 1
            break

    if not found:
        insert_obj = RatingObj()
        insert_obj.value = value_rating
        insert_obj.count = 1
        rating_list_light.append(insert_obj)

if len(rating_list) > 0:
    df = pd.DataFrame()
    for obj in rating_list:
        df = pd.concat([df, pd.DataFrame([[
            obj.value,
            obj.wear,
            obj.count
        ]], columns=['Rarity', 'Wear', 'Count'])])

    df.to_excel('output/Rarity + Wear.xlsx', index=False)

if len(rating_list_light) > 0:
    df = pd.DataFrame()
    for obj in rating_list_light:
        df = pd.concat([df, pd.DataFrame([[
            obj.value,
            obj.count
        ]], columns=['Rarity', 'Count'])])

    df.to_excel('output/Rarity Light.xlsx', index=False)

if len(collection_list) > 0:
    df = pd.DataFrame()
    for obj in collection_list:
        df = pd.concat([df, pd.DataFrame([[
            obj.collection,
            obj.value,
            obj.wear,
            obj.count
        ]], columns=['Collection', 'Rarity', 'Wear', 'Count'])])

    df.to_excel('output/Collection + Rarity + Wear.xlsx', index=False)

if len(collection_list_light) > 0:
    df = pd.DataFrame()
    for obj in collection_list_light:
        df = pd.concat([df, pd.DataFrame([[
            obj.collection,
            obj.value,
            obj.count
        ]], columns=['Collection', 'Rarity', 'Count'])])

    df.to_excel('output/Collection + Rarity.xlsx', index=False)

print()
