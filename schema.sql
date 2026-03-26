-- Parking Management System Schema
-- MySQL 8.0+

CREATE DATABASE IF NOT EXISTS parking_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE parking_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL,
    role ENUM('admin', 'user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS slots (
    id INT PRIMARY KEY,
    status ENUM('available', 'occupied') NOT NULL DEFAULT 'available'
);

CREATE TABLE IF NOT EXISTS vehicles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20) NOT NULL UNIQUE,
    owner_name VARCHAR(100) NOT NULL,
    user_id INT NOT NULL,
    entry_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    exit_time DATETIME DEFAULT NULL,
    fee DECIMAL(10, 2) DEFAULT 0.00,
    status ENUM('parked', 'exited') NOT NULL DEFAULT 'parked',
    slot_number INT DEFAULT NULL,
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_slot FOREIGN KEY (slot_number) REFERENCES slots(id)
);

-- Seed 50 slots
INSERT INTO slots (id, status) VALUES
(1,'available'),(2,'available'),(3,'available'),(4,'available'),(5,'available'),
(6,'available'),(7,'available'),(8,'available'),(9,'available'),(10,'available'),
(11,'available'),(12,'available'),(13,'available'),(14,'available'),(15,'available'),
(16,'available'),(17,'available'),(18,'available'),(19,'available'),(20,'available'),
(21,'available'),(22,'available'),(23,'available'),(24,'available'),(25,'available'),
(26,'available'),(27,'available'),(28,'available'),(29,'available'),(30,'available'),
(31,'available'),(32,'available'),(33,'available'),(34,'available'),(35,'available'),
(36,'available'),(37,'available'),(38,'available'),(39,'available'),(40,'available'),
(41,'available'),(42,'available'),(43,'available'),(44,'available'),(45,'available'),
(46,'available'),(47,'available'),(48,'available'),(49,'available'),(50,'available');

-- Default admin (password: 1234)
INSERT INTO users (username, password, role) VALUES
('admin', 'pbkdf2:sha256:600000$rS1mWqLzXNHt3yKp$9f2a8e4d6c0b1f3a5e7d9c2b4f6a8e0d2c4b6f8a0e2d4c6b8f0a2e4d6c8b0f2', 'admin')
ON DUPLICATE KEY UPDATE username = username;
INSERT INTO users (username, password, role) VALUES
('admin', 'pbkdf2:sha256:600000$rS1mWqLzXNHt3yKp$9f2a8e4d6c0b1f3a5e7d9c2b4f6a8e0d2c4b6f8a0e2d4c6b8f0a2e4d6c8b0f2', 'admin')
ON DUPLICATE KEY UPDATE username = username;
