import requests
import random
import string


url = "http://127.0.0.1:5000/signup"


# List of usernames to use
usernames = [
    "blackmolecule",
    "carvedcontinued",
    "gatechuffer",
    "glazedkosher",
    "cutaffect",
    "nethertwinkling",
    "lakescopyright",
    "beetrootscoal",
    "buriedindication",
    "flowerpotprayer",
    "jacksurprise",
    "nuggetcomedy",
    "impalingpossess",
    "yellowjudgmental",
    "fossiljellyfish",
    "lilyhost",
    "nautilusobstinacy",
    "roseequatorial",
    "taigaprovision",
    "bottleadjoining",
    "hutchirp",
    "snowfoot",
    "lilypaddeclare",
    "lecternillfated",
    "minecraftthaw",
    "kelplabor",
    "smokerbandanna",
    "bonemealhaunting",
    "beefhomework",
    "leverplumber",
    "arthropodsvia",
    "eyestill",
    "icerubbery",
    "villagermay",
    "mushroomthirsty",
    "notemoth",
    "structurecourteous",
    "jigsawincident",
    "spawnselection",
    "birchwoodlazy",
    "terracottaillustrate",
    "poweredweirdo",
    "granitesplit",
    "polarcheat",
    "flinttowards",
    "sprucesolve",
    "tundraamused",
    "blocksfollowing",
    "outpostmutant",
    "crackedkayaking"
]




for i in range(100):
    # Generate a random username and password
    username2 = random.choice(usernames) + str(random.randint(0,9999))
    password2 = ''.join(random.choices(string.ascii_uppercase + str(random.randint(0,9999)), k=8))
    
    # Send a POST request to create the account
    data = {'username': username2, 'password': password2, 'confirm_password': password2}
    response = requests.post(url, data=data)
    
    if response.status_code == 200:
        print(f"Successfully created account for {username2}")
        #users.append([data['username'], data['password']])
        
        
        
    else:
        print(f"Failed to create account for {username2}")
        

