# pBsky

Python based BlueSky Client for the Linux Command Line.  This is not intended to be an exhustive client.  Instead it serve's as an example use of the atprototools codebase.

Uses [atprototools](https://github.com/ianklatzco/atprototools) for bSky Interopability.

# Setup

Create a config file in the same directory as `pBsky.py` called `pBsky.ini`.
Edit the file with your bsky username and password:
```
[AUTHENTICATION]
USERNAME = your_username
PASSWORD = your_password
```

# Usage

Run the python script with `python3 pBsky.py --help`, or execute with `./pBsky.py --help` to see available options.

# TODO

Todo List:

- [ ] Error checking.
- [ ] Identify pics and insert a 'picture' placeholder.
- [ ] Identify embedded items.
- [ ] Need to figure out how to repost.
- [ ] Need to figure out like.
- [ ] Need to figure out follow.

# Extras

Tested on Ubuntu 22.04.2 LTS VM on a MacBook Pro with Python3

Original Author: David Carryer\
Email: david@davidcarryer.com\
Bluesky: @davidcarryer.com\
License: MIT
