#!/usr/bin/python3
#The above line needs to be the first line.  When you chmod the file to an executable and
#add this line, you can run the file without putting python3 in front of the file.
#Example: ./pBsky -p "This is a test."

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
import argparse
import configparser
import re
import json

#Colors for Display
class bColors:
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

#Parse the passed arguments
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
                    help='follow a user witha given username')
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
# Usage (Post Something): ./pBsky.py -p {post_text}
#
#We want to post something 
if (args.post != None):
    session.postBloot(args.post)
    # Image Example: session.post_bloot("here's an image!", "path/to/your/image")

#
# REPLY
# Usage (Reply to Something): ./pBsky.py -r "This is my reply" {rkey}
#
#We want to reply to something first_post
if (args.reply != None):

    #Build the at_uri based on the did and rkey
    at_uri = "at://did:plc:" + args.reply[1] + "/app.bsky.feed.post/" + args.reply[2]

    #Get the post.
    original_post = session.getBlootByUrl(at_uri).json().get('posts')

    #Need to create a dictionary to pass as the reply details.
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

    #Post
    session.postBloot(args.reply[0], reply_to=reply_ref)

#
# DELETE
# Usage (Delete Something): ./pBsky.py -d {did} {rkey}
#
#We want to post something 
if (args.delete != None):
    session.deleteBloot(args.delete[0], args.delete[1])

#
# FOLLOW
# Usage (Follow Someone): ./pBsky.py -f {username - without the @}
#
#We want to follow someone 
if (args.follow != None):
    session.follow(username=args.follow)

#
# GET
# Usage (Get Following Timeline + Max Count): ./pBsky.py -g 10
# Usage (Get Specific Timeline + Max Count):  ./pBsky.py -g davidcarryer.com 10
# 
#We want to get last posts for a user..get('post').get('record').get('text')
if (args.get != None):

    #Will grab the 'following' timeline when a number is specified.
    if (args.get[0].isnumeric()):
        skyline = session.getSkyline(args.get[0]) #defaults to 10
        feed = skyline.json().get('feed')
    else:
        #Will grab the timeline of a specific user.
        skyline = session.getLatestNBloots(args.get[0], args.get[1]).content
        feed = json.loads(skyline).get('feed')

    print("\n") #Just some padding.

    for i in feed:
        bloot_text = str(i.get('post').get('record').get('text'))
        bloot_displayName = str(i.get('post').get('author').get('displayName'))
        bloot_did = str(i.get('post').get('author').get('did')[8:])
        bloot_rkey = str(i.get('post').get('uri')).split("/")[-1]
        bloot_handle = str(i.get('post').get('author').get('handle'))
        bloot_replyCount = str(i.get('post').get('replyCount'))
        bloot_repostCount = str(i.get('post').get('repostCount'))
        bloot_likeCount = str(i.get('post').get('likeCount'))
        bloot_uri = str(i.get('post').get('uri'))

        #Trying to figure out of this is a reply.
        bloot_reply = str(i.get('post').get('record').get('reply'))
        if (bloot_reply != "None"):
            bloot_reply_uri = str(i.get('post').get('record').get('reply').get('parent').get('uri'))
            ret_json = session.getBlootByUrl(bloot_reply_uri).json().get('posts')
            bloot_response_author_handle = str(ret_json[0].get('author').get('displayName'))

        #Trying to figure out if this is a repost.
        bloot_reason = str(i.get('reason'))
        if (bloot_reason != "None"):
            bloot_repost_author_displayName = str(i.get('reason').get('by').get('displayName'))

        #The main text is full of newlines, etc.  Strip them all.
        re.sub('[\W_]+',' ',bloot_text) #strip everyting but letters and characters
        bloot_text = ''.join(bloot_text.split('\n')) #string new lines

        print(bColors.DIVIDER + "-----------------------------------------------------------------")

        if (bloot_reply != "None"): #red
            print(bColors.REPLY_TO + "< Reply to " + bloot_response_author_handle + bColors.CLEAR)

        if (bloot_reason != "None"): #orange
            print(bColors.REPOSTED_BY + "+ Reposted by " + bloot_repost_author_displayName + bColors.CLEAR)

        print(bColors.BRACKET + "[" + bColors.HANDLE +"@" + bloot_handle + bColors.BRACKET +"] " + 
            bColors.DISPLAY_NAME + bloot_displayName + bColors.BASIC + ":" + bColors.CLEAR) 
        print(bColors.POST + bloot_text.strip())

        #print did and rkey. needed for delete (if your record) or reply
        print(bColors.IDS + bloot_did + " " + bloot_rkey)

        print(bColors.PAREN + "(" + 
            bColors.REPLY + "Reply" + bColors.BASIC + ": " + bColors.BASIC_LIGHT + bloot_replyCount + " " +
            bColors.REPOST + "Repost" + bColors.BASIC + ": " + bColors.BASIC_LIGHT + bloot_repostCount + " " +
            bColors.LIKE + "Like" + bColors.BASIC + ": " + bColors.BASIC_LIGHT + bloot_likeCount + 
            bColors.PAREN + ")")
        
    print(bColors.DIVIDER + "-----------------------------------------------------------------")

    print("\n") #Just some padding.
