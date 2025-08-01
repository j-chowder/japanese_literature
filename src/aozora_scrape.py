import bs4
import requests
import pandas as pd
import re
import csv

def failed():
      with open('bookinfo.csv', 'a', encoding='UTF-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([index, row['作品ID'], None, None, None])
def get_year(subtext):
    start = subtext[subtext.find('初出'):]
    match = re.search(r'\b\d{4}\b', start)
    if(match is not None):
        return match.group(0)
    else:
        return None

df = pd.read_csv('newbatch.csv',index_col=0)
print(df)

for index, row in df.loc[0:].iterrows():
    print('-' * 80, '\n', f'trying {row["作品ID"]}', '\n', '-' *80)

    print(row['XHTML/HTMLファイルURL'])
    if('www.aozora.gr.jp' not in row['XHTML/HTMLファイルURL']):
        failed()
        continue
    resp = requests.get(row['XHTML/HTMLファイルURL'])
    # resp = requests.get('https://www.aozora.gr.jp/cards/000050/files/3647_33653.html')
    resp.encoding = 'SHIFT_JIS'
    data = resp.text
    soup = bs4.BeautifulSoup(data, 'html.parser')

    body = soup.body
   

    # main_text = body.find('div', class_='main_text')
    # if(main_text is None):
    #     failed()
    #     continue
    main_text = body
    
    text = main_text.get_text(separator='\n', strip=True)
    text: str = re.sub(r'\s+', '', text)

    total = len(text)
    subtext = text[text.rfind('底本', 0, text.rfind('青空文庫')):]
    text = text[0: text.find(subtext)]

    sub = len(subtext)
    main = len(text)

    print(f'{total} = {sub} + {main} ({sub + main})')
    print(subtext)

    
    year = None
    inception = body.find('div', class_='bibliographical_information')
    
    if(inception is None): 
        # if('青空文庫' in text):
               # subtext = text[::-1][0:500][::-1]
        if('初出' in subtext):
            year = get_year(subtext)
            print(f'main_text: {year}')

    elif('初出' in inception.text):
       year = get_year(inception.text)
       print(year)

    print([index, row['作品ID'], year, len(text)])
    with open('new.csv', 'a', encoding='UTF-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([index, row['作品ID'], year, len(text), text])


    
 