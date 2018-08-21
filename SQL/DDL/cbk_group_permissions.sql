CREATE TABLE cbk_group_permissions(
    group_id integer REFERENCES cbk_groups(id),
    object_label char(200) NOT NULL,
    permission_id integer REFERENCES cbk_permissions(id)
);