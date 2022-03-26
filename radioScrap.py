# -*- coding: utf-8 -*-

from requests_html import HTMLSession
from datetime import datetime
import re
import sys
from tqdm import tqdm
from pathlib import Path

#Helper function for getting all images associated with a specific data-study-id
def scrapeStudy(data_study_id):
    global sub_folder_counter
    picture_stacks_url = "https://radiopaedia.org/studies/" + data_study_id + "/stacks"
    print("Fetching study json from " + picture_stacks_url +" ...")
    PARAMS = {'lang':lang}

    picture_stacks_json = session.get(url = picture_stacks_url, params = PARAMS)
    json_data = picture_stacks_json.json()
    print("Got study json!")

    print("Found " + str(len(json_data)) + " image sets in study " + data_study_id)
    # one image_set is one "modality" / "images" element in the json data
    for image_set in json_data:
        modality = str(image_set["modality"])
        plane_projection = str(image_set["images"][0]["plane_projection"])
        aux_modality = str(image_set["images"][0]["aux_modality"])
        # change units like "mm/s" to "m per s" because / is an illegal character for folders
        sub_folder_name = (str(sub_folder_counter) + "_" + modality + "_" + plane_projection + "_" + aux_modality).replace("/", " per ")
        # replace most other illegal folder chraracters
        sub_folder_name = illegal_char_regex.sub(" ", sub_folder_name)
        folder = str(main_folder + "/" + sub_folder_name)
        Path(folder).mkdir(parents=True, exist_ok=True)
        images = image_set["images"]
        print("Downloading " + str(len(images)) + " images for set \"" + sub_folder_name + "\" ...")
        pbar = tqdm(images, unit=" img")
        for image in pbar:
            img_url = image["fullscreen_filename"]
            image_id = image["id"]
            img_file = session.get(img_url)
            file_type = "." + str(file_type_regex.search(img_url)[1])
            file_name = str(image_id) + str(file_type)
            pbar.set_description("Downloading %s" % file_name, True)
            open(folder + '/' + file_name, 'wb').write(img_file.content)
        pbar.close()
        sub_folder_counter = sub_folder_counter + 1
    print("Finished scraping study " + data_study_id)

# Main program
sub_folder_counter = 1

if (len(sys.argv)-1 != 1 or "https://radiopaedia.org/cases/" not in sys.argv[1]):
    print("Wrong argument, musst provide radiopaedia cases url!")
    exit()

case_url = str(sys.argv[1])
print("URL:\t\t" + case_url)

illegal_char_regex = re.compile(r"(\\|\/|:|\*|\?|\"|<|>|\|)")
caseRegex = re.compile(r"^(https://radiopaedia\.org/cases/)(?:(.*)(?:\?lang=(\w{1,3}))|(.*))$", flags=re.IGNORECASE)
file_type_regex = re.compile(r"(jpeg|jpg|png|gif|tiff)$", flags=re.IGNORECASE)

lang = str(caseRegex.search(case_url)[3])
if (lang == "None" or lang is None):
    # No ?lang=x element at the end
    case_name = str(caseRegex.search(case_url)[4])
    lang = ""
else:
    case_name = str(caseRegex.search(case_url)[2])

print("case name:\t" + case_name)
print("lang:\t\t" + lang)

now = datetime.now()
main_folder = case_name + "_" + str(datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))
main_folder = illegal_char_regex.sub(" ", main_folder)
Path(main_folder).mkdir(parents=True, exist_ok=True)

session = HTMLSession()
#non-essential user-agent check
try:
    user_agent = session.get("https://httpbin.org/user-agent")
    print("\nuser-agent: %s" % user_agent.json()["user-agent"])
except:
    pass

print("\nSearching for data-study-ids ...")
main_html = session.get(case_url)
#main_html.html.render() -- uneccessrary
content_div = main_html.html.find('div.user-generated-content', first=True)
data_study_divs = content_div.find('div.well.case-section.case-study')

datat_study_ids = [str(data_div.attrs["data-study-id"]) for data_div in data_study_divs]
print("Found " + str(len(datat_study_ids)) + " data-study-id(s): " + str(datat_study_ids))

for data_study_id in datat_study_ids:
    print("\nScraping study " + data_study_id)
    scrapeStudy(data_study_id)

print("\nScraping finished!")