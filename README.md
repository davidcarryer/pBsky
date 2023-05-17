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
```
POST: ./pBsky.py -p "{post_text}"
REPLY: ./pBsky.py -r "This is my reply" {rkey}
DELETE: ./pBsky.py -d {did} {rkey}
FOLLOW: ./pBsky.py -f {username - without the @}
GET (Your Following): ./pBsky.py -g {return count}
GET (Specific Account): ./pBsky.py -g {username - without the @} {return count}
GET PROFILE (Specific Account): ./pBsky.py -gp {username - without the @}
```

# TODO

Todo List:
=======
- [ ] Error checking.
- [ ] Display reposts with a quote.
- [ ] Like.

# Extras

- Tested on Ubuntu 22.04.2 LTS VM on a MacBook Pro with Python3
- Best efforts made to align with PEP 8 – Style Guide for Python Code

Original Author: David Carryer\
Email: david@davidcarryer.com\
Bluesky: @davidcarryer.com\
License: MIT
