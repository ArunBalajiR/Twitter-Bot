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
import time
import tweepy


api = TwitterAPI(os.environ.get('TWITTER_CONSUMER_KEY'), 
                 os.environ.get('TWITTER_CONSUMER_SECRET'),
                 os.environ.get('TWITTER_ACCESS_TOKEN_KEY'),
                 os.environ.get('TWITTER_ACCESS_TOKEN_SECRET'))


auth = tweepy.OAuthHandler(
    os.environ.get('TWITTER_CONSUMER_KEY'),
    os.environ.get('TWITTER_CONSUMER_SECRET')
)
auth.set_access_token(
    os.environ.get('TWITTER_ACCESS_TOKEN_KEY'),
    os.environ.get('TWITTER_ACCESS_TOKEN_SECRET')
)

tweepy_api = tweepy.API(auth)

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

    if str(chosenPicture["id"]) in postedPics:
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

#Get the Respective Owners's twitter Id to mention in tweet
twitterHandle = {
    "kamalvmpt" : "@Retouch_Gallery",
    "kamalvijay32" : "@KamalOfcl",
    "rockybhai369offl" : "@RockybhaiOffcl",
    "nikhilab1511":"@Nikhil_Ofcl",
    "KeshhFlix":"@ItzKeshh",
    "ivineimmanuel0611" : "@Ivine2255",
    "deepakppvfc6":"@_DR_Designs",
    "Rakhi\u30c4":"@rakesh_tarakian",
    "suryasandy13":"@TroyboiS",
    "evilhari664":"@Hariis87937166",
    "ItsAnbuchelvan":"@itsanbuchelvan",
    "Dark Rum Pintrest":"@DarkRrum",
    "Prinz_ram":"@itzram73",
    "athulkrishnan884":"@athulkrishnanvf",
    "kannanrishu" : "@Rishi_Touches",
    "Ebi Suriya" : "@EbiSuriya",
    "deepakppvfc6" : "@_Deepthy_",
    "Retouch_Crew" : "@Retouch_Crew",

}    

# Assemble the tweet text

tweet = f"{chosenPicture['title']} \n\nImage By {twitterHandle.get(chosenPicture['ownername'],chosenPicture['ownername'])}\n\n\nHD Download Link : {chosenPicture['url_o']}"

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

            postedPics[chosenPicture['id']] = {"tweet_id":twitterPostData['id'], "posted_on":datetime.now().isoformat()}

            gist.edit(files={"posted.json": github.InputFileContent(content=json.dumps(postedPics, indent=2))})
            print(" : PostedPics updated")
        else:
            raise SystemExit(f" : FAILURE: Tweet not posted: {r.text}")


#Like Retweet specified accounts and retweet for keyword 'retouch'
try:
    tweepy_api.verify_credentials()
    print("Connected to API")
    
except:
    print("Error during authentication")



userID=['Retouch_Gallery','KamalOfcl','Rishi_Touches','ScarletSpeeds16','DarkRrum','ItzVarun_____','Ivine2255','Nikhil_Ofcl','HQ_Shots']
keyword = "Retouch"

print ('Bot is Running ..')
print("\n")
    
for user in userID:
  print(user)
  tweets = tweepy_api.user_timeline(screen_name=user, 
                  # 200 is the maximum allowed count
                  count=1,
                  include_rts = False,
                  exclude_replies=True,
                  tweet_mode = 'extended'
                  )
  for info in tweets[:1]:
      id=info.id
      print("ID: {}".format(id))
      print(info.created_at)
      print(info.full_text)
      
        
      
      status = tweepy_api.get_status(id)        
      retweeted = status.retweeted 

      if retweeted == True:
          print("The authenticated user has retweeted the tweet.")
      else:
          print("The authenticated user has not retweeted the tweet.") 
          tweet = tweepy_api.get_status(id) 
          tweet.favorite()  
          tweet.retweet()
          print("it is now retweeted")
          time.sleep(10)
          

print("Keyword Searching..")

for tweet in tweepy.Cursor(tweepy_api.search_tweets, q=keyword,result_type="mixed").items(2):
    id=tweet.id
    print("ID: {}".format(id))
    print(tweet.created_at)

    status = api.get_status(id)        
    
    if not status.favorited and not status.retweeted:
        print('Liked & ReTweeted')
        tweet.favorite()
        tweet.retweet()
        time.sleep(10)  
print("Finished")

