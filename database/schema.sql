CREATE TABLE IF NOT EXISTS users
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    username VARCHAR(16) NOT NULL UNIQUE,
    email VARCHAR(254),
    email_confirmed TINYINT(1) NOT NULL DEFAULT 0, -- whether or not the email address has been confirmed
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    creation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    password CHAR(81), -- 64 for SHA-256 plus 16 for salt
    handle VARCHAR(16) NOT NULL UNIQUE, -- user's chosen in-game alias; can be changed
    computer_id INT(12) NOT NULL DEFAULT 0 REFERENCES computers(id),
    token VARCHAR(12) NOT NULL DEFAULT '', -- token for email confirmation and password resets
    token_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, -- date on which the token was created
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS computers
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    ip VARCHAR(16) NOT NULL UNIQUE,
    password VARCHAR(16) NOT NULL, -- root password for hacking into the computer
    domain_name VARCHAR(32), -- exists if this computer is a web server
    owner_id INT(12) REFERENCES users(id),
    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    bank_id INT(12) REFERENCES banks(id), -- exists if this computer is a bank server
    ram INT(8) DEFAULT 512, -- total RAM in MB
    cpu INT(8) DEFAULT 512, -- total CPU speed in MHz
    hdd INT(8) DEFAULT 1, -- total hard drive space in GB (smallest drive is 1 GB)
    online TINYINT(1) DEFAULT 1, -- whether or not the computer can be contacted
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS directories
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    dir_name VARCHAR(16) NOT NULL,
    parent_id INT(12) NOT NULL,
    computer_id INT(12) NOT NULL DEFAULT 0 REFERENCES computers(id),
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_only TINYINT(1) DEFAULT 0,
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS files
(
    id INT(12) NOT NULL UNIQUE AUTO_INCREMENT,
    file_name VARCHAR(32) NOT NULL,
    parent_id INT(12) NOT NULL REFERENCES directories(id),
    owner_id INT(12) NOT NULL REFERENCES users(id),
    content VARCHAR(4096) DEFAULT NULL,
    file_type VARCHAR(5) NOT NULL,
    file_level INT(2) NOT NULL,
    file_size INT(12) NOT NULL, -- size in bytes
    creation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(32) DEFAULT NULL, -- e.g. 'fw', 'cr'
    comment VARCHAR(128) DEFAULT NULL, -- description for .bin files
    memory INT(8) DEFAULT NULL, -- memory usage for .bin files in MB
    is_live TINYINT(1) DEFAULT NULL, -- whether or not a virus file is live
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
    sender_email VARCHAR(254) NOT NULL REFERENCES users(email),
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS processes
(
    id int(12) NOT NULL UNIQUE AUTO_INCREMENT,
    comp_id INT(12) NOT NULL DEFAULT 0 REFERENCES computers(id), -- computer the process runs on
    file_id INT(12) NOT NULL DEFAULT 0 REFERENCES files(id), -- file which started the process
    user_id INT(12) NOT NULL DEFAULT 0 REFERENCES users(id), -- user who started the process
    target_id INT(12) DEFAULT NULL REFERENCES computers(id), -- target computer if applicable
    started_on TIMESTAMP NOT NULL DEFAULT now(), -- when the process was initiated
    finished_on TIMESTAMP NOT NULL DEFAULT now(), -- when the process will be done
    memory INT(8) DEFAULT 0 REFERENCES files(memory), -- how much memory this process takes up
    PRIMARY KEY(id)
);

CREATE TABLE IF NOT EXISTS user_stats
(
    id int(12) NOT NULL REFERENCES users(id),
    ssh_count int(12), -- number of SSH logins
    cr_count int(12), -- number of passwords cracked
    virus_count int(12), -- number of virus installations
    av_count int(12), -- number of antivirus scans run
    login_count int(12), -- number of game logins
    files_edited int(12), -- number of file edits
    PRIMARY KEY(id)
);