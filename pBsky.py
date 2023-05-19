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
    FOLLOWS = '\033[0;36m'
    FOLLOWERS = '\033[0;36m'
    POSTS = '\033[0;36m'
    IDS = '\033[38;5;236m'
    POST = '\033[38;5;65m' 
    POST_BRIGHT = '\033[38;5;10m' 
    DIVIDER = '\033[0;90m'
    REPLY_BAR = '\033[0;90m'
    IMAGE = '\033[38;5;228m'
    IMAGE_BRACKET = '\033[38;5;220m'

##########################################################################################
#
# Core Skeeting Functions
#
##########################################################################################

#
# Defining main function
#
def main():
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

    # Get Profile
    if (args.getprofile != None):
        get_profile(session,
                    args.getprofile) #handle

    # Post a Skeet
    if (args.post != None):
        post_skeet(session,
                   args.post) #text to post

    # Reply to Skeet
    if (args.reply != None):
        reply_to_skeet(session,
                       args.reply[0], #text to post
                       args.reply[1], #did
                       args.reply[2]) #rkey
    
    # Delete Skeet
    if (args.delete != None):
        delete_skeet(session,
                     args.delete[0], #did
                     args.delete[1]) #rkey

    # Follow Handle
    if (args.follow != None):
        follow_handle(session,
                      args.follow) #handle

    # Get Skeets    
    if (args.get != None):
        if (args.get[0].isnumeric()):
            get_skeets(session,
                       args.get[0], #count
                       "") #placeholder
        else:
            get_skeets(session,
                       args.get[0], #handle
                       args.get[1]) #count           

#
# Define get_profile function
#
def get_profile(my_session,user_name):
    profile = my_session.get_profile(username=user_name)
    loaded_json = profile.json()

    profile_did = str(loaded_json.get('did'))
    profile_handle = str(loaded_json.get('handle'))
    profile_displayName = str(loaded_json.get('displayName'))
    profile_description = clean(str(loaded_json.get('description')))
    profile_followsCount = str(loaded_json.get('followsCount'))
    profile_followersCount = str(loaded_json.get('followersCount'))
    profile_postsCount = str(loaded_json.get('postsCount'))
    profile_labels = str(loaded_json.get('labels'))

    print_fat_divider()
    print_handle_bar(profile_handle,profile_displayName)
    print_profile_description(profile_description)
    print_profile_labels(profile_labels)
    print_did_rkey(profile_did,"")
    print_follows_followers_posts_bar(profile_followsCount,profile_followersCount,profile_postsCount)
    print_fat_divider()     

#
# Define post_skeet
#
def post_skeet(my_session,skeet_text):
    my_session.postBloot(skeet_text)

#
# Define reply_to_skeet
#
def reply_to_skeet(my_session,skeet_text,did,rkey):
    at_uri = "at://did:plc:" + did + "/app.bsky.feed.post/" + rkey
    original_post = my_session.getBlootByUrl(at_uri).json().get('posts')
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
    my_session.postBloot(skeet_text, reply_to=reply_ref)

#
# Define delete_skeet
#
def delete_skeet(my_session,did,rkey):
    my_session.deleteBloot(did, rkey)   

#
# Define follow_handle
#
def follow_handle(my_session,handle):
    my_session.follow(username=handle)

