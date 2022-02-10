# nft-stealer
Python script to Funge NFTs. It scrapes OpenSea for a given list of NFT collections and downloads a certain number of NFTs from each collection
or the entire collections.

# Installation:
    Python 2: "pip install -r requirements.txt"
    Python 3: "pip3 install -r requirements.txt"
## Linux:
    Run: "sudo apt-get install firefox"
    Before running, you must add the path to the current folder to the PATH variable (so that the program finds "geckodriver", needed by firefox)
    Adding to PATH: "export PATH=$PATH:/path/to/current/folder"

# Features:
- Download a certain amount N of NFTs from multiple collections;
- Controlled through the config file;
- Bypasses OpenSea's CloudFlare protection by simulating a headless web browser;

# To do:
- Implement the functionality of downloading the first N collections from the "Trending", "Top" and "Art" tabs on OpenSea;
- Make the download work on multiple threads;
- Improve logging;

# Usage:
    1. In the config file (confi.json), the "collections" key represents an array of all of the collections that you want to download. Change that array
however you like so that it contains only the names of the collections you want to download.
To find out the name of a NFT collection, visit its page on OpenSea and look at the URL.
Example: https://opensea.io/collection/hapeprime -> The name of the collection is "hapeprime". Whatever is after "/collection/" is the name of the collection
    2. Change the number of NFTs to be downloaded per collection however you like. If you give it the value "-1", it will download the entire collections;
    3. Run the script:
        Python 2: "python main.py"
        Python 3: "python3 main.py"
    4. Wait for the script to run, until it finishes. At the moment it is still a work in progress, so if there are any warnings, you can ignore them,
and if there are any errors, raise the issue on the GitHub repo.