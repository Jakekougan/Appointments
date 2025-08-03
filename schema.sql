DROP TABLE IF EXISTS appointments;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name VARCHAR(75) NOT NULL,
    last_name VARCHAR(75) NOT NULL,
    email VARCHAR(50) NOT NULL UNIQUE,
    phone_number CHAR(10),
    password VARCHAR(100) NOT NULL,
    type boolean
);

CREATE TABLE appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id int NOT NULL REFERENCES users(id),
    date CHAR(10),
    start_time CHAR(8),
    end_time CHAR(8)
);