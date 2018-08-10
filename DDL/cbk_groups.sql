CREATE TABLE cbk_groups(
    id serial UNIQUE NOT NULL,
    name char(30) NOT NULL,
    date_created timestamp NOT NULL,
    date_modified timestamp NOT NULL,
    PRIMARY KEY(id)
);