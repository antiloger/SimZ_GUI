from flask import Flask
import duckdb

mainDBconn = duckdb.connect('./api/data.db')
App = Flask(__name__)
mainDBconn.sql("SHOW TABLES").show()

@App.get("/recent-project")
def get_recent_project():
    data = mainDBconn.sql(
        "SELECT * FROM projects ORDER BY last_use DESC;"
    ).fetchall()

    return data

