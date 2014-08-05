# ==================================================================================================
#
#    Copyright (c) 2008, Patrick Janssen (patrick@janssen.name)
#
#    This file is part of Dexen.
#
#    Dexen is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    Dexen is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with Dexen.  If not, see <http://www.gnu.org/licenses/>.
#
# ==================================================================================================

import os
import logging
import multiprocessing
import stat
from StringIO import StringIO
import zipfile


def setup_logging(log_path):
    root_logger = logging.getLogger()

    formatter = logging.Formatter("[%(levelname)-5s] - %(asctime)s - %(name)-15s"
                                  " - %(message)s", "%Y/%m/%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    if log_path:
        file_handler = logging.FileHandler(log_path, mode="w")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        root_logger.addHandler(file_handler)
        console_handler.setLevel(logging.INFO)
    else:
        console_handler.setLevel(logging.DEBUG)

    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.DEBUG)


def cpu_count():
    try:
        return multiprocessing.cpu_count()
    except:
        return 4


def zipfolder(foldername, target_dir, include_rootdir=True):
    zipobj = zipfile.ZipFile(foldername + '.zip', 'w', zipfile.ZIP_DEFLATED)
    prev_dir = os.getcwd()
    root_dir = os.path.basename(target_dir)
    rootlen = 0
    if not include_rootdir:
        rootlen = len(root_dir)+1
    try:
        os.chdir(os.path.dirname(target_dir))
        for base, dirs, files in os.walk(root_dir):
            for file in files:
                fn = os.path.join(base, file)
                zipobj.write(fn, fn[rootlen:])
    finally:
        os.chdir(prev_dir)


def rmentry(entry):
    if os.path.isdir(entry):
        del_tree(entry)
        os.rmdir(entry)
    elif os.path.isfile(entry):
        os.remove(entry)
    else:
        pass #ERROR


def del_tree(path):
    " Delete all the directory structure, could be very dangerous "
    " Does not delete root folder"
    for root, dirs, files in os.walk(path, topdown=False):
#        if root[0] == '.' :
#            continue
        for name in files:
            os.remove(os.path.join(root,name))
        for name in dirs:
            os.rmdir(os.path.join(root,name))


def unzip(zip_file_content , output_dir , mode='d'):
    """ 
    Unzip the zip_file_content in output-dir
    If the output_dir does not exist, it will create it first
    mode : 'd' to delete every thing in the output directory before extraction
           'i' do not write on the existing files in the output-directory
           'o' overwrite on the existing file and ignore rest of files and directories
    """
    
    if not os.path.exists(output_dir):
        os.mkdir(output_dir)
    
    zip_file = StringIO(zip_file_content)
    contents = zipfile.ZipFile(zip_file, 'r')
    
    output_dir += "/"
    base_dir = output_dir

    if mode=="d" :
        del_tree(output_dir)
    
    for file in contents.namelist():
        file_dir = os.path.join(base_dir, os.path.dirname(file.replace('/', os.sep)))
        file_name = os.path.basename(file)
        file_path = os.path.join(base_dir, file.replace('/', os.sep))
        #print file, "!", file_name, "!", file_path, "<br><br>"
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
            writeable(file_dir)
        data = contents.read(file)
        try:
            fp = open(file_path, 'wb')
            fp.write(data)
            fp.close()
            if file.endswith("py"):
                # give read and execute permission to file
                writeable(file_path)
        except IOError:
            pass # XXX handle permissions    


def writeable(file):
    """
    Make writeable by other users
    """
    try:
        os.chmod(file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)#stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    except OSError:
        pass # insufficient permissions


