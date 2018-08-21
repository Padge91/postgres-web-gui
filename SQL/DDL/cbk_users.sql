CREATE TABLE cbk_users(
    id serial UNIQUE NOT NULL,
    username char(50) NOT NULL,
    password char(200) NOT NULL,
    salt char(200) NOT NULL,
    date_created timestamp NOT NULL,
    date_modified timestamp,
    session char(100),
    session_expire timestamp,
    admin boolean NOT NULL,
    PRIMARY KEY(id)
);