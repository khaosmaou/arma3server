#!/usr/bin/python3

# MIT License
#
# Copyright (c) 2017 Marcel de Vries
# Copyright (c) 2021 Christopher Suttles
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import os.path
import re
import shutil
import time

from datetime import datetime
from urllib import request

# region Configuration
STEAM_CMD = "/home/arma3server/.steam/steamcmd/steamcmd.sh"
STEAM_USER = '$STEAM_USER'
STEAM_PASS = '$STEAM_PASS'

A3_SERVER_ID = "233780"
A3_SERVER_DIR = "/home/arma3server/serverfiles"
A3_WORKSHOP_ID = "107410"

A3_WORKSHOP_DIR = "{}/steamapps/workshop/content/{}".format(A3_SERVER_DIR, A3_WORKSHOP_ID)
A3_MODS_DIR = "/home/arma3server/serverfiles/mods"
A3_KEYS_DIR = "/home/arma3server/serverfiles/keys"

MODPACK_NAME = "ANON Operations Liberation"
MODPACK_PATH = "/home/arma3server/modpack.html"
MODS = {
    "@cba":                             "450814997",
    "@ace":                             "463939057",
    "@jbad":                            "520618345",
    "@lythium":                         "909547724",
    "@project_opfor":                   "735566597",
    "@rhs_usaf":                        "843577117",
    "@rhs_afrf":                        "843425103",
    "@rhs_gref":                        "843593391",
    "@ace_compat_rhs_usaf":             "773125288",
    "@ace_compat_rhs_afrf":             "773131200",
    "@ace_compat_rhs_gref":             "884966711",
    "@jbad_compat_legacy":              "2442475820",
    "@acre":                            "751965892",
    "@ragdoll_physics":                 "2290838143",
    "@ace_menu_expansion":              "1376867375",
    "@gruppe_adler_trenches":           "1224892496",
    "@advanced_rappelling":             "713709341",
    "@advanced_urban_rappelling":       "730310357",
    "@advanced_towing":                 "639837898",
    "@advanced_sling_loading":          "615007497",
    "@breaching_charge":                "1314910827",
    "@realistic_autopilots":            "1439605692",
    "@immerse":                         "825172265",
    "@suppress":                        "825174634",
    "@enhanced_movement":               "333310405",
    "@enhanced_movement_rework":        "2034363662",
    "@jsrs_soundmod":                   "861133494",
    "@jsrs_soundmod_compat_rhs_usaf":   "1180533757",
    "@jsrs_soundmod_compat_rhs_afrf":   "945476727",
    "@jsrs_soundmod_compat_rhs_gref":   "1180534892",
    "@jsrs_soundmod_reloading":         "1429098683",
    "@enhanced_soundscape":             "825179978",
    "@salmon_buttstroke":               "1528883208",
    "@advanced_weapon_mounting":        "1436537928",
    "@dzn_rifle_tripod":                "1720595785",
    "@dzn_mg_tripod":                   "1713801249",
    "@dzn_mg_tripod_compat_rhs":        "1947836596",
    "@dzn_animeme_face":                "1620525773",
    "@bettir":                          "2260572637",
    "@fawks_enhanced_nvgs":             "2513044572",
    "@thermal_improvement":             "2041057379",
    "@zeus_enhanced":                   "1779063631",
    "@zeus_enhanced_compat_ace":        "2018593688",
    "@walkable_moving_objects":         "925018569",
    "@immersion_cigs":                  "753946944",
    "@vcom_ai":                         "721359761",
    "@lambs_rpg":                       "1858070328",
    "@lambs_rpg_compat_rhs":            "2521192995",
    "@lambs_turrets":                   "1862208264",
    "@lambs_suppression":               "1808238502",
    "@real_engine":                     "2127693591",
    "@no_more_aircraft_bouncing":       "1770265310",
    "@tactical_ready":                  "1363663797",
    "@vet_unflipping":                  "1703187116",
    "@enhanced_missile_smoke":          "1484261993",
    "@helicopter_dust_efx":              "1537745369",
    "@arma_fxp":                        "1105511475",
    "@bullet_casings":                  "606289254",
    "@magazine_sim":                    "1373715042",
    "@fluid_door_opening":              "281074849",
    "@enhanced_gps":                    "2480263219",
    "@enhanced_map":                    "2467590475",
    "@boxloader":                       "1199318917",
    "@boxloader_compat_ace":            "1201499127",
    "@unit_voiceovers":                 "1868302880",
    "@unit_voiceovers_compat_rhs":      "1779856762"
}
# Only mod names go here, server/optional mods also need to be listed in MODS
SERVER_MODS = {
    ""
}
OPTIONAL_MODS = {
    ""
}

DLC = {
    "Marksmen": "332350"
}
UPDATE_PATTERN = re.compile(r"workshopAnnouncement.*?<p id=\"(\d+)\">", re.DOTALL)
TITLE_PATTERN = re.compile(r"(?<=<div class=\"workshopItemTitle\">)(.*?)(?=<\/div>)", re.DOTALL)
WORKSHOP_CHANGELOG_URL = "https://steamcommunity.com/sharedfiles/filedetails/changelog"


# endregion

# region Functions
def log(msg):
    print("")
    print("{{0:=<{}}}".format(len(msg)).format(""))
    print(msg)
    print("{{0:=<{}}}".format(len(msg)).format(""))


def call_steamcmd(params):
    os.system("{} {}".format(STEAM_CMD, params))
    print("")


def update_server():
    steam_cmd_params = " +login {} {}".format(STEAM_USER, STEAM_PASS)
    steam_cmd_params += " +force_install_dir {}".format(A3_SERVER_DIR)
    steam_cmd_params += " +app_update {}".format(A3_SERVER_ID)
    steam_cmd_params += " +quit"

    call_steamcmd(steam_cmd_params)


def mod_needs_update(mod_id, path):
    if os.path.isdir(path):
        response = request.urlopen("{}/{}".format(WORKSHOP_CHANGELOG_URL, mod_id)).read()
        response = response.decode("utf-8")
        match = UPDATE_PATTERN.search(response)

        if match:
            updated_at = datetime.fromtimestamp(int(match.group(1)))
            created_at = datetime.fromtimestamp(os.path.getctime(path))

            return updated_at >= created_at

    return False


def update_mods():
    for mod_name, mod_id in MODS.items():
        path = "{}/{}".format(A3_WORKSHOP_DIR, mod_id)

        # Check if mod needs to be updated
        if os.path.isdir(path):

            if mod_needs_update(mod_id, path):
                # Delete existing folder so that we can verify whether the
                # download succeeded
                shutil.rmtree(path)
            else:
                print("No update required for \"{}\" ({})... SKIPPING".format(mod_name, mod_id))
                continue

        # Keep trying until the download actually succeeded
        tries = 0
        while os.path.isdir(path) is False and tries < 10:
            log("Updating \"{}\" ({}) | {}".format(mod_name, mod_id, tries + 1))

            steam_cmd_params = " +login {} {}".format(STEAM_USER, STEAM_PASS)
            steam_cmd_params += " +force_install_dir {}".format(A3_SERVER_DIR)
            steam_cmd_params += " +workshop_download_item {} {} validate".format(
                A3_WORKSHOP_ID,
                mod_id
            )
            steam_cmd_params += " +quit"

            call_steamcmd(steam_cmd_params)

            # Sleep for a bit so that we can kill the script if needed
            time.sleep(5)

            tries = tries + 1

        if tries >= 10:
            log("!! Updating {} failed after {} tries !!".format(mod_name, tries))


def lowercase_workshop_dir():
    def rename_all(root, items):
        for name in items:
            try:
                os.rename(os.path.join(root, name), os.path.join(root, name.lower()))
            except OSError:
                pass
    for root, dirs, files in os.walk(A3_WORKSHOP_DIR, topdown=False):
        rename_all(root, dirs)
        rename_all(root, files)

def create_mod_symlinks():
    for mod_name, mod_id in MODS.items():
        link_path = "{}/{}".format(A3_MODS_DIR, mod_name)
        real_path = "{}/{}".format(A3_WORKSHOP_DIR, mod_id)

        if os.path.isdir(real_path):
            if not os.path.islink(link_path):
                os.symlink(real_path, link_path)
                print("Creating symlink '{}'...".format(link_path))
        else:
            print("Mod '{}' does not exist! ({})".format(mod_name, real_path))


key_regex = re.compile(r'(key).*', re.I)


def copy_keys():
    # Check for broken symlinks
    for key in os.listdir(A3_KEYS_DIR):
        key_path = "{}/{}".format(A3_KEYS_DIR, key)
        if os.path.islink(key_path) and not os.path.exists(key_path):
            print("Removing outdated server key '{}'".format(key))
            os.unlink(key_path)
    # Update/add new key symlinks
    for mod_name, mod_id in MODS.items():
        if mod_name not in SERVER_MODS:
            real_path = "{}/{}".format(A3_WORKSHOP_DIR, mod_id)
            if not os.path.isdir(real_path):
                print("Couldn't copy key for mod '{}', directory doesn't exist.".format(mod_name))
            else:
                dirlist = os.listdir(real_path)
                keyDirs = [x for x in dirlist if re.search(key_regex, x)]

                if keyDirs:
                    keyDir = keyDirs[0]
                    if os.path.isfile("{}/{}".format(real_path, keyDir)):
                        # Key is placed in root directory
                        key = keyDir
                        key_path = os.path.join(A3_KEYS_DIR, key)
                        if not os.path.exists(key_path):
                            print("Creating symlink to key for mod '{}' ({})".format(mod_name, key))
                            os.symlink(os.path.join(real_path, key), key_path)
                    else:
                        # Key is in a folder
                        for key in os.listdir(os.path.join(real_path, keyDir)):
                            real_key_path = os.path.join(real_path, keyDir, key)
                            key_path = os.path.join(A3_KEYS_DIR, key)
                            if not os.path.exists(key_path):
                                print("Creating symlink to key for mod '{}' ({})".format(mod_name, key))
                                os.symlink(real_key_path, key_path)
                else:
                    print("!! Couldn't find key folder for mod {} !!".format(mod_name))


def generate_preset():
    f = open(MODPACK_PATH, "w")
    f.write(('<?xml version="1.0" encoding="utf-8"?>\n'
             '<html>\n\n'
             '<!--Created using a3update.py: https://gist.github.com/Freddo3000/a5cd0494f649db75e43611122c9c3f15-->\n'
             '<head>\n'
             '<meta name="arma:Type" content="{}" />\n'
             '<meta name="arma:PresetName" content="{}" />\n'
             '<meta name="generator" content="a3update.py https://gist.github.com/Freddo3000/a5cd0494f649db75e43611122c9c3f15"/>\n'
             ' <title>Arma 3</title>\n'
             '<link href="https://fonts.googleapis.com/css?family=Roboto" rel="stylesheet" type="text/css" />\n'
             '<style>\n'
             'body {{\n'
             'margin: 0;\n'
             'padding: 0;\n'
             'color: #fff;\n'
             'background: #000;\n'
             '}}\n'
             'body, th, td {{\n'
             'font: 95%/1.3 Roboto, Segoe UI, Tahoma, Arial, Helvetica, sans-serif;\n'
             '}}\n'
             'td {{\n'
             'padding: 3px 30px 3px 0;\n'
             '}}\n'
             'h1 {{\n'
             'padding: 20px 20px 0 20px;\n'
             'color: white;\n'
             'font-weight: 200;\n'
             'font-family: segoe ui;\n'
             'font-size: 3em;\n'
             'margin: 0;\n'
             '}}\n'
             'h2 {{'
             'color: white;'
             'padding: 20px 20px 0 20px;'
             'margin: 0;'
             '}}'
             'em {{\n'
             'font-variant: italic;\n'
             'color:silver;\n'
             '}}\n'
             '.before-list {{\n'
             'padding: 5px 20px 10px 20px;\n'
             '}}\n'
             '.mod-list {{\n'
             'background: #282828;\n'
             'padding: 20px;\n'
             '}}\n'
             '.optional-list {{\n'
             'background: #222222;\n'
             'padding: 20px;\n'
             '}}\n'
             '.dlc-list {{\n'
             'background: #222222;\n'
             'padding: 20px;\n'
             '}}\n'
             '.footer {{\n'
             'padding: 20px;\n'
             'color:gray;\n'
             '}}\n'
             '.whups {{\n'
             'color:gray;\n'
             '}}\n'
             'a {{\n'
             'color: #D18F21;\n'
             'text-decoration: underline;\n'
             '}}\n'
             'a:hover {{\n'
             'color:#F1AF41;\n'
             'text-decoration: none;\n'
             '}}\n'
             '.from-steam {{\n'
             'color: #449EBD;\n'
             '}}\n'
             '.from-local {{\n'
             'color: gray;\n'
             '}}\n'
             ).format("Modpack", MODPACK_NAME))

    f.write(('</style>\n'
             '</head>\n'
             '<body>\n'
             '<h1>Arma 3  - {} <strong>{}</strong></h1>\n'
             '<p class="before-list">\n'
             '<em>Drag this file or link to it to Arma 3 Launcher or open it Mods / Preset / Import.</em>\n'
             '</p>\n'
             '<h2 class="list-heading">Required Mods</h2>'
             '<div class="mod-list">\n'
             '<table>\n'
             ).format("Modpack", MODPACK_NAME))

    for mod_name, mod_id in MODS.items():
        if not (mod_name in OPTIONAL_MODS or mod_name in SERVER_MODS):
            mod_url = "http://steamcommunity.com/sharedfiles/filedetails/?id={}".format(mod_id)
            response = request.urlopen(mod_url).read()
            response = response.decode("utf-8")
            match = TITLE_PATTERN.search(response)
            if match:
                mod_title = match.group(1)
                f.write(('<tr data-type="ModContainer">\n'
                         '<td data-type="DisplayName">{}</td>\n'
                         '<td>\n'
                         '<span class="from-steam">Steam</span>\n'
                         '</td>\n'
                         '<td>\n'
                         '<a href="{}" data-type="Link">{}</a>\n'
                         '</td>\n'
                         '</tr>\n'
                         ).format(mod_title, mod_url, mod_url))
    f.write('</table>\n'
            '</div>\n'
            '<h2 class="list-heading">Optional Mods</h2>'
            '<div class="optional-list">\n'
            '<table>\n'
            )

    for mod_name, mod_id in MODS.items():
        if mod_name in OPTIONAL_MODS:
            mod_url = "http://steamcommunity.com/sharedfiles/filedetails/?id={}".format(mod_id)
            response = request.urlopen(mod_url).read()
            response = response.decode("utf-8")
            match = TITLE_PATTERN.search(response)
            if match:
                mod_title = match.group(1)
                f.write(('<tr data-type="OptionalContainer">\n'
                         '<td data-type="DisplayName">{}</td>\n'
                         '<td>\n'
                         '<span class="from-steam">Steam</span>\n'
                         '</td>\n'
                         '<td>\n'
                         '<a href="{}" data-type="Link">{}</a>\n'
                         '</td>\n'
                         '</tr>\n'
                         ).format(mod_title, mod_url, mod_url))
    f.write('</table>\n'
            '</div>\n'
            '<h2 class="list-heading">DLC</h2>\n'
            '<div class="dlc-list">\n'
            '<table>\n'
            )
    for dlc_name, mod_id in DLC.items():
        mod_url = "https://store.steampowered.com/app/{}".format(mod_id)
        f.write(('<tr data-type="DlcContainer">\n'
                 '<td data-type="DisplayName">{}</td>\n'
                 '<td>\n'
                 '<a href="{}" data-type="Link">{}</a>\n'
                 '</td>\n'
                 '</tr>\n'
                 ).format(dlc_name, mod_url, mod_url))
    f.write('</table>\n'
            '</div>\n'
            '<div class="footer">\n'
            '<span>Created using a3update.py by marceldev89; forked by Freddo3000.</span>\n'
            '</div>\n'
            '</body>\n'
            '</html>\n'
            )

def print_launch_params():
    rel_path = os.path.relpath(A3_MODS_DIR, A3_SERVER_DIR)
    params = "Copy this for launch params:  "
    for mod_name, mod_id in MODS.items():
        params += "{}/{}\;".format(rel_path, mod_name)

    print(params)

# endregion


log("Updating A3 server ({})".format(A3_SERVER_ID))
update_server()

log("Updating mods")
update_mods()

log("Converting uppercase files/folders to lowercase...")
lowercase_workshop_dir()

log("Creating symlinks...")
create_mod_symlinks()

log("Copying server keys...")
copy_keys()

log("Generating modpack .html file...")
generate_preset()

log("Printing launch params...")
print_launch_params()

log("Done!")
