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
parser.add_argument('-p', '--post', type=str,
                    help='create a post from the given string.')
parser.add_argument('-d', '--delete', nargs=2,
                    help='delete a post with given did and rkey.')
parser.add_argument('-g', '--get', nargs='*',
                    help='get your last n posts (default 10) or another users last n posts.')
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
if (args.post != None):
    session.post_bloot(args.post)
    # Image Example: session.post_bloot("here's an image!", "path/to/your/image")

#
# DELETE
# Usage (Delete Something): ./pBsky.py delete {did} {rkey}
#
#We want to post something 
if (args.delete != None):
    session.delete_bloot(args.delete[0], args.delete[1])

#
# GET
# Usage (Get Following Timeline + Max Count): ./pBsky.py get 10
# Usage (Get Specific Timeline + Max Count):  ./pBsky.py get davidcarryer.com 10
# 
#We want to get last posts for a user..get('post').get('record').get('text')
if (args.get != None):

    #Will grab the 'following' timeline when a number is specified.
    if (args.get[0].isnumeric()):
        skyline = session.get_skyline(args.get[0]) #defaults to 10
        feed = skyline.json().get('feed')
    else:
        #Will grab the timeline of a specific user.
        skyline = session.get_latest_n_bloots(args.get[0], args.get[1]).content
        feed = json.loads(skyline).get('feed')

    print("\n") #Just some padding.

    for i in feed:
        bloot_text = i.get('post').get('record').get('text')
        bloot_cid = str(i.get('post').get('cid'))
        bloot_displayName = i.get('post').get('author').get('displayName')
        bloot_did = i.get('post').get('author').get('did')
        bloot_did = bloot_did[8:]
        bloot_rkey = str(i.get('post').get('uri')).split("/")[-1]
        bloot_handle = i.get('post').get('author').get('handle')
        bloot_replyCount = str(i.get('post').get('replyCount'))
        bloot_repostCount = str(i.get('post').get('repostCount'))
        bloot_likeCount = str(i.get('post').get('likeCount'))

        re.sub('[\W_]+',' ',bloot_text) #strip everyting but letters and characters
        bloot_text = ''.join(bloot_text.split('\n')) #string new lines
        
        #I feel like there should be a better cleaner way to deal with colors. \033[0;90m etc.
        #This works just fine but it just looks messy in the code.

        print("\033[0;90m-----------------------------------------------------------------")

        print("\033[0;93m[\033[0;0m\033[38;5;159m@" + bloot_handle + "\033[0;93m] \033[1;96m" + bloot_displayName + "\033[1;97m:\n" + 
                "\033[0;0m\033[38;5;2m" + bloot_text.strip() + "\n"
                "\033[38;5;236m" + bloot_did + " " + bloot_rkey + "\n"
                "\033[0;93m(" + 
                "\033[0;36mReply\033[0;97m: \033[0;37m" + bloot_replyCount + " " +
                "\033[0;36mRepost\033[0;97m: \033[0;37m" + bloot_repostCount + " " +
                "\033[0;36mLike\033[0;97m: \033[0;37m" + bloot_likeCount + 
                "\033[0;93m)")
        
    print("\033[0;90m-----------------------------------------------------------------")

    print("\n") #Just some padding.
