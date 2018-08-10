CREATE TABLE cbk_group_permissions(
    group_id integer REFERENCES cbk_groups(id),
    table_name char(200) NOT NULL,
    can_read boolean NOT NULL,
    can_create boolean NOT NULL,
    can_update boolean NOT NULL,
    can_delete boolean NOT NULL
);