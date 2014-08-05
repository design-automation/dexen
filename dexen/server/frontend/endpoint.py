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

from flask import request, redirect, url_for
from flask.ext.login import (login_user, logout_user, login_required,
                             current_user)
from flask.helpers import make_response
from flask.json import jsonify
from flask.templating import render_template
import pymongo

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
            return redirect(url_for("login"))
        logger.debug("Errors %s", form.errors)
        return "Registration failed"
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


def start_webserver(backend_addr, db_addr):
    global _server_backend, _user_mgr, _db_client
    _db_client = pymongo.MongoClient(db_addr.ip, db_addr.port)
    _server_backend = proxy.ServerBackendProxy(backend_addr)
    _user_mgr = db.UserManager()
    app.run(threaded=True, debug=True, use_reloader=False)
