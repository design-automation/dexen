'''
Created on Aug 1, 2013

@author: Cihat Basol
'''


import os
import sys
import time
import subprocess


from gridfs import GridFS
from pymongo import Connection
from bson.objectid import ObjectId

from flask import Flask

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


def main():
    """
    os.environ["DENEME"] = "HAHA"
    de = {"ali" : "veli"}
    
    p = subprocess.Popen(["python", "temp2.py"])
    for _ in xrange(5):
        time.sleep(1)
        print p.poll()
        #break
    if p.poll() is None:
        p.terminate()
    """

    """
    db = Connection().test_database
    fs = GridFS(db)
    #file_id = fs.put("hello world2")
    #print file_id
    file_id = ObjectId("51fad99a482d41d28f496ce5")
    print fs.get(file_id).read()
    """
    
    """
    from dexen.common import utils
    
    target_dir = os.path.join(os.path.dirname(os.getcwd()), "libs")
    
    print target_dir
    
    utils.zipfolder("deneme", target_dir)
    
    f = open("deneme.zip", "rb")
    
    utils.unzip(f.read(), "haha")
    
    f.close()
    """
    
    app.run(debug=True)
    
    
if __name__ == '__main__':
    main()




