# Author: David Carryer 
# Email: david@davidcarryer.com
# Bluesky: @davidcarryer.com
#
# Utilities to make python easier to code.

# Do my imports
import json
import re
from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import TerminalFormatter


# DUMP_JSON
# Function to pretty print json to the screen for debugging with color
def dump_json(j):
    json_str = json.dumps(j, indent=4, sort_keys=True)
    print(highlight(json_str, JsonLexer(), TerminalFormatter()))


# DUMP
# Simple function to print to the screen
def dump(d):
    print("\n")
    print("=========================================================")
    print(d)  
    print("=========================================================")
    print("\n")

# CLEAN
# Simple function to change complex text to simple text.
def clean(t):
    re.sub('[\W_]+',' ',t) # strip everyting but letters and characters
    t = ''.join(t.split('\n')) # strip out all the specific \n
    return t.strip()
