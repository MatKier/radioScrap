from requests_html import HTMLSession
import requests
import os
from datetime import datetime
import re
import sys

if (len(sys.argv)-1 != 1):
    print("Wrong number of arguments, musst provide radiopaedia case url!")
    exit()

case_url = str(sys.argv[1])
print("URL: " + case_url)

caseRegex = re.compile("^(https://.*cases/)(.*)(?:\?lang=\w{1,2})", flags=re.IGNORECASE)
file_type_regex = re.compile("(jpeg|jpg|png|gif|tiff)$", flags=re.IGNORECASE)

case_name = str(caseRegex.search(case_url)[2])
print("case name:" + case_name)

now = datetime.now()
main_folder = case_name + "_" + str(datetime.now().strftime("%d_%m_%Y-%H_%M_%S"))
os.mkdir(main_folder)

print("\nSearching for data-study-id ...")
session = HTMLSession()
main_html = session.get(case_url)
main_html.html.render()
div_1 = main_html.html.find('div.user-generated-content', first=True)
div_2 = div_1.find('div.well.case-section.case-study', first=True)
data_study_id = str(div_2.attrs['data-study-id'])
print("data-study-id: " + data_study_id)


picture_stacks_url = "https://radiopaedia.org/studies/" + data_study_id + "/stacks"
print("\nFetching study json from " + picture_stacks_url +" ...")
PARAMS = {'lang':'us'}

picture_stacks_json = requests.get(url = picture_stacks_url, params = PARAMS)
data = picture_stacks_json.json()
print("Got study json!\n")

counter = 1
for image_set in data:
    plane_projection = str(image_set["images"][0]["plane_projection"])
    aux_modality = str(image_set["images"][0]["aux_modality"])
    sub_folder_name = str(counter) + "_" + plane_projection + "_" + aux_modality
    folder = str(main_folder + "/" + sub_folder_name)
    os.mkdir(folder)
    images = image_set["images"]
    print("Downloading images for " + sub_folder_name + " ...")
    for image in images:
        img_url = image["fullscreen_filename"]
        image_id = image["id"]
        img_file = requests.get(img_url)
        file_type = "." + str(file_type_regex.search(img_url)[1])
        open(folder + '/' + str(image_id) + file_type, 'wb').write(img_file.content)
    counter = counter + 1

print("\nFinished!")