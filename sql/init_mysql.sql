-- --------------------------------------------------------
-- Restaurant Reservation Database
-- --------------------------------------------------------
CREATE DATABASE IF NOT EXISTS restaurant_db;
USE restaurant_db;

-- --------------------------------------------------------
-- Table: customers
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    phone_number VARCHAR(12) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    preferences VARCHAR(255) DEFAULT '',
    dietary_requirements VARCHAR(255) DEFAULT '',
    visit_count INT DEFAULT 0,
    special_notes VARCHAR(255),
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dummy Customers
INSERT INTO customers (first_name, last_name, phone_number, email, preferences, dietary_requirements, visit_count)
VALUES
('John', 'Doe', '9876543210', 'john@example.com', 'Window Seat', 'Vegetarian', 3),
('Alice', 'Smith', '8765432109', 'alice@example.com', 'Booth', 'Vegan', 1),
('Bob', 'Brown', '7654321098', 'bob@example.com', 'Quiet Area', 'Gluten-Free', 0);

-- --------------------------------------------------------
-- Table: tables
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS tables (
    id INT AUTO_INCREMENT PRIMARY KEY,
    table_number INT UNIQUE NOT NULL,
    capacity INT NOT NULL,
    location ENUM('Window','Center','Outdoor') NOT NULL,
    is_combinable BOOLEAN DEFAULT FALSE,
    status ENUM('Available','Occupied','Maintenance','Special Event','Reserved') DEFAULT 'Available',
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dummy Tables
INSERT INTO tables (table_number, capacity, location, is_combinable, status)
VALUES
(1, 2, 'Window', TRUE, 'Available'),
(2, 4, 'Center', TRUE, 'Available'),
(3, 2, 'Outdoor', FALSE, 'Available'),
(4, 6, 'Center', TRUE, 'Available'),
(5, 4, 'Window', FALSE, 'Available');

-- --------------------------------------------------------
-- Table: reservations
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    party_size INT NOT NULL,
    reservation_date DATE NOT NULL,
    reservation_time TIME NOT NULL,
    duration_hours INT DEFAULT 2,
    booking_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('Confirmed','Pending','Seated','Completed','Cancelled') DEFAULT 'Confirmed',
    notes VARCHAR(255),
    requested_preference ENUM('Quiet Area','Window Seat','Booth','Near Kitchen'),
    is_walk_in BOOLEAN DEFAULT FALSE,
    assigned_capacity INT DEFAULT 0,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE CASCADE
);

-- Dummy Reservations
INSERT INTO reservations (customer_id, party_size, reservation_date, reservation_time, status, requested_preference, notes)
VALUES
(1, 2, '2025-10-04', '19:00:00', 'Confirmed', 'Window Seat', 'Anniversary dinner'),
(2, 4, '2025-10-04', '20:00:00', 'Pending', 'Booth', NULL);

-- --------------------------------------------------------
-- Table: reservation_table_association
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS reservation_table_association (
    reservation_id INT NOT NULL,
    table_id INT NOT NULL,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (reservation_id, table_id),
    FOREIGN KEY (reservation_id) REFERENCES reservations(id) ON DELETE CASCADE,
    FOREIGN KEY (table_id) REFERENCES tables(id) ON DELETE CASCADE
);

-- Dummy associations
INSERT INTO reservation_table_association (reservation_id, table_id)
VALUES
(1, 1),
(2, 2);

-- --------------------------------------------------------
-- Table: operating_hours
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS operating_hours (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day_of_week VARCHAR(20) NOT NULL,
    opening_time TIME NOT NULL,
    closing_time TIME NOT NULL,
    created_on DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Dummy Operating Hours
INSERT INTO operating_hours (day_of_week, opening_time, closing_time)
VALUES
('Monday', '10:00:00', '22:00:00'),
('Tuesday', '10:00:00', '22:00:00'),
('Wednesday', '10:00:00', '22:00:00'),
('Thursday', '10:00:00', '22:00:00'),
('Friday', '10:00:00', '23:00:00'),
('Saturday', '09:00:00', '23:00:00'),
('Sunday', '09:00:00', '21:00:00');