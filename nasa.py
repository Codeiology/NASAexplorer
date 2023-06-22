# Import dependencies

import requests
import os
import json
import sys
from PIL import Image
from io import BytesIO
import time
import signal
import textwrap

# Initialize KeyboardInterrupt handler

user_interrupt_occured = False
def user_interrupt(signal, frame):
    global user_interrupt_occured
    user_interrupt_occured = True
    print("")
    print("\033[1;31mProgram stopped.\033[0m")
    print("")
    sys.exit()
signal.signal(signal.SIGINT, user_interrupt)

# Initial setup process

if not os.path.exists('apikey.json'):
    print("***  NASA Explorer Inital Setup  ***")
    print("")
    print("This regularly accesses the NASA API to function.")
    print("You must register for an API key at https://api.nasa.gov/.")
    print("They will send you your API key in an email after you have registered.")
    print("")
    bongus = input("When you are ready, paste your API key here: ")
    print("")
    print("Saving for later as 'apikey.json'. Do not delete it.")
    var_val = {
        'api_key': f'{bongus}'
    }
    with open('apikey.json', 'w') as file:
        json.dump(var_val, file)
    print("Done! Exiting (Run the program again to boot with the API key defined)... ")
    sys.exit()
else:
    with open('apikey.json', 'r') as file:
        var_val = json.load(file)
        
# Register API key

global key
key = var_val['api_key']

# Initialize functions

def getrovermanifest(rover_name, sol=None):
    api_url = f"https://api.nasa.gov/mars-photos/api/v1/manifests/{rover_name}"
    params = {
        "api_key": key
    }

    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        manifest = response.json()
        if sol:
            filtered_entries = [
                entry for entry in manifest["photo_manifest"]["photos"]
                if entry["sol"] == sol
            ]
            manifest["photo_manifest"]["photos"] = filtered_entries
        return manifest
    else:
        print(f"Failed to retrieve manifest. Status code: {response.status_code}")
        return None
def getroverpics(sol, rover, cam):
    if cam == "all":
        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?sol={sol}&api_key={key}"
    else:
        url = f"https://api.nasa.gov/mars-photos/api/v1/rovers/{rover}/photos?sol={sol}&camera={cam}&api_key={key}"
    print("Fetching photos... ")
    response = requests.get(url)
    if response.status_code == 200:
        photos = response.json()
        return photos
    else:
        print(f"Failed to retrieve photos! Status code: {response.status_code}")
        return None
def getdatesnat():
    url = f"https://api.nasa.gov/EPIC/api/natural/available?api_key={key}"
    response = requests.get(url)
    if response.status_code == 200:
        dates = response.json()
        return dates
    else:
        print(f"Failed to fetch available dates. Status code: {response.status_code}")
        return None
def getdatesen():
    url = f"https://api.nasa.gov/EPIC/api/enhanced/available?api_key={key}"
    response = requests.get(url)
    if response.status_code == 200:
        dates = response.json()
        return dates
    else:
        print(f"Failed to fetch available dates. Status code: {response.status_code}")
        return None
def getimageidentnat(date):
    url = f"https://api.nasa.gov/EPIC/api/natural/date/{date}?api_key={key}"
    response = requests.get(url)
    if response.status_code == 200:
        images = response.json()
        return images
    else:
        print(f"Failed to fetch EPIC image. Status code: {response.status_code}")
        return None
def getimageidenten(date):
    url = f"https://epic.gsfc.nasa.gov/api/enhanced/date/{date}"
    response = requests.get(url)
    if response.status_code == 200:
        images = response.json()
        return images
    else:
        print(f"Failed to fetch EPIC image. Status code: {response.status_code}")
        return None
def print_data_values(json_data):
    if isinstance(json_data, list):
        for item in json_data:
            print_data_values(item)
    elif isinstance(json_data, dict):
        for k, v in json_data.items():
            if k == 'data':
                print(json.dumps(v, indent=4))
            else:
                print_data_values(v)
    else:
        pass

# Initiate interactive loop

while True:
    
# Clear screen

    os.system('cls' if os.name == 'nt' else 'clear')
    sys.stdout.write('\033[2J')
    sys.stdout.write('\033[H')
    sys.stdout.flush()

