CREATE TABLE cbk_group_members(
    member_id integer REFERENCES cbk_users(id),
    group_id integer REFERENCES cbk_groups(id)
);