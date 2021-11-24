import os
import json
import github
import shutil
import random
import pprint
import requests
from pprint import pprint
from datetime import datetime
from TwitterAPI import TwitterAPI


api = TwitterAPI(os.environ.get('TWITTER_CONSUMER_KEY'), 
                 os.environ.get('TWITTER_CONSUMER_SECRET'),
                 os.environ.get('TWITTER_ACCESS_TOKEN_KEY'),
                 os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'))


# Get the GitHub Gist that contains our state database
gh = github.Github(os.environ.get('GIST_TOKEN'))
gist = gh.get_gist(os.environ.get('PICTURE_DB'))


postedPics = json.loads(gist.files['posted.json'].content)


print(f" : Loaded Posted Pictures Database with {len(postedPics)} entries")

# Get the PicturesToPost DB

req = requests.get(os.environ.get('PICTURE_DB_URL'))
picsToPost = req.json()

print(f" : Loaded PicturesToPost DB with {len(picsToPost)} entries")

# Randomly select picsToPost from the database, comparing them to the postedPics database
#   to make sure they haven't already been posted. If they have then pick a new one.

print(" : Choosing a random picture")

while True:
    # Find our random picture to post from the DB

    chosenPicture = random.choice(picsToPost)

    print(f" : Checking Picture '{chosenPicture['title']}'")

    if chosenPicture['title'] in postedPics:
        print(f" : WARNING: Memory {chosenPicture['title']} already posted; choosing new one...")
        continue
    else:
        break

print(" : Picture Chosen")
print("==================================================================")
pprint(chosenPicture)
print("==================================================================")

# Download the Chosen Picture

response = requests.get(chosenPicture['url_o'], stream=True)

with open('img.jpg', 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)

# Assemble the tweet text

tweet = f"{chosenPicture['title']} \n\nPhoto By {chosenPicture['ownername']}"

print(" : Preview of tweet to be posted")
print("==================================================================")
print(tweet)
print("==================================================================")

# Post to Twitter!

if "DRY_RUN" in os.environ:
    print(" : Dry Run, exiting without posting to twitter")
else:
    # STEP 1 - upload image
    file = open('img.jpg', 'rb')
    data = file.read()
    r = api.request('media/upload', None, {'media': data})
    if r.status_code == 200:
        print(' : SUCCESS: Photo upload to twitter')
    else: 
        raise SystemExit(f" : FAILURE: Photo upload to twitter: {r.text}")

    # STEP 2 - post tweet with a reference to uploaded image
    if r.status_code == 200:
        media_id = r.json()['media_id']
        r = api.request('statuses/update', {'status': tweet, 'media_ids': media_id})
        if r.status_code == 200: 

            twitterPostData = json.loads(r.text)

            print(' : SUCCESS: Tweet posted')

            # Append to the postedPics database

            postedPics[chosenPicture['title']] = {"tweet_id":twitterPostData['id'], "posted_on":datetime.now().isoformat()}

            gist.edit(files={"posted.json": github.InputFileContent(content=json.dumps(postedPics, indent=2))})
            print(" : PostedPics updated")
        else:
            raise SystemExit(f" : FAILURE: Tweet not posted: {r.text}")


