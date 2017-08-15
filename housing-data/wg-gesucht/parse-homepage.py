#!/usr/local/bin/python
import re
import time
import requests
import numpy as np
import pandas as pd
import sqlite3 as db
from pyquery import PyQuery as pq
from collections import namedtuple

def parse_wg_gesucht(tr):
    tds = [td.text_content().strip() for td in e.findall('td')][2:]
    tds.append('http://wg-gesucht.de/' + tr.attrib['adid'])
    return tds

if __name__ == '__main__':
    con = db.connect('wg-gesucht.db')

    einzimmer = ['price', 'area', 'borough', 'frei_ab', 'frei_bis', 'url']
    wohnung = [ 'date', 'price', 'area', 'borough', 'frei_ab', 'frei_bis', 'url']
    page_format = {'einzimmer':einzimmer, 'wohnung':wohnung}
    base_templates = {'einzimmer':'http://www.wg-gesucht.de/1-zimmer-wohnungen-in-Hamburg.55.1.0.0.html?offer_filter=1&city_id=55&category=1&rent_type=2&rMax=750&img_only=1',
                     'wohnung':'http://www.wg-gesucht.de/wohnungen-in-Hamburg.55.2.0.0.html?offer_filter=1&sort_column=0&city_id=55&category=2&rent_type=2&rMax=750&img_only=1'}

    dfs = []
    for wohnung_typ, template in base_templates.items():
        """        
        url = template.format(**{'page':i})
        res = requests.get(url)
        cookies[wohnung_typ] = res.cookies
        """
        res = requests.get(template)
        d = pq(res.text)        
        trs = d('#table-compact-list tr').not_('.inlistTeaser')[2:]
        ids = [tr.attrib['adid'] for tr in trs]

        data = [{k:v for k, v in zip(page_format[wohnung_typ], parse_wg_gesucht(e))} for e in trs]
        df = pd.DataFrame(data, columns=page_format[wohnung_typ])
        inactive = (df.frei_ab == 'aktuell') & (df.frei_bis == 'vermietet')
        df = df[~inactive]
        df['wohnung_typ'] = wohnung_typ
        dfs.append(df)
        time.sleep(np.random.uniform(0.25, 1))
    if len(df) > 0:
        df = pd.concat(dfs, ignore_index=True)
        df['price'] = df.price.apply(lambda x: re.sub("[^0-9]", "", x))
        df['area'] = df.area.apply(lambda x: re.sub("[^0-9]", "", x))
        df['price'] = pd.to_numeric(df.price)
        df['area'] = pd.to_numeric(df.area)
        df['price_area_ratio'] = df.price/df.area
        del df['date']
        del df['frei_bis']
        df.to_sql('overview', con, if_exists='append', index=False)
