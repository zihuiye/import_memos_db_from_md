import copy
import re
import sqlite3
import time
from pathlib import Path
from urllib.parse import quote
import json

from dateutil.parser import parse

import boto3
import shortuuid
from tqdm import tqdm

img_md_pattern = re.compile(r'!\[.*?\]\((.*?)\)') # extract image 
link_md_pattern = re.compile(r'\[.*?\]\((.*?)\)') # extract link 
title_date_pattern = re.compile(r'# \d{8}') # title date like "# 20241023"

R2_accesskeyID = 'ot65661j35k46q34q2derhu'
R2_accesskeySecret = '90oe99897u0o0e774e8i7678a98oeu'
R2_endpoint = 'https://5546ue357o65a34d8f846e6e2u1.r2.cloudflarestorage.com/'
R2_region = 'auto'
R2_bucket = 'memos'
R2_public_hostname = 'https://store.example.com/'


folder = 'diary' # 'quicknotes' 'gpt' 'collections' 'diary'

DIR_PATH = '/mnt/d/userfiles/Documents/onenote_export/diary/'

session = boto3.Session(
        aws_access_key_id=R2_accesskeyID,
        aws_secret_access_key=R2_accesskeySecret
    )
settings = {'endpoint_url': R2_endpoint, 'region_name':R2_region}
client = session.client('s3', config=boto3.session.Config(signature_version='s3v4'),
                         **settings)

def explain_md(content):
    haslink = True if re.findall(link_md_pattern, content) else False
    timestamp = int(time.time())
    matches = re.findall(title_date_pattern, content)
    if matches:
        timestamp = int(parse(matches[0][2:]).timestamp())
    processed = copy.deepcopy(content)
    image_phases = re.findall(img_md_pattern, content)

    for image in image_phases:
        # send image to r2 using s3 api
        image_key = f'assets/{int(time.time())}_{image}'
        client.put_object(Bucket=R2_bucket, Key=image_key, 
                          Body=Path(DIR_PATH+image).read_bytes())
        processed = processed.replace(image, 
                                      R2_public_hostname+quote(image_key))
    return processed, timestamp, haslink

def read_md(path):
    md_path = Path(path)
    if not md_path.exists():
        return []
    result = []
    for md in md_path.iterdir():
        if md.is_file() and md.name.endswith('.md'):
            result.append(md.read_text())
    return result



def main():
    con = sqlite3.connect("memos_prod.db")
    cur = con.cursor()
    dir_path = Path(DIR_PATH)
    mds = read_md(DIR_PATH)
    for md in tqdm(mds):
        content, timestamp, haslink = explain_md(md)
        content += f'\n#{dir_path.name}'
        # write db
        VISIBILITY = 'PUBLIC' if dir_path.name in ['collections'] else 'PRIVATE'
        payload = {"property":{"tags": [dir_path.name]}}
        if haslink:
            payload['property']['hasLink'] = True
        
        cur.execute("""
INSERT INTO memo(uid, creator_id, created_ts, updated_ts, row_status, content, visibility, tags, payload) 
    VALUES(?,?,?,?,?,?,?,?,?)
        """,
        (shortuuid.uuid(),1,timestamp,timestamp,'NORMAL', content,
         VISIBILITY,f'["{dir_path.name}"]',json.dumps(payload)))
        con.commit()
    con.close()

if __name__ == '__main__':
    main()
