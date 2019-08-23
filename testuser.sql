CREATE USER 'testuser'@'localhost' IDENTIFIED BY 'testpassword';
GRANT ALL PRIVILEGES ON * . * TO 'testuser'@'localhost';
FLUSH PRIVILEGES;
