import os
import sys
import tempfile
import urllib2
import zipfile
import json
from StringIO import StringIO
from distutils.dir_util import copy_tree, remove_tree


def cleanup(zip_buffer, extracted_dir):
    if zip_buffer:
        zip_buffer.close()
    if os.path.isdir(extracted_dir):
        remove_tree(extracted_dir)


settings_stream = open("settings.json", "r")
settings = json.load(settings_stream)

dir_tmp = tempfile.gettempdir()
dir_extracted_root = ""
dir_backup = os.path.join(dir_tmp, "ElvUIBackup")
dir_addons = "%s/Interface/AddOns/" % settings['dir_wow']

git_repo_url = "https://git.tukui.org/elvui/elvui/-/archive/master/elvui-master.zip"

try:
    print ("Downloading latest Elv UI...")
    response = urllib2.urlopen(git_repo_url)
    data = response.read()
except urllib2.URLError:
    print("Failed to download data from %s" % git_repo_url)
    exit(1)

# write the data to a file-like object in memory
buff = StringIO(data)

# extract the core and config dirs from the zip file
try:
    print ("Extracting zip to %s" % dir_tmp)
    with zipfile.ZipFile(buff, "r") as zip_fp:
        namelist = zip_fp.namelist()
        if ".git" in namelist:
            del namelist[".git"]

        zip_fp.extractall(dir_tmp)
        dir_extracted_root = os.path.join(dir_tmp, namelist[0])
except zipfile.BadZipfile:
    print("Downloaded zip file is not valid")
    cleanup(buff, dir_extracted_root)
    exit(1)
except RuntimeError:
    print("Failed to extract contents of zip")
    cleanup(buff, dir_extracted_root)
    exit(1)

# Create a backup
try:
    print ("Backing up current folder to %s" % dir_backup)
    copy_tree(dir_extracted_root, dir_backup)
except RuntimeError as e:
    print e
    print("Failed to create backup; aborting")
    cleanup(buff, dir_extracted_root)
    exit(1)

# overwrite the files with the new ones
try:
    print ("Copying extract to %s" % dir_addons)
    copy_tree(dir_extracted_root, dir_addons)
except:
    print("Error copying files to addons dir")
finally:
    cleanup(buff, dir_extracted_root)
    print("Done")
