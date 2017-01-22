CREATE TABLE IF NOT EXISTS users
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    username VARCHAR(16) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password CHAR(81), -- 64 for SHA-256 plus 16 for salt
    handle VARCHAR(16) NOT NULL UNIQUE, -- user's chosen in-game alias; can be changed
    computer_id INT(12) NOT NULL DEFAULT 0 REFERENCES computers(id),
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS computers
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    ip VARCHAR(16) NOT NULL UNIQUE,
    password VARCHAR(16) NOT NULL, -- password used to hack into the computer
    domain_name VARCHAR(32),
    owner_id INT(12) REFERENCES users(id),
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bank_id INT(12) REFERENCES banks(id),
    ram INT(8) DEFAULT 512, -- total RAM in MB
    cpu INT(8) DEFAULT 512, -- total CPU speed in MHz
    hdd INT(8) DEFAULT 1, -- total hard drive space in GB
    disk_free INT(8) DEFAULT 1, -- total free disk space in GB
    fw_level INT(3) DEFAULT 1,  -- strength of best firewall on system
    av_level INT(3) DEFAULT 1,  -- strength of best antivirus software
    cr_level INT(3) DEFAULT 1,  -- strength of best password cracker
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS directories
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    dir_name VARCHAR(32) NOT NULL,
    parent_id INT(12) NOT NULL,
    computer_id INT(12) NOT NULL DEFAULT 0 REFERENCES computers(id),
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS files
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    file_name VARCHAR(32) NOT NULL,
    parent_id INT(12) NOT NULL REFERENCES directories(id),
    content VARCHAR(4096),
    file_type VARCHAR(4) NOT NULL,
    file_level INT(2) NOT NULL,
    file_size INT(12) NOT NULL, -- size in bytes
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS banks
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    bank_name VARCHAR(32) NOT NULL UNIQUE,
    description VARCHAR(1024),
    min_funds INT(16) NOT NULL DEFAULT 0, -- some banks require a minimum deposit
    account_cost INT(16) NOT NULL DEFAULT 0, -- cost of opening an account
    interest_rate INT(2) NOT NULL DEFAULT 0, -- percentage (1-100)
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS bank_accounts
(
    acct_number INT(12) NOT NULL,
    bank_id INT(12) NOT NULL REFERENCES banks(id),
    pin INT(8),
    owner_id INT(12) NOT NULL REFERENCES users(id),
    funds INT(16) NOT NULL DEFAULT 0,
    PRIMARY KEY(acct_number, bank_id)
);

CREATE TABLE IF NOT EXISTS emails
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    sent_on TIMESTAMP NOT NULL,
    content VARCHAR(4096),
    subject VARCHAR(256),
    server_id INT(12) NOT NULL REFERENCES computers(id),
    recipient_email VARCHAR(254) NOT NULL REFERENCES users(email),
    sender_email VARCHAR(254) NOT NULL REFERENCES users(email)
);
