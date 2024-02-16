from flask import Flask, render_template, send_from_directory, make_response, request

import database as db
import util

app = Flask(__name__)


@app.route("/images/<img>")
def images_img(img):
    return send_from_directory("templates/images", img)


@app.route("/assets/<file>")
def assets_file(file):
    return send_from_directory("templates/assets", file)


@app.route("/assets/<resource>/<file>")
def assets_resource_file(resource, file):
    return send_from_directory(f"templates/assets/{resource}", file)


@app.route("/assets/<resource>/<subfolder>/<file>")
def assets_resource_subfolder_file(resource, subfolder, file):
    return send_from_directory(f"templates/assets/{resource}/{subfolder}", file)


@app.route("/sw.js")
def service_worker():
    return send_from_directory(f"templates/assets/pwa", "sw.js")


@app.route("/offline.html")
@app.route("/")
def homepage():  # put application's code here
    user_id, needs_cookie = util.get_make_user(request)
    task, task_completed = request.args.get("task"), False
    if task:
        task_completed = util.complete_task(user_id, int(task))
    open_tasks, closed_tasks = util.get_incomplete_tasks(
        user_id
    ), util.get_complete_tasks(user_id)
    open_tasks, closed_tasks = (
        open_tasks[0 : min(len(open_tasks), 5)],
        closed_tasks[0 : min(len(closed_tasks), 5)],
    )
    resp = make_response(
        render_template(
            "index.html",
            open_tasks=open_tasks,
            closed_tasks=closed_tasks,
            just_scanned=util.did_just_scan(user_id),
        )
    )
    resp.set_cookie("scvgr_user_id", str(user_id), 365 * 24 * 60 * 60)
    return resp


@app.route("/tasks")
def tasks():
    user_id, needs_cookie = util.get_make_user(request)
    open_tasks, closed_tasks = util.get_incomplete_tasks(
        user_id
    ), util.get_complete_tasks(user_id)
    resp = make_response(
        render_template(
            "task.html",
            open_tasks=open_tasks,
            closed_tasks=closed_tasks,
            just_scanned=util.did_just_scan(user_id),
        )
    )
    resp.set_cookie("scvgr_user_id", str(user_id), 365 * 24 * 60 * 60)
    return resp


@app.route("/test")
def test():  # put application's code here
    user_id, needs_cookie = util.get_make_user(request)
    task, task_completed = request.args.get("task"), False
    if task:
        task_completed = util.complete_task(user_id, int(task))
    resp = make_response(render_template("task.html"))
    resp.set_cookie("scvgr_user_id", str(user_id), 365 * 24 * 60 * 60)
    print(f"Completed tasks for {user_id}: {util.get_complete_tasks(user_id)}")
    print(f"Incomplete tasks for {user_id}: {util.get_incomplete_tasks(user_id)}")

    return resp


if __name__ == "__main__":
    app.run()