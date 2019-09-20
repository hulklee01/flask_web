drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  'text' text not null
);

create table user (
    id integer primary key autoincrement,
    user_id text not null,
    password text not null
);