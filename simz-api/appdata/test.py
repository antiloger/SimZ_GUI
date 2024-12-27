#
# import duckdb
# import uuid
#
# con = duckdb.connect("./api/data.db")

# con.execute("""
#     CREATE TABLE users (
#         id UUID PRIMARY KEY,
#         name varchar(225) NOT NULL,
#         email varchar(225),
#         role varchar(225),
#         create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         last_use TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     )
# """)
# con.execute("""
#     CREATE TABLE sim_server (
#         id UUID PRIMARY KEY,
#         name varchar(225) NOT NULL,
#         location varchar(225),
#         server varchar(225),
#         create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         last_use TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#     )
# """)
# con.execute("""
#     CREATE TABLE projects (
#         id UUID PRIMARY KEY,
#         name varchar(225) NOT NULL,
#         sim_server_id UUID,
#         create_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         last_use TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
#         create_user_id UUID,
#         FOREIGN KEY (sim_server_id) REFERENCES sim_server(id)
#     )
# """)
# con.execute("""
#     INSERT INTO users (id, name, email, role) VALUES (?,?,?, ?);""",
#     (uuid.uuid4(), "user1", "test@ts.com", "admin")
# )
# con.execute("""
#     INSERT INTO sim_server (id, name, location) VALUES (?,?,?);""",
#             (uuid.uuid4(), "server1", "local://file/t.s")
# )
# con.sql("SELECT * FROM users").show()
# con.sql("SELECT * FROM sim_server").show()
# con.execute("""
#     INSERT INTO projects (id, name, sim_server_id, create_user_id) VALUES (?,?,?, ?);""",
#     (uuid.uuid4(), "projects1", "735beba6-8952-499e-bc3e-945384bc7529", "7fc40abb-9b4c-46e8-a266-3427fa869181")
# )

# con.sql("SELECT * FROM projects").show()
