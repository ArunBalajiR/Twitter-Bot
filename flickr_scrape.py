#!/usr/local/bin/python3
import os
import sys
import json
import flickrapi
from pprint import pprint

# flickr_api_key    = os.environ.get('FLICKR_API_KEY')
# flickr_api_secret = os.environ.get('FLICKR_API_SECRET')

flickr_api_key    = "e29282819555c436e94c770bfbe0c035"
flickr_api_secret = "a98eb427dd24a45b"

# flickrUserId = os.environ.get('FLICKR_USER_ID')
flickrUserId = "194367389@N08"
firstPage = 1

flickr = flickrapi.FlickrAPI(flickr_api_key, flickr_api_secret, format='parsed-json')

photoDb = []
fetchPage = firstPage

while True:

    print(f"Fetching page: {fetchPage}. Total records fetched: {len(photoDb)}")

    results = flickr.photos.search(user_id=flickrUserId, per_page='407', extras='description,url_o,owner_name', page=fetchPage)
    
    for item in results['photos']['photo']:
        photoDb.append(item)
    if fetchPage >= results['photos']['pages']:
        break
    else:
        fetchPage += 1

# with open(os.environ.get('OUTFILE'), 'w') as outfile:
with open("photos_unposted_kamalvj.json", 'w') as outfile:    
    json.dump(photoDb, outfile, indent=2)
    outfile.close()