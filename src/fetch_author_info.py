import requests
import pandas as pd
from datetime import datetime;
import time
import wptools
import csv
import re

def get_df():
    df = pd.read_excel('./data/aozora.xlsx', 'books', usecols=['作品ID',	'作品名',	'作品名読み',	'ソート用読み'])

    return df

def get_info(info):
    df = pd.DataFrame(info, index=[1])
    df.apply(lambda x: x.replace('[', ""))
    bd = None
    bp = None
    dd = None
    try:
        bd, bp, dd = df.loc[1, ['birth_date', 'birth_place', 'death_date']]
    except:
        if bd is None:
            try:
                bd = df.loc[1, '生年月日']
            except(KeyError):
                pass
        if bp is None:
            try:
                bd = df.loc[1, '生誕地']
            except(KeyError):
                pass
            
    if bd is not None:    
        bd = bd.replace('{', '', -1).replace('}', '', -1)
        try:
            bd = bd[bd.index('|') + 1:]
            bd = bd.replace('|', '-', -1)
            bd = re.sub(r'[^0-9-]', '', bd)
        except:
            bd = re.sub('年', '-', bd)
            bd = re.sub('月', '-', bd)
            bd = re.sub(r'[^0-9-]', '', bd)
    if bp is not None:
        if('[' in bp or ']' in bp):
            bp = bp.replace('{', '', -1).replace('}', '', -1)
            try:
                bp = bp[bp.index('[[', bp.index('現')) + 2:]
            except:
                bp = bp[bp.index('[[') + 2:]
            bp = bp[0: bp.index(']')]
        else:
            bp = bp
        
    
    if dd is not None:
        dd = dd.replace('{', '', -1).replace('}', '', -1)
        dd = dd[::-1]
        dd = dd[0: dd.index('|', 7)]
        dd = dd[::-1]
        dd = dd.replace('|', '-')

    return [bd, bp, dd]

df = get_df()

for index, row in df.loc[12820:].iterrows():
    print('-' * 80, '\n', f'trying {row["作品名"]}', '\n', '-' *80)
    
    try:
        y = wptools.page(row['作品名'],  lang='ja').get_parse()

    except(LookupError):
        try:
            y = wptools.page(row['作品名読み'], lang='ja').get_parse()

        except(LookupError):
            with open('bookdate.csv', 'a', encoding='UTF-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([index, row['作品ID']])
            continue
    try:
        page = wptools.page(wikibase=y.data['wikibase'])
    except(KeyError):
        with open('bookdate.csv', 'a', encoding='UTF-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([index, row['作品ID']])
    a = page.get_wikidata()
    print(a.data['claims'])
    print('P571' in a.data['claims'])
    if 'P571' in a.data['claims']:
        inception = a.data['claims']['P571'][0]
    else:
        inception = None
        with open('bookdate.csv', 'a', encoding='UTF-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([index, row['作品ID']])
        continue

    data = [index, row['作品ID'], inception]
    

    print(data)
    with open('bookdate.csv', 'a', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(data)
    
    

# df = pd.read_csv('authors.csv')
# df_null = df.isnull()
# rows = df_null.any(axis=1)
# df = df.loc[rows, ['author', 'last', 'first']]







