from datetime import datetime
import requests
import sys
import os

# Arguments - to get all posts: main.py page_id token
#           - to use date filter: main.py date_from date_to page_id token
# Date Format -> 2004-02-01


# Getting arguments
if (len(sys.argv)==5):
   from_date  = datetime.strptime(sys.argv[1], "%Y-%m-%d")
   to_date = datetime.strptime(sys.argv[2], "%Y-%m-%d")
   pageid = sys.argv[3]
   token = sys.argv[4]
else:
   from_date = datetime.strptime("2004-02-01", "%Y-%m-%d")
   to_date = datetime.strptime("2999-02-01", "%Y-%m-%d")
   pageid = sys.argv[1]
   token=sys.argv[2]


# Requesting feed
reqFeed = requests.get("https://graph.facebook.com/v2.9/" + pageid + "/feed?access_token=" + token)

if (reqFeed.status_code==400):
    print("Invalid token")
    sys.exit()

# JSON format
feedData = reqFeed.json()

# Output file
f = open(os.getcwd()+'/output.csv', 'w')
f.write("message;created_time;reactions\n")

# Counters: ix_match -> posts that are between selected dates ix_total -> all posts found
ix_match = 0
ix_total = 0

while (True):

    for item in feedData['data']:

        # Getting post date
        post_date = datetime.strptime(item["created_time"][:10], "%Y-%m-%d")

        ix_total = ix_total + 1
        print("Post Total Counter:" + str(ix_total))

        # Checking date
        if ((post_date>=from_date) and (post_date<=to_date)):
            postID = item["id"]

            # Requesting info about the post
            reqPost = requests.get("https://graph.facebook.com/v2.9/" + postID + "/reactions?access_token=" + token + "&debug=all&format=json&method=get&pretty=0&summary=total_count&suppress_http_code=1")
            postData = reqPost.json()

            try:
                reactions_counter = postData["summary"]["total_count"]
            except:
                reactions_counter = 0

            # Shared posts don't have message element
            try:
                post_msg = item["message"]
            except:
                post_msg = "shared"

            f.write(post_msg + ";" + item["created_time"] + ";" + str(reactions_counter) + "\n")

            ix_match = ix_match + 1
            print("Post Match Counter:" + str(ix_match))

    # Paging
    try:
        next_page = feedData["paging"]["next"]
    except:
        next_page = ""

    if (next_page==""):
        break
    else:
        reqFeed = requests.get(next_page)
        feedData = reqFeed.json()
        print("next page")


f.close()