# Show logo and disclaimer

    print('''

  :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
  ::                                                     ::
  ::  The content within this program is property of:    ::
  ::                                                     ::
  ::  |\\    ||       /\\        ________        /\\        ::
  ::  ||\\   ||      //\\\      / _______>      //\\\       ::
  ::  || \\  ||     //  \\\    | <_______      //  \\\      ::
  ::  ||  \\ ||    //____\\\    \_______ \    //____\\\     ::
  ::  ||   \\||   //______\\\    _______> |  //______\\\    ::
  ::  ||    \\|  //        \\\  <________/  //        \\\   ::
  ::                                                     ::
  ::  The National Aeronautics & Space Administration    ::
  ::                                                     ::
  :::::::::::::::::::::::::::::::::::::::::::::::::::::::::
(ASCII art from Telehack)
(Press CTRL + C to exit at any time)

Coded by Codeiology on GitHub
''')
# Ask the user for which API to interact

    apichoices = '''
These modules are currently available:

1. Mars Rover pictures
2. NASA image and video library
3. EPIC (Earth Polychromatic Imaging Camera)
4. Astronomy Picture of the day
5. DONKI astronomy notifications
    '''
    print(apichoices)
    apichoice = input("Choose a number: ")
    print("")

    # UX for Mars rover pictures

    if apichoice == "1":
        manifor1 = input("Would you like to fetch a manifest or a picture? (manif/pic): ")
        print("")
        if manifor1 == "manif":
            print("Information for camera abbreviations and others can be found at https://api.nasa.gov/ under Mars Rover Photos")
            print("")
            rover = input("Rover name? ")
            rover1 = rover.upper()
            sol = int(input("Max sol? "))
            manifest = getrovermanifest(rover, sol)
            if manifest:
                print(f"Manifest for {rover} retreived successfully! ")
                print("")
                print(f"ROVER {rover1}")
                print("")
                print(f"Launch date: {manifest['photo_manifest']['launch_date']}")
                print(f"Landing date: {manifest['photo_manifest']['landing_date']}")
                if manifest['photo_manifest']['status'] == 'complete':
                    manifstatus = "\033[1;31mMISSION ENDED\033[0m"
                else:
                    manifstatus = manifest['photo_manifest']['status']
                print(f"Current status: {manifstatus}")
                print(f"Amount of Mars days online: {manifest['photo_manifest']['max_sol']}")
                print(f"Last online: {manifest['photo_manifest']['max_date']}")
                print(f"Photos taken: {manifest['photo_manifest']['total_photos']}")
                print(f"JSON value entry for inputted sol: {manifest['photo_manifest']['photos']}")
            else:
                print("Manifest for {rover} could not be found or was not retrieved correctly!")
        elif manifor1 == "pic":
            print("")
            print('''
Cameras:                                Rovers have that have them

Name:                                   Curiosity   Opportunity   Spirit   Perseverance
FHAZ (Front Hazard Avoidance Camera)    YES         YES           YES         
RHAZ (Rear Hazard Avoidance Camera)     YES         YES           YES
MAST (Mast Camera)                      YES         NO            NO
CHEMCAM (Chemistry and Camera Complex)  YES         NO            NO       (No camera specification for API
MAHLI (Mars Hand Lens Imager)           YES         NO            NO       supported yet. Just 'all'.)
MARDI (Mars Descent Imager)             YES         NO            NO
NAVCAM (Navigation Camera)              YES         YES           YES
PANCAM (Panoramic Camera)               NO          YES           YES
MINITES (Thermal Emission Spectrometer) NO          YES           YES

    ''')
            rover = input("Rover name? ").lower()
            sol = input("Max sol? (number): ")
            cam = input("Camera (Type, 'all' to show all cameras)? ").lower()
            picdatas = getroverpics(sol, rover, cam)
            if picdatas != None:
                print(f"Photos taken up to sol {sol} by rover {rover}: ")
                for picdata in picdatas["photos"]:
                    print(picdata["img_src"])
                while True:
                    viewurl = input("Image URL to view ('exit' to exit module): ")
                    if viewurl == "exit":
                        image.close()
                        break
                    else:
                        response = requests.get(viewurl)
                        image = Image.open(BytesIO(response.content))
                        image.show()
            else:
                print("\033[1;31mNo images found for your query!\033[0m")
        else:
            print("Invalid.")
            
    # UX for Imange and Video library searcher
            
    elif apichoice == "2":
        print("")
        print("NASA Image and Video Library")
        print("")
        print("Search all images and videos!")
        print("")
        while True:
            query1 = input("Search query ('exit' to exit module): ")
            query = query1.replace(" ", "+")
            if query1 == "exit":
                break
            else:
                searchurl = f"https://images-api.nasa.gov/search?q={query}"
                response = requests.get(searchurl)
                results = response.json()
                if response.status_code == 200:
                    for collection in results.get('collection', {}).get('items', []):
                        for item in collection.get('data', []):
                            print(json.dumps(item, indent=4))
                        for item in collection.get('links', []):
                            print(json.dumps(item, indent=4))
                else:
                    print(f"Failed to get search results. Status code: {response.status_code}")
        
    # UX for EPIC

    elif apichoice == "3":
        print("")
        print("EPIC Library")
        print("")
        natoren = input("View natural photos, or enhanced photos? (nat/en): ")
        if natoren == "nat":
            print("Fetching dates...")
            dates = getdatesnat()
            if dates is not None:
                print(dates)
                mostrecent = input("Choose a date: ")
                mostrecent1 = mostrecent.replace("-", "/")
                print(f"Most recent date: {mostrecent}")
                images = getimageidentnat(mostrecent)
                if images:
                    for image in images:
                        print(f"https://epic.gsfc.nasa.gov/archive/natural/{mostrecent1}/png/{image['image']}.png")
                    while True:
                        imgurl = input("URL to view ('exit' to exit module): ")
                        if imgurl == "exit":
                            image.close()
                            break
                        else:
                            response = requests.get(imgurl)
                            image = Image.open(BytesIO(response.content))
                            image.show()
                else:
                    print("No URLs found.")
            else:
                print("No dates found. No b**ches! ")
        elif natoren == "en":
            print("Fetching dates...")
            dates = getdatesen()
            if dates is not None:
                print(dates)
                mostrecent = input("Choose a date: ")
                mostrecent1 = mostrecent.replace("-", "/")
                print(f"Most recent date: {mostrecent}")
                images = getimageidenten(mostrecent)
                if images:
                    for image in images:
                        print(f"https://epic.gsfc.nasa.gov/archive/enhanced/{mostrecent1}/png/{image['image']}.png")
                    while True:
                        imgurl = input("URL to view ('exit' to exit module): ")
                        if imgurl == "exit":
                            image.close()
                            break
                        else:
                            response = requests.get(imgurl)
                            image = Image.open(BytesIO(response.content))
                            image.show()
                else:
                    print("No URLs found.")
            else:
                print("No dates found. No b**ches! ")

    # UX for APOD

    elif apichoice == "4":
        print("")
        print("APOD (Astronomy Picture Of the Day)")
        print("")
        print("Scanning for today's APOD...")
        url = f"https://api.nasa.gov/planetary/apod?api_key={key}"
        response = requests.get(url)
        apod = response.json()
        if response.status_code == 200:
            print("")
            print(apod['title'])
            print(f"\033[2;39m{apod['date']}\033[0m")
            print("")
            desc = textwrap.fill(apod['explanation'])
            print(desc)
            print("")
            print(apod['url'])
            copyright1 = apod['copyright'].replace('\n', '')
            copyright = copyright1.replace('\u00e0', '')
            print(f"\033[2;39mCopyright: {copyright}\033[0m")
            print("")
            response = requests.get(apod['url'])
            image = Image.open(BytesIO(response.content))
            input("Hit enter to show picture...")
            image.show()
        else:
            print(f"Failed to retrive APOD. Status code: {response.status_code}")

    # UX for DONKI
    
    elif apichoice == "5":
        print("")
        print("DONKI")
        print("")
        startdate = input("Start day (YYYY-MM-DD) for notifications: ")
        endate = input("End day (YYYY-MM-DD) for notifications: ")
        print("")
        print("Fetching DONKI notifications...")
        print("")
        url = f"https://api.nasa.gov/DONKI/notifications?startDate={startdate}&endDate={endate}&type=all&api_key={key}"
        response = requests.get(url)
        notifs = response.json()
        for notif in notifs:
            print("██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████")
            print("")
            print(f"Issue type: {notif['messageType']}")
            print(f"Message ID: {notif['messageID']}")
            print(f"URL: {notif['messageURL']}")
            print(f"Time Issued: {notif['messageIssueTime']}")
            print("")
            desc = textwrap.fill(notif['messageBody'], width=150, replace_whitespace=False) # Adjust the width to fit your terminal!
            print(desc)
        print("██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████")
        print("\n\n\n")
        input("Hit enter to continue...")

# End it with the handler ;)

if user_interrupt_ocurred:
    sys.exit(0)
