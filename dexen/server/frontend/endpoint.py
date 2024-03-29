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

from flask import request, redirect, url_for, flash, send_file
from flask.ext.login import (login_user, logout_user, login_required,
                             current_user)
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template
import pymongo

from bson.binary import Binary
from bson.objectid import ObjectId

import cPickle as pickle
import base64
import sys

import tempfile

from dexen.common import db, task
from dexen.server.frontend import app, login_mgr, form as dexen_form, proxy


logger = logging.getLogger(__name__)

_server_backend = None
_user_mgr = None
_db_client = None


@login_mgr.user_loader
def load_user(user_id):
    return _user_mgr.get_user(id=user_id)


@app.route("/")
def index():
    if not current_user.is_authenticated():
        logger.debug("Current user is not authenticated redirecting to login page")
        return redirect(url_for("login"))
    logger.debug("Current user is authenticated: %s", current_user.username) # @UndefinedVariable
    return render_template("index.html", username=current_user.username)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":  # @UndefinedVariable
        form = dexen_form.RegistrationForm(_user_mgr)
        if form.validate_on_submit():
            _user_mgr.register_user(form.username.data, form.password.data)
            flash("Registration successfull. Please login.", "success")
            return redirect(url_for("login"))
        logger.debug("Errors %s", form.errors)
        flash("Username already exists.", "danger")
        return redirect(url_for("register"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    logger.debug("The request method in login %s", request.method)
    if request.method == "POST":  # @UndefinedVariable
        form = dexen_form.LoginForm(_user_mgr)
        if form.validate_on_submit():
            login_user(form.get_user())
            logger.debug("%s logged in successfully", current_user.username)  # @UndefinedVariable
            return redirect(url_for("index"))  # @UndefinedVariable
        logger.debug("Login failed. Errors: %s", form.errors)
        flash("Incorrect username or password.", "danger")
        return redirect(url_for("login"))
    print "Getting login.html"
    return render_template("login.html")


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    logger.debug("I am logging out user: %s", current_user.username)  # @UndefinedVariable
    logout_user()
    assert current_user.is_authenticated() == False
    logger.debug("I am redirecting to login page again")
    return redirect(url_for("index"))


@app.route("/upload_file/<job_name>", methods=["POST"])
@login_required
def upload_file(job_name):
#     file_ = request.files['file'] # @UndefinedVariable
#     logger.info("Uploading file %s for %s", file_.filename, job_name)
#     #db_name = GetUserDBName(current_user.username) # @UndefinedVariable
#     #logger.debug("Accessing username's db: %s", db_name)
#     file_mgr = db.FileManager(_db_client, current_user.username) # @UndefinedVariable
#     file_mgr.put_data(job_name, file_.filename, file_.read())

    logger.info("Request.files type: %s", type(request.files))
    logger.info("request files: %s", request.files)

    res = {"files": []}
    file_mgr = db.FileManager(_db_client, current_user.username) # @UndefinedVariable
    for file_ in request.files.values():
        logger.info("Uploading file %s for %s", file_.filename, job_name)
        file_mgr.put_data(job_name, file_.filename, file_.read())
        res["files"].append(file_.filename)
    return jsonify(res)


@app.route("/executions/<job_name>", methods=["GET"])
@login_required
def get_executions(job_name):
    last_update = request.args.get("last_update", 0) # @UndefinedVariable
    last_update = float(last_update)
    execution_mgr = db.ExecutionManager(_db_client, current_user.username,  # @UndefinedVariable
                                        job_name)
    executions = execution_mgr.get_executions(last_update)
    return jsonify(executions=executions)


@app.route("/jobs", methods=["GET"])
@login_required
def get_jobs():
    logger.info("getting jobs")
    jobs = _server_backend.get_jobs(current_user.username) # @UndefinedVariable
    return jsonify(jobs=jobs)


@app.route("/tasks/<job_name>", methods=["GET"])
@login_required
def get_tasks(job_name):
    logger.info("gettings tasks")
    tasks = _server_backend.get_tasks(current_user.username, job_name)
    return jsonify(tasks=tasks)


@app.route("/files_metadata/<job_name>", methods=["GET"])
@login_required
def get_files_metadata(job_name):
    logger.info("Getting files metadata for job: %s.", job_name)
    file_mgr = db.FileManager(_db_client, current_user.username) # @UndefinedVariable
    files_metadata = file_mgr.get_files_metadata(job_name)
    return jsonify(files_metadata=files_metadata)


@app.route("/download_file/<job_name>/<file_name>", methods=["GET"])
@login_required
def download_file(job_name, file_name):
    logger.info("Downloading file %s for job: %s", file_name, job_name)
    file_mgr = db.FileManager(_db_client, current_user.username) # @UndefinedVariable
    f = file_mgr.get_file(job_name, file_name)
    content = f.read()
    f.close()
    response = make_response(content)
    response.headers["Content-Disposition"] = "attachment; filename=%s" % file_name
    return response

@app.route("/data/<job_name>", methods=["GET"])
@login_required
def get_data(job_name):
    try:
        BINARY_KEYS = "keys"
        DATA_ID = "_id"

        logger.info("Getting all data for job: %s", job_name)
        data_mgr = db.JobDataManager(_db_client, current_user.username, job_name) # @UndefinedVariable
        all_data = data_mgr.get_all_data()
        metadata = []
        for data in all_data:
            keysWithBinaryVal = []
            rec = {}
            for key,val in data.items():
                if isinstance(val, Binary):
                    data[key] = ""
                    keysWithBinaryVal.append(key)

            if len(keysWithBinaryVal) != 0:
                rec[BINARY_KEYS] = keysWithBinaryVal
                rec[DATA_ID] = base64.b64encode(pickle.dumps(data[DATA_ID]))

            data[DATA_ID] = str(data[DATA_ID])

            metadata.append(rec)

        return jsonify(data=all_data, metadata=metadata)
    except:
        logger.warning("Unexpected error while reading data objects: ", sys.exc_info()[0])
        return make_response("Unable to read the data objects", 500, None);

@app.route("/data/<job_name>/<enc_data_id>", methods=["GET"])
@login_required
def get_data_object(job_name, enc_data_id):
    try:
        logger.info("Getting data for job: %s, encoded id: %s", job_name, enc_data_id)
        data_id = pickle.loads(base64.b64decode(enc_data_id))
        logger.info("Decoded data id: %s", str(data_id))
        data_mgr = db.JobDataManager(_db_client, current_user.username, job_name) # @UndefinedVariable

        doc = data_mgr.get_data(data_id)

        if doc is None:
            return make_response("Data not found", 400, None)

        ret = base64.b64encode(pickle.dumps(doc))

        return jsonify(data=ret)
    except:
        logger.warning("Unexpected error while reading data object: ", sys.exc_info()[0])
        return make_response("Unable to read the data object", 500, None);

@app.route("/data/<job_name>/<enc_data_id>/<attr_name>", methods=["GET"])
@login_required
def download_data(job_name, enc_data_id, attr_name):
    try:
        logger.info("Getting data for job: %s, encoded id: %s, attr: %s", job_name, enc_data_id, attr_name)
        data_id = pickle.loads(base64.b64decode(enc_data_id))
        logger.info("Decoded data id: %s", str(data_id))
        data_mgr = db.JobDataManager(_db_client, current_user.username, job_name) # @UndefinedVariable
        val = data_mgr.get_data_value(data_id, attr_name)

        if val is None:
            return make_response("Data not found", 400, None)

        if not isinstance(val, Binary):
            return make_response("Unsupported data type", 400, None)

        response = make_response(val)
        ext = request.args.get('ext')
        if ext is None:
            ext = ""
        else:
            ext = "." + ext
        filename = "{0}.{1}.{2}{3}".format(job_name, str(data_id), attr_name, ext)
        response.headers["Content-Disposition"] = "attachment; filename=" + filename

        return response
    except:
        logger.warning("Unexpected error while reading the data object: ", sys.exc_info()[0])
        return make_response("Unable to read the data object for job {0} with id {1} and attr_name {2}".format(job_name, enc_data_id, attr_name), 500, None);


@app.route("/deneme")
def deneme():
    s = "dfafdsafdsafdsf\ndfafdasfdafdfads"
    response = make_response(s)
    response.headers["Content-Disposition"] = "attachment; filename=deneme.txt"
    return response


@app.route("/create_job/<job_name>", methods=["POST"])
@login_required
def create_job(job_name):
    logger.info("%s is created.", job_name)
    _server_backend.create_job(current_user.username, job_name) # @UndefinedVariable
    return "%s created.\n"%(job_name,)


@app.route("/delete_job/<job_name>", methods=["POST"])
@login_required
def delete_job(job_name):
    logger.info("%s is deleted.", job_name)
    _server_backend.delete_job(current_user.username, job_name) # @UndefinedVariable
    return "%s deleted.\n"%(job_name,)


@app.route("/run_job/<job_name>", methods=["POST"])
@login_required
def run_job(job_name):
    logger.info("%s is created.", job_name)
    _server_backend.run_job(current_user.username, job_name) # @UndefinedVariable
    return "Running %s.\n"%(job_name,)


@app.route("/stop_job/<job_name>", methods=["POST"])
@login_required
def stop_job(job_name):
    _server_backend.stop_job(current_user.username, job_name) # @UndefinedVariable
    return "Stopping %s.\n"%(job_name,)


@app.route("/register_task/<job_name>", methods=["POST"])
@login_required
def register_task(job_name):
    task_obj = task.TaskFromJSON(request.json) # @UndefinedVariable
    logger.info("Registering %s %s", job_name, task_obj.name)
    _server_backend.register_task(current_user.username, job_name, task_obj) # @UndefinedVariable
    return jsonify({})


@app.route("/deregister_task/<job_name>/<task_name>", methods=["POST"])
@login_required
def deregister_task(job_name, task_name):
    logger.info("Deregistering %s %s.", job_name, task_name)
    _server_backend.deregister_task(current_user.username, job_name, task_name) # @UndefinedVariable
    return "Deregistering %s %s.\n"%(job_name, task_name)

@app.route("/export/<job_name>", methods=["GET"])
@login_required
def export_job(job_name):
    logger.info("Exporting job %s for user %s.", job_name, current_user.username)
    err, data = _server_backend.export_job(current_user.username, job_name)
    if err:
        return make_response(err, 500, None)

    filename = "{0}.zip".format(job_name)

    return send_file(data, mimetype='application/zip', as_attachment=True, attachment_filename=filename)

@app.route("/import", methods=["POST"])
@login_required
def import_job():
    errorkey = "error"
    logger.info("Request.files type: %s", type(request.files))
    logger.info("request files: %s", request.files)

    fileobj = request.files["jobZip"]
    if fileobj is None:
        return jsonify({errorkey : "Can't find the uploaded file"})
    
    job_name = fileobj.filename
    if job_name.endswith('.zip'):
        job_name = job_name[:-4]

    if len(job_name) == 0:
        return jsonify({errorkey : "Can't find the name of the uploaded file"})

    logger.info("Found job name: %s", job_name)

    savedfile = tempfile.NamedTemporaryFile(suffix='.zip', prefix='dexen-import-' + job_name, delete=False)
    logger.info("Saving to: %s", savedfile.name)
    
    try:
        fileobj.save(savedfile)
        savedfile.close()
        err = _server_backend.import_job(current_user.username, job_name, savedfile.name)
        return jsonify({errorkey : err})

    except Exception, e:
        savedfile.close()
        os.remove(savedfile.name)
        logger.info("Error while saving file: " + str(e))
        return jsonify({errorkey : "Error while saving file: " + str(e)})
    

def start_webserver(backend_addr, db_addr):
    global _server_backend, _user_mgr, _db_client
    _db_client = pymongo.MongoClient(db_addr.ip, db_addr.port)
    _server_backend = proxy.ServerBackendProxy(backend_addr)
    _user_mgr = db.UserManager()
    app.run(threaded=True, debug=True, use_reloader=False)
