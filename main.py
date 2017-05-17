from datetime import datetime
from urllib.parse import unquote
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
req_feed = requests.get("https://graph.facebook.com/v2.9/" + pageid + "/feed?limit=100&access_token=" + token)

if (req_feed.status_code==400):
    print("Invalid token")
    sys.exit()

# JSON format
feed_data = req_feed.json()


# Output file
f = open(os.getcwd()+'/output.csv', 'w')
f.write("message_title;message_link;created_time;reactions;total_reach\n")

# Counters: ix_match -> posts that are between selected dates ix_total -> all posts found
ix_match = 0
ix_total = 0

while (True):

    for item in feed_data['data']:

        # Getting post date
        post_date = datetime.strptime(item["created_time"][:10], "%Y-%m-%d")

        ix_total = ix_total + 1
        print("Total Counter:" + str(ix_total))

        # Checking date
        if ((post_date>=from_date) and (post_date<=to_date)):
            post_id = item["id"]

            # unknown posts don't have message element, usually they are new photos or some profile update
            try:
                post_msg = item["message"]
            except:
                post_msg = "unknown"

            # Requesting info about the post
            req_post = requests.get("https://graph.facebook.com/v2.9/" + post_id + "/reactions?access_token=" + token + "&debug=all&format=json&method=get&pretty=0&summary=total_count&suppress_http_code=1")

            if (req_post.status_code == 400):
                print("Invalid token")
                sys.exit()

            post_data = req_post.json()

            # Getting the summary of reactions
            try:
                reactions_counter = post_data["summary"]["total_count"]
            except:
                reactions_counter = 0

            req_attach = requests.get("https://graph.facebook.com/v2.9/" + post_id + "/attachments?access_token=" + token)

            if (req_attach.status_code == 400):
                print("Invalid token")
                sys.exit()


            # Getting post link
            attach_data = req_attach.json()
            for item_attach in attach_data['data']:
                try:
                    attach_link = item_attach["target"]["url"]
                except:
                    attach_link = ""

            # Getting the reach amount - Facebook has a constraint that only returns a value for pages with more than 30 people
            req_reach = requests.get("https://graph.facebook.com/v2.9/" + post_id + "/insights/post_impressions_unique?access_token=" + token)
            if (req_reach.status_code == 400):
                print("Invalid token")
                sys.exit()

            Reach_data = req_reach.json()
            for item_reach in Reach_data['data']:
                for item_reach_counter in item_reach['values']:
                    try:
                        reach_number = item_reach_counter["value"]
                    except:
                        reach_number = "0"

            # cleaning' data
            post_msg=post_msg.replace('\n',' ')
            attach_link = unquote(unquote(attach_link))
            attach_link=attach_link.replace('https://l.facebook.com/l.php?u=','')

            f.write(post_msg+ ";" + attach_link + ";" + item["created_time"] + ";" + str(reactions_counter) + ";" + str(reach_number) + "\n")

            ix_match = ix_match + 1
            print("Match Counter:" + str(ix_match))

    # Paging
    try:
        next_page = feed_data["paging"]["next"]
    except:
        next_page = ""

    if (next_page==""):
        break
    else:
        req_feed = requests.get(next_page)
        feed_data = req_feed.json()
        print("next page")


f.close()
