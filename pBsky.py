#!/usr/bin/python3

# Author: David Carryer 
# Email: david@davidcarryer.com
# Bluesky: @davidcarryer.com
#
# Uses atprototools for bSky Interopability.
# https://github.com/ianklatzco/atprototools

# Do my imports
from atprototools import Session
from utils import *
import argparse
import configparser
import re
import json

# Display Colors
class DC:
    REPLY_TO = '\033[95m'
    REPOSTED_BY = '\033[94m'
    CLEAR = '\033[0;0m'
    BRACKET = '\033[0;93m'
    PAREN = '\033[0;93m'
    HANDLE = '\033[38;5;159m'
    DISPLAY_NAME = '\033[1;96m'
    BASIC = '\033[1;97m'
    BASIC_LIGHT = '\033[0;37m'
    REPLY = '\033[0;36m'
    REPOST = '\033[0;36m'
    LIKE = '\033[0;36m'
    IDS = '\033[38;5;236m'
    POST = '\033[38;5;65m' 
    DIVIDER = '\033[0;90m'
    REPLY_BAR = '\033[0;90m'
    IMAGE = '\033[38;5;220m'

# Parse the passed arguments
parser = argparse.ArgumentParser(
    prog='pBsky',
    description='Comand line BlueSky client for Linux.')
parser.add_argument('-p', '--post', type=str,
                    help='create a post from the given string.')
parser.add_argument('-d', '--delete', nargs=2,
                    help='delete a post with given did and rkey.')
parser.add_argument('-g', '--get', nargs='*',
                    help='get your last n posts (default 10) or another users last n posts.')
parser.add_argument('-r', '--reply', nargs=3,
                    help='replay to a post with given string, did, and rkey')
parser.add_argument('-f', '--follow', type=str,
                    help='follow a user with a given username')
parser.add_argument('-gp', '--getprofile', type=str,
                    help='get a profile for a user')
args = parser.parse_args()

# Open the INI for authentication information.
config = configparser.ConfigParser()
config.read('pBsky.ini')
USERNAME = config['AUTHENTICATION']['USERNAME'] 
PASSWORD = config['AUTHENTICATION']['PASSWORD'] 

# Establish the session
session = Session(USERNAME, PASSWORD)


# GET PROFILE
# Usage (Get a profile): ./pBsky.py -gp {username - without the @}
if (args.getprofile != None):
    profile = session.get_profile(username=args.getprofile)
    loaded_json = profile.json()

    profile_did = str(loaded_json.get('did'))
    profile_handle = str(loaded_json.get('handle'))
    profile_displayName = str(loaded_json.get('displayName'))
    profile_description = str(loaded_json.get('description'))
    profile_followsCount = str(loaded_json.get('followsCount'))
    profile_followersCount = str(loaded_json.get('followersCount'))
    profile_postsCount = str(loaded_json.get('postsCount'))
    profile_labels = str(loaded_json.get('labels'))

    print("\n") 
    print(DC.DIVIDER + "-----------------------------------------------------------------")

    print(DC.BRACKET + "[" + DC.HANDLE +"@" + profile_handle + DC.BRACKET +"] " + 
          DC.DISPLAY_NAME + profile_displayName + DC.CLEAR) 
    print(DC.BASIC + profile_description.strip())

    if (profile_labels!="[]"):
        print(DC.BASIC_LIGHT + "Labels: " + profile_labels)   

    print(DC.IDS + profile_did)    

    print(DC.PAREN + "(" + 
          DC.REPLY + "Follows" + DC.BASIC + ": " + DC.BASIC_LIGHT + profile_followsCount + " " +
          DC.REPOST + "Followers" + DC.BASIC + ": " + DC.BASIC_LIGHT + profile_followersCount + " " +
          DC.LIKE + "Posts" + DC.BASIC + ": " + DC.BASIC_LIGHT + profile_postsCount + 
          DC.PAREN + ")")

    print(DC.DIVIDER + "-----------------------------------------------------------------")   
    print("\n") 


# POST
# Usage (Post Something): ./pBsky.py -p "{post_text" 
if (args.post != None):
    session.postBloot(args.post)
    # Image Example: session.post_bloot("here's an image!", "path/to/your/image")


# REPLY
# Usage (Reply to Something): ./pBsky.py -r "This is my reply" {rkey}
if (args.reply != None):

    # Build the at_uri based on the did and rkey
    at_uri = "at://did:plc:" + args.reply[1] + "/app.bsky.feed.post/" + args.reply[2]

    # Get the post.
    original_post = session.getBlootByUrl(at_uri).json().get('posts')

    # Need to create a dictionary to pass as the reply details.
    root = {
        "cid" : original_post[0].get('cid'),
        "uri" : original_post[0].get('uri')
    }
    parent = {
        "cid" : original_post[0].get('cid'),
        "uri" : original_post[0].get('uri')
    }
    reply_ref = {
        "root" : root,
        "parent" : parent
    } 

    # Post
    session.postBloot(args.reply[0], reply_to=reply_ref)


# DELETE
# Usage (Delete Something): ./pBsky.py -d {did} {rkey}
if (args.delete != None):
    session.deleteBloot(args.delete[0], args.delete[1])


# FOLLOW
# Usage (Follow Someone): ./pBsky.py -f {username - without the @}
if (args.follow != None):
    session.follow(username=args.follow)


# GET
# Usage (Get Following Timeline + Max Count): ./pBsky.py -g 10
# Usage (Get Specific Timeline + Max Count):  ./pBsky.py -g davidcarryer.com 10
if (args.get != None):

    # Will grab the 'following' timeline when a number is specified.
    if (args.get[0].isnumeric()):
        skyline = session.getSkyline(args.get[0]) #defaults to 10
        feed = skyline.json().get('feed')
    else:
        # Will grab the timeline of a specific user.
        skyline = session.getLatestNBloots(args.get[0], args.get[1]).content
        feed = json.loads(skyline).get('feed')

    print("\n") 

    for i in feed:
        # spacer to ident reply to make it easier to identify with reply - default no space
        bloot_spacer = ""

        # Capture all the individual elements that make up a post
        bloot_text = str(i.get('post').get('record').get('text'))
        bloot_displayName = str(i.get('post').get('author').get('displayName'))
        bloot_did = str(i.get('post').get('author').get('did')[8:])
        bloot_rkey = str(i.get('post').get('uri')).split("/")[-1]
        bloot_handle = str(i.get('post').get('author').get('handle'))
        bloot_replyCount = str(i.get('post').get('replyCount'))
        bloot_repostCount = str(i.get('post').get('repostCount'))
        bloot_likeCount = str(i.get('post').get('likeCount'))
        bloot_uri = str(i.get('post').get('uri'))
        bloot_anyEmbedded = str(i.get('post').get('embed'))            

        # The main text is full of newlines, etc.  Strip them all to jeep display clean.
        re.sub('[\W_]+',' ',bloot_text) # strip everyting but letters and characters
        bloot_text = ''.join(bloot_text.split('\n')) # strip out all the specific \n

        print(DC.DIVIDER + "=================================================================")
        print('')

        # If this is a reply, post the parent to the reply.
        bloot_reply = str(i.get('post').get('record').get('reply'))
        if (bloot_reply != "None"):
            bloot_spacer = "   " # spacer to ident reply to make it easier to identify with reply

            bloot_reply_uri = str(i.get('post').get('record').get('reply').get('parent').get('uri'))
            ret_json = session.getBlootByUrl(bloot_reply_uri).json().get('posts')
            bloot_response_author_handle = str(ret_json[0].get('author').get('displayName'))

            print(DC.REPLY_TO + "< Reply to " + bloot_response_author_handle + DC.CLEAR)

            orig_bloot_text = str(i.get('reply').get('parent').get('record').get('text'))
            re.sub('[\W_]+',' ',orig_bloot_text) # strip everyting but letters and characters
            orig_bloot_text = ''.join(orig_bloot_text.split('\n')) # strip out all the specific \n

            orig_bloot_displayName = str(i.get('reply').get('parent').get('author').get('displayName'))
            orig_bloot_handle = str(i.get('reply').get('parent').get('author').get('handle'))
            orig_bloot_did = str(i.get('reply').get('parent').get('author').get('did')[8:])
            orig_bloot_uri = str(i.get('reply').get('parent').get('uri')).split("/")[-1]
            orig_bloot_replyCount = str(i.get('reply').get('parent').get('replyCount'))
            orig_bloot_repostCount = str(i.get('reply').get('parent').get('repostCount'))
            orig_bloot_likeCount = str(i.get('reply').get('parent').get('likeCount'))
            orig_bloot_anyEmbedded = str(i.get('reply').get('embed'))

            print(DC.BRACKET + "[" + DC.HANDLE +"@" + orig_bloot_handle + DC.BRACKET +"] " + 
                  DC.DISPLAY_NAME + orig_bloot_displayName + DC.BASIC + ":" + DC.CLEAR) 
            print(DC.POST + orig_bloot_text.strip())    

            # any embedded images
            if (orig_bloot_anyEmbedded != "None"): 
                if (i.get('post').get('embed').get('$type') == "app.bsky.embed.images#view"):
                    orig_bloot_images = i.get('post').get('embed').get('images')

                    for j in orig_bloot_images:
                        orig_bloot_image_alt = j.get('alt')
                        if (orig_bloot_image_alt == ''):
                            orig_bloot_image_alt = "No alt text provided."
                        print(bloot_spacer + DC.IMAGE + "[Embedded Image: " + orig_bloot_image_alt + "]")  

            print(DC.IDS + orig_bloot_did + " " + orig_bloot_uri)

            print(DC.PAREN + "(" + 
                  DC.REPLY + "Reply" + DC.BASIC + ": " + DC.BASIC_LIGHT + orig_bloot_replyCount + " " +
                  DC.REPOST + "Repost" + DC.BASIC + ": " + DC.BASIC_LIGHT + orig_bloot_repostCount + " " +
                  DC.LIKE + "Like" + DC.BASIC + ": " + DC.BASIC_LIGHT + orig_bloot_likeCount + 
                  DC.PAREN + ")")

            print(DC.REPLY_BAR + bloot_spacer + "|")
            print(DC.REPLY_BAR + bloot_spacer + "|")
            print(DC.REPLY_BAR + bloot_spacer + "|")

        # Looks like this is a repost.
        bloot_reason = str(i.get('reason'))
        if (bloot_reason != "None"):
            bloot_repost_author_displayName = str(i.get('reason').get('by').get('displayName'))
            print(DC.REPOSTED_BY + "+ Reposted by " + bloot_repost_author_displayName + DC.CLEAR)

        print(bloot_spacer + DC.BRACKET + "[" + DC.HANDLE +"@" + bloot_handle + DC.BRACKET +"] " + 
              DC.DISPLAY_NAME + bloot_displayName + DC.BASIC + ":" + DC.CLEAR) 
        print(bloot_spacer + DC.POST + bloot_text.strip())

        # anything embedded?
        if (bloot_anyEmbedded != "None"): #We found something embedded
            if (i.get('post').get('embed').get('$type') == "app.bsky.embed.images#view"): #The embeeded this is an image
                bloot_images = i.get('post').get('embed').get('images')

                for j in bloot_images:
                    bloot_image_alt = j.get('alt')
                    if (bloot_image_alt == ''):
                        bloot_image_alt = "No alt text provided."
                    print(bloot_spacer + DC.IMAGE + "[Embedded Image: " + bloot_image_alt + "]")         

            if (i.get('post').get('embed').get('$type') == "app.bsky.embed.record#view"):
                bloot_spacer = "   " # spacer to ident embedded post
                embedded_text = i.get('post').get('embed').get('record').get('value').get('text')
                embedded_displayName = i.get('post').get('embed').get('record').get('author').get('displayName')
                embedded_handle = i.get('post').get('embed').get('record').get('author').get('handle')

                print('')
                print(DC.DIVIDER + bloot_spacer + '--------------------------------------------------------------')
                print(bloot_spacer + DC.BRACKET + "[" + DC.HANDLE +"@" + embedded_handle + DC.BRACKET +"] " + 
                      DC.DISPLAY_NAME + embedded_displayName + DC.BASIC + ":" + DC.CLEAR)
                print(bloot_spacer + DC.POST + embedded_text.strip())
                print(DC.DIVIDER + bloot_spacer + '--------------------------------------------------------------')
                bloot_spacer = ""

            if (i.get('post').get('embed').get('$type') == "app.bsky.embed.external#view"):
                bloot_spacer = "   " # spacer to ident embedded post
                embedded_description = i.get('post').get('embed').get('external').get('description')
                embedded_title = i.get('post').get('embed').get('external').get('title')
                embedded_uri = i.get('post').get('embed').get('external').get('uri')

                print('')
                print(DC.DIVIDER + bloot_spacer + '--------------------------------------------------------------')
                print(bloot_spacer + DC.POST + embedded_description.strip())
                print(bloot_spacer + DC.POST + embedded_title.strip())
                print(bloot_spacer + DC.POST + embedded_uri.strip())
                print(DC.DIVIDER + bloot_spacer + '--------------------------------------------------------------')
                bloot_spacer = ""

        # print did and rkey. needed for delete (if your record) or reply
        print(bloot_spacer + DC.IDS + bloot_did + " " + bloot_rkey)

        print(bloot_spacer + DC.PAREN + "(" + 
              DC.REPLY + "Reply" + DC.BASIC + ": " + DC.BASIC_LIGHT + bloot_replyCount + " " +
              DC.REPOST + "Repost" + DC.BASIC + ": " + DC.BASIC_LIGHT + bloot_repostCount + " " +
              DC.LIKE + "Like" + DC.BASIC + ": " + DC.BASIC_LIGHT + bloot_likeCount + 
              DC.PAREN + ")")  

        print('')
        
    print(DC.DIVIDER + "=================================================================")

    #dump_json(i)

    print("\n") 

    
