#!/usr/bin/python3
#The above line needs to be the first line.  When you chmod the file to an executable and
#add this line, you can run the file without putting python3 in front of the file.
#Example: ./pBsky post "This is a test."

####################################################
# Author: David Carryer 
# Email: david@davidcarryer.com
# Bluesky: @davidcarryer.com
#
# Uses atprototools for bSky Interopability.
# https://github.com/ianklatzco/atprototools
#
####################################################

#Do my imports
from atprototools import Session
import os
import argparse
import configparser
import re
import json

#Parse the passed arguments
parser = argparse.ArgumentParser(
    prog='pBsky',
    description='Comand line BlueSky client for Linux.')
parser.add_argument('action')
parser.add_argument('details') 
parser.add_argument('more', nargs='?', const=1, type=str)
args = parser.parse_args()

#Open the INI for authentication information.
config = configparser.ConfigParser()
config.read('pBsky.ini')
USERNAME = config['AUTHENTICATION']['USERNAME'] 
PASSWORD = config['AUTHENTICATION']['PASSWORD'] 

#Establish the session
session = Session(USERNAME, PASSWORD)

#
# POST
# Usage (Post Something): ./pBsky.py post {post_text}
#
#We want to post something 
if (args.action.lower() == "post"):
    session.post_bloot(args.details)
    # Image Example: session.post_bloot("here's an image!", "path/to/your/image")

#
# DELETE
# Usage (Delete Something): ./pBsky.py delete {did} {rkey}
#
#We want to post something 
if (args.action.lower() == "delete"):
    session.delete_bloot(args.details, args.more)

#
# GET
# Usage (Get Following Timeline + Max Count): ./pBsky.py get 10
# Usage (Get Specific Timeline + Max Count):  ./pBsky.py get davidcarryer.com 10
# 
#We want to get last posts for a user..get('post').get('record').get('text')
if (args.action.lower() == "get"):

    #Will grab the 'following' timeline when a number is specified.
    if (args.details.isnumeric()):
        skyline = session.get_skyline(args.details) #defaults to 10
        feed = skyline.json().get('feed')
    else:
        #Will grab the timeline of a specific user.
        skyline = session.get_latest_n_bloots(args.details,args.more).content
        feed = json.loads(skyline).get('feed')

    print("\n") #Just some padding.

    for i in feed:
        bloot_text = str(i.get('post').get('record').get('text'))
        bloot_cid = str(i.get('post').get('cid'))
        bloot_displayName = str(i.get('post').get('author').get('displayName'))
        bloot_did = str(i.get('post').get('author').get('did'))
        bloot_did = str(bloot_did[8:])
        bloot_rkey = str(i.get('post').get('uri')).split("/")[-1]
        bloot_handle = str(i.get('post').get('author').get('handle'))
        bloot_replyCount = str(i.get('post').get('replyCount'))
        bloot_repostCount = str(i.get('post').get('repostCount'))
        bloot_likeCount = str(i.get('post').get('likeCount'))

        #Trying to figure out of this is a reply.
        bloot_reply = str(i.get('post').get('record').get('reply'))
        if (bloot_reply != "None"):
            bloot_reply_uri = str(i.get('post').get('record').get('reply').get('parent').get('uri'))
            ret_json = session.get_bloot_by_url(bloot_reply_uri).json().get('posts')
            bloot_response_author_handle = str(ret_json[0].get('author').get('displayName'))

        #Trying to figure out if this is a repost.
        bloot_reason = str(i.get('reason'))
        if (bloot_reason != "None"):
            bloot_repost_author_displayName = str(i.get('reason').get('by').get('displayName'))

        #The main text is full of newlines, etc.  Strip them all.
        re.sub('[\W_]+',' ',bloot_text) #strip everyting but letters and characters
        bloot_text = ''.join(bloot_text.split('\n')) #string new lines
        
        #I feel like there should be a better cleaner way to deal with colors. \033[0;90m etc.
        #This works just fine but it just looks messy in the code.

        print("\033[0;90m-----------------------------------------------------------------")

        if (bloot_reply != "None"): #red
            print("\033[38;5;124m< Reply to " + bloot_response_author_handle + "\033[0;0m")

        if (bloot_reason != "None"): #orange
            print("\033[38;5;166m+ Reposted by " + bloot_repost_author_displayName + "\033[0;0m")

        print("\033[0;93m[\033[0;0m\033[38;5;159m@" + bloot_handle + "\033[0;93m] \033[1;96m" + bloot_displayName + "\033[1;97m:\n" + 
            "\033[0;0m\033[38;5;2m" + bloot_text.strip())

        #only print did and rkey if it's your own record that you can delete
        if (bloot_handle == USERNAME):
            print("\033[38;5;236m" + bloot_did + " " + bloot_rkey)

        print("\033[0;93m(" + 
            "\033[0;36mReply\033[0;97m: \033[0;37m" + bloot_replyCount + " " +
            "\033[0;36mRepost\033[0;97m: \033[0;37m" + bloot_repostCount + " " +
            "\033[0;36mLike\033[0;97m: \033[0;37m" + bloot_likeCount + 
            "\033[0;93m)")
        
    print("\033[0;90m-----------------------------------------------------------------")

    print("\n") #Just some padding.