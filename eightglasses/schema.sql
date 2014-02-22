drop table if exists entries;
create table entries (
  id integer PRIMARY KEY AUTOINCREMENT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  name text NOT NULL,
  total real DEFAULT 1,
  type text DEFAULT "increment",
  notes text DEFAULT NULL
);

drop table if exists goals;
create table goals (
  id integer PRIMARY KEY AUTOINCREMENT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  name text NOT NULL,
  goal real DEFAULT NULL,
  type text DEFAULT "increment",
  direction text DEFAULT "positive",
  period text DEFAULT "daily",
  verb text DEFAULT NULL,
  subtitle text DEFAULT NULL
);

insert into goals (verb, goal, name, subtitle, period) values ("drink", 8, "glasses", "of water", "daily");

drop table if exists messages;
create table messages (
	id integer PRIMARY KEY AUTOINCREMENT,
	created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
	name text NOT NULL,
	direction text DEFAULT "positive",
	rule text NOT NULL,
	text text NOT NULL,
	hidden tinyint DEFAULT 0
);