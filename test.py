from flask import Flask
from flask import jsonify
from flask import request
from flask_api import status
import sqlite3


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


app = Flask(__name__)
dbname = "todos.db"


@app.route("/todos", methods=["GET"])
def get_all_todos():
    conn = sqlite3.connect(dbname)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("select * from todos")
    return jsonify(c.fetchall()), status.HTTP_200_OK


@app.route("/todos/<int:todo_id>", methods=["GET"])
def get_todo(todo_id):
    conn = sqlite3.connect(dbname)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("select * from todos where id = ?", [todo_id])
    todo = c.fetchone()
    if todo:
        return jsonify(todo), status.HTTP_200_OK

    return jsonify({"result": "Not found"}), status.HTTP_404_NOT_FOUND


@app.route("/search", methods=["GET"])
def search_todo():
    result = []
    task = request.args.get("task")
    conn = sqlite3.connect(dbname)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("select * from todos where task like ?", ['%' + task + '%'])
    for todo in c.fetchall():
        result.append(todo)
    if result:
        return jsonify(result), status.HTTP_200_OK
    else:
        return jsonify({"result": "Not found"}), status.HTTP_404_NOT_FOUND


@app.route("/todos", methods=["POST"])
def post_todo():
    req = request.get_json()
    if not req["task"]:
        return jsonify({"result": "Bad Request"}), status.HTTP_400_BAD_REQUEST
    else:
        conn = sqlite3.connect(dbname)
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("select * from todos where task = ?", [req["task"]])
        check = c.fetchone()
        if check:
            return jsonify({"result": "conflict"}), status.HTTP_409_CONFLICT
        try:
            c.execute("insert into todos(task) values(?)", [req["task"]])
            conn.commit()
        except sqlite3.Error as e:
            print(e)
        c.execute("select * from todos where rowid = last_insert_rowid()")
        todo = c.fetchone()
        return jsonify(todo), status.HTTP_201_CREATED


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id):
    conn = sqlite3.connect(dbname)
    conn.row_factory = dict_factory
    c = conn.cursor()
    c.execute("select * from todos where id = ?", [todo_id])
    todo = c.fetchone()
    if todo:
        c.execute("delete from todos where id = ?", [todo_id])
        conn.commit()
        return jsonify(), status.HTTP_204_NO_CONTENT

    return jsonify({"result": "Not found"}), status.HTTP_404_NOT_FOUND


@app.route("/todos", methods=["PUT"])
def put_todo():
    req = request.get_json()
    if not req["id"] or not req["task"]:
        return jsonify({"result": "Bad Request"}), status.HTTP_400_BAD_REQUEST
    else:
        conn = sqlite3.connect(dbname)
        conn.row_factory = dict_factory
        c = conn.cursor()
        c.execute("select * from todos where id = ?", [req["id"]])
        todo = c.fetchone()
        if todo:
            c.execute("update todos set task = ? where id = ?", (req["task"],
                                                                 req["id"]))
            conn.commit()
            return jsonify(), status.HTTP_204_NO_CONTENT

        return jsonify({"result": "Not found"}), status.HTTP_404_NOT_FOUND


if __name__ == "__main__":
    app.run()