#
# Define get_skeets
#
def get_skeets(my_session,arg0,arg1):
    # Will grab the 'following' timeline when a number is specified.
    if (arg0.isnumeric()):
        # Get some skeets
        skyline = my_session.getSkyline(arg0) 
        feed = skyline.json().get('feed')
    else:
        # Will grab the timeline of a specific user.
        skyline = my_session.getLatestNBloots(arg0, arg1).content
        feed = json.loads(skyline).get('feed')

    # Print divider
    print_fat_divider()

    for i in feed:
        # Capture all the individual elements that make up a post
        bloot_text = clean(str(i.get('post').get('record').get('text')))
        bloot_displayName = str(i.get('post').get('author').get('displayName'))
        bloot_did = str(i.get('post').get('author').get('did')[8:])
        bloot_rkey = str(i.get('post').get('uri')).split("/")[-1]
        bloot_handle = str(i.get('post').get('author').get('handle'))
        bloot_replyCount = str(i.get('post').get('replyCount'))
        bloot_repostCount = str(i.get('post').get('repostCount'))
        bloot_likeCount = str(i.get('post').get('likeCount'))           

        # > Reply to ...
        if (str(i.get('post').get('record').get('reply')) != "None"):
            bloot_reply_uri = str(i.get('post').get('record').get('reply').get('parent').get('uri'))
            ret_json = my_session.getBlootByUrl(bloot_reply_uri).json().get('posts')
            bloot_response_author_handle = str(ret_json[0].get('author').get('displayName'))
            print_reply_to(bloot_response_author_handle)

            orig_bloot_text = clean(str(i.get('reply').get('parent').get('record').get('text')))
            orig_bloot_displayName = str(i.get('reply').get('parent').get('author').get('displayName'))
            orig_bloot_handle = str(i.get('reply').get('parent').get('author').get('handle'))
            orig_bloot_did = str(i.get('reply').get('parent').get('author').get('did')[8:])
            orig_bloot_uri = str(i.get('reply').get('parent').get('uri')).split("/")[-1]
            orig_bloot_replyCount = str(i.get('reply').get('parent').get('replyCount'))
            orig_bloot_repostCount = str(i.get('reply').get('parent').get('repostCount'))
            orig_bloot_likeCount = str(i.get('reply').get('parent').get('likeCount'))
            orig_bloot_anyEmbedded = str(i.get('reply').get('embed'))

            # Display the name and handle
            print_handle_bar(orig_bloot_handle,orig_bloot_displayName)
            
            # print the skeet
            print_original_skeet(orig_bloot_text)

            # any embedded images
            if (orig_bloot_anyEmbedded != "None"): 
                if (i.get('post').get('embed').get('$type') == "app.bsky.embed.images#view"):
                    orig_bloot_images = i.get('post').get('embed').get('images')

                    for j in orig_bloot_images:
                        orig_bloot_image_alt = j.get('alt')
                        if (orig_bloot_image_alt == ''):
                            orig_bloot_image_alt = "No alt text provided."
                        print(DC.IMAGE_BRACKET + "[" + DC.IMAGE + "Embedded Image" + 
                              DC.BASIC +  ": " + orig_bloot_image_alt + DC.IMAGE_BRACKET + "]")  

            # Did and Uri
            print_did_uri(orig_bloot_did,orig_bloot_uri)

            # Reply, Repost, and Like bar
            print_reply_repost_like_bar(orig_bloot_replyCount,orig_bloot_repostCount,orig_bloot_likeCount)

            # Print reply connector
            print_reply_connector_line()

        # + Reposted by ...
        if (str(i.get('reason')) != "None"):
            bloot_repost_author_displayName = str(i.get('reason').get('by').get('displayName'))
            print_reposted_by(bloot_repost_author_displayName)

        # Display name and Handle
        print_handle_bar(bloot_handle,bloot_displayName)

        # Text from Skeet
        print_skeet(bloot_text)

        # Anything embedded?
        if (str(i.get('post').get('embed')) != "None"): 

            # Embedded images found
            if (i.get('post').get('embed').get('$type') == "app.bsky.embed.images#view"): 
                bloot_images = i.get('post').get('embed').get('images')
                print_embedded_images(bloot_images)

            # Embedded repost found
            if (i.get('post').get('embed').get('$type') == "app.bsky.embed.record#view"):
                embedded_text = clean(str(i.get('post').get('embed').get('record').get('value').get('text')))
                embedded_displayName = i.get('post').get('embed').get('record').get('author').get('displayName')
                embedded_handle = i.get('post').get('embed').get('record').get('author').get('handle')
                print_embedded_post(embedded_handle,embedded_displayName,embedded_text)

            # Embedded website found
            if (i.get('post').get('embed').get('$type') == "app.bsky.embed.external#view"):
                embedded_description = clean(str(i.get('post').get('embed').get('external').get('description')))
                embedded_title = clean(str(i.get('post').get('embed').get('external').get('title')))
                embedded_uri = i.get('post').get('embed').get('external').get('uri')
                print_embedded_website(embedded_title,embedded_description,embedded_uri)

        # Display the did and rkey
        print_did_rkey(bloot_did,bloot_rkey)

        # Reply, Repost, and Like bar
        print_reply_repost_like_bar(bloot_replyCount,bloot_repostCount,bloot_likeCount)
        
        # Print divider
        print_fat_divider()



##########################################################################################
#
# Print Functions
#
##########################################################################################

#
# Define print_fat_divider
#
def print_fat_divider(spacer=""):
    print(spacer + DC.DIVIDER + "=================================================================")

#
# Define print_thin_divider
#
def print_thin_divider(spacer=""):
    print(spacer + DC.DIVIDER + "-----------------------------------------------------------------")

#
# Define print_profile_desription
#
def print_profile_description(description):
    print(DC.BASIC + description)

#
# Define print_handle_bar
#
def print_handle_bar(handle,displayName):
    print(DC.BRACKET + "[" + DC.HANDLE +"@" + handle + DC.BRACKET +"] " + 
          DC.DISPLAY_NAME + displayName + DC.BASIC + ":" + DC.CLEAR)

#
# Define print_profile_labels
#
def print_profile_labels(labels):
    if (labels!="[]"):
        print(DC.BASIC_LIGHT + "Labels: " + labels)  

#
# Define print_follows_followers_posts
#
def print_follows_followers_posts_bar(followsCount,followersCount,postsCount):
    print(DC.PAREN + "(" + 
          DC.FOLLOWS + "Follows" + DC.BASIC + ": " + DC.BASIC_LIGHT + followsCount + " " +
          DC.FOLLOWERS + "Followers" + DC.BASIC + ": " + DC.BASIC_LIGHT + followersCount + " " +
          DC.POSTS + "Posts" + DC.BASIC + ": " + DC.BASIC_LIGHT + postsCount + 
          DC.PAREN + ")")  
    
#
# Define print_follows_followers_posts
#
def print_reply_repost_like_bar(replyCount,repostCount,likeCount):
    print(DC.PAREN + "(" + 
          DC.REPLY + "Reply" + DC.BASIC + ": " + DC.BASIC_LIGHT + replyCount + " " +
          DC.REPOST + "Repost" + DC.BASIC + ": " + DC.BASIC_LIGHT + repostCount + " " +
          DC.LIKE + "Like" + DC.BASIC + ": " + DC.BASIC_LIGHT + likeCount + 
          DC.PAREN + ")")  
    
#
# Define print_reposted_by
#
def print_reposted_by(displayName):
    print(DC.REPOSTED_BY + "+ Reposted by " + displayName + DC.CLEAR)

#
# Define print_reply_to
#
def print_reply_to(handle):
    print(DC.REPLY_TO + "< Reply to " + handle + DC.CLEAR)

#
# Define print_did_rkey
#  
def print_did_rkey(did,rkey):
    print(DC.IDS + did + " " + rkey) 

#
# Define print_did_uri
#  
def print_did_uri(did,uri):
    print(DC.IDS + did + " " + uri) 

#
# Define print_reply_connector_line
#
def print_reply_connector_line():
    print(DC.REPLY_BAR + " | ")
    print(DC.REPLY_BAR + " | ")
    print(DC.REPLY_BAR + " | ")

#
# Define print_skeet
#
def print_skeet(skeet):
    print(DC.POST_BRIGHT + skeet)

#
# Define print_original_skeet
#
def print_original_skeet(skeet):
    print(DC.POST + skeet)

#
# Define print_embedded_images
#
def print_embedded_images(images):
    spacer = "   "
    for image_in_list in images:
        bloot_image_alt = image_in_list.get('alt')
        if (bloot_image_alt == ''):
            bloot_image_alt = "No alt text provided."
        print(spacer + DC.IMAGE_BRACKET + "[" + DC.IMAGE + "Embedded Image" + 
              DC.BASIC +  ": " + bloot_image_alt + DC.IMAGE_BRACKET + "]") 

#
# Define print_embedded_post
#
def print_embedded_post(handle,displayName,text):
    spacer = "   "
    print_thin_divider(spacer)
    print(spacer + DC.BRACKET + "[" + DC.HANDLE +"@" + handle + DC.BRACKET +"] " + 
          DC.DISPLAY_NAME + displayName + DC.BASIC + ":" + DC.CLEAR)
    print(spacer + DC.POST + text)
    print_thin_divider(spacer)

#
# Define print_embedded_website
#
def print_embedded_website(title,description,uri):
    spacer = "   "
    print_thin_divider(spacer)
    print(spacer + DC.POST + "[" + title + "] " + description + uri)
    print_thin_divider(spacer)



##########################################################################################
#
# Main Function
#
##########################################################################################

#
# Using the special variable 
# __name__
if __name__=="__main__":
    main()