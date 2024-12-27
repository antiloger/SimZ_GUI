from api.app import App

if __name__ == "__main__":
    App.run()


# import duckdb
# import uuid
#
# con = duckdb.connect("./api/data.db")
# con.sql("SHOW TABLES").show()
