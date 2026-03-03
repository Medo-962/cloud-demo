-- ==============================
-- ADMINS
-- ==============================
CREATE TABLE admins (
    adminID INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    passwordHash VARCHAR(255) NOT NULL,
    isActive BOOLEAN DEFAULT TRUE,
    lastLogin DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE = InnoDB;

-- ==============================
-- CARS
-- ==============================
CREATE TABLE cars (
    vehicleID INT AUTO_INCREMENT PRIMARY KEY,
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    licensePlate VARCHAR(20) NOT NULL UNIQUE,
    color VARCHAR(30),
    year INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB;

-- ==============================
-- DRIVERS
-- ==============================
CREATE TABLE drivers (
    driverID INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    phoneNumber VARCHAR(20) UNIQUE NOT NULL,
    passwordHash VARCHAR(255) NOT NULL,
    fullName VARCHAR(100) NOT NULL,
    activeVehicleID INT NULL,
    rating DECIMAL(2, 1) DEFAULT 5.0,
    totalRides INT DEFAULT 0,
    isAvailable BOOLEAN DEFAULT TRUE,
    isVerified BOOLEAN DEFAULT FALSE,
    isSuspended BOOLEAN DEFAULT FALSE,
    currentLat DECIMAL(10, 8) NULL,
    currentLng DECIMAL(11, 8) NULL,
    failedLoginAttempts INT DEFAULT 0,
    lastLogin DATETIME,
    lastOnline DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (activeVehicleID) REFERENCES cars (vehicleID) ON DELETE SET NULL,
    INDEX idx_email (email),
    INDEX idx_phone (phoneNumber)
) ENGINE = InnoDB;

-- ==============================
-- DRIVER_VEHICLES (Linking Table)
-- ==============================
CREATE TABLE driver_vehicles (
    driverID INT NOT NULL,
    vehicleID INT NOT NULL,
    isPrimary BOOLEAN DEFAULT FALSE,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (driverID, vehicleID),
    FOREIGN KEY (driverID) REFERENCES drivers (driverID) ON DELETE CASCADE,
    FOREIGN KEY (vehicleID) REFERENCES cars (vehicleID) ON DELETE CASCADE
) ENGINE = InnoDB;

-- ==============================
-- RIDERS
-- ==============================
CREATE TABLE riders (
    riderID INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(100) UNIQUE NOT NULL,
    phoneNumber VARCHAR(20) UNIQUE NOT NULL,
    passwordHash VARCHAR(255) NOT NULL,
    fullName VARCHAR(100) NOT NULL,
    rating DECIMAL(2, 1) DEFAULT 5.0,
    totalRides INT DEFAULT 0,
    isSuspended BOOLEAN DEFAULT FALSE,
    failedLoginAttempts INT DEFAULT 0,
    lastLogin DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_phone (phoneNumber)
) ENGINE = InnoDB;

-- ==============================
-- RIDES
-- ==============================
CREATE TABLE rides (
    rideID INT AUTO_INCREMENT PRIMARY KEY,
    riderID INT NOT NULL,
    driverID INT NULL,
    pickupAddress VARCHAR(150) NOT NULL,
    dropoffAddress VARCHAR(150) NOT NULL,
    pickupLat DECIMAL(10, 8) NOT NULL,
    pickupLng DECIMAL(11, 8) NOT NULL,
    dropoffLat DECIMAL(10, 8) NOT NULL,
    dropoffLng DECIMAL(11, 8) NOT NULL,
    distanceKM DECIMAL(6, 2),
    estimatedPrice DECIMAL(10, 2),
    totalPrice DECIMAL(10, 2),
    rideStatus ENUM(
        'requested',
        'accepted',
        'arrived',
        'in_progress',
        'completed',
        'cancelled'
    ) DEFAULT 'requested',
    paymentMethod ENUM('cash', 'card') DEFAULT 'cash',
    requested_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    accepted_at DATETIME NULL,
    started_at DATETIME NULL,
    completed_at DATETIME NULL,
    cancelled_at DATETIME NULL,
    FOREIGN KEY (riderID) REFERENCES riders (riderID) ON DELETE CASCADE,
    FOREIGN KEY (driverID) REFERENCES drivers (driverID) ON DELETE SET NULL,
    INDEX idx_rider (riderID),
    INDEX idx_driver (driverID),
    INDEX idx_status (rideStatus)
) ENGINE = InnoDB;

-- ==============================
-- RIDE TRACKING
-- ==============================
CREATE TABLE ride_tracking (
    trackingID INT AUTO_INCREMENT PRIMARY KEY,
    rideID INT NOT NULL,
    status VARCHAR(50) NOT NULL,
    updatedBy ENUM(
        'system',
        'driver',
        'rider',
        'admin'
    ) NOT NULL,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rideID) REFERENCES rides (rideID) ON DELETE CASCADE
) ENGINE = InnoDB;

-- ==============================
-- RATINGS
-- ==============================
CREATE TABLE ratings (
    ratingID INT AUTO_INCREMENT PRIMARY KEY,
    rideID INT NOT NULL,
    givenBy ENUM('rider', 'driver') NOT NULL,
    score DECIMAL(2, 1) CHECK (score BETWEEN 1 AND 5),
    review TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rideID) REFERENCES rides (rideID) ON DELETE CASCADE
) ENGINE = InnoDB;

-- ==============================
-- LOGIN SESSIONS
-- ==============================
CREATE TABLE rider_sessions (
    sessionID INT AUTO_INCREMENT PRIMARY KEY,
    riderID INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    ipAddress VARCHAR(45),
    deviceInfo VARCHAR(255),
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (riderID) REFERENCES riders (riderID) ON DELETE CASCADE,
    INDEX idx_token (token)
) ENGINE = InnoDB;

CREATE TABLE driver_sessions (
    sessionID INT AUTO_INCREMENT PRIMARY KEY,
    driverID INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    ipAddress VARCHAR(45),
    deviceInfo VARCHAR(255),
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driverID) REFERENCES drivers (driverID) ON DELETE CASCADE,
    INDEX idx_token (token)
) ENGINE = InnoDB;

CREATE TABLE admin_sessions (
    sessionID INT AUTO_INCREMENT PRIMARY KEY,
    adminID INT NOT NULL,
    token VARCHAR(255) NOT NULL,
    ipAddress VARCHAR(45),
    deviceInfo VARCHAR(255),
    expires_at DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (adminID) REFERENCES admins (adminID) ON DELETE CASCADE,
    INDEX idx_token (token)
) ENGINE = InnoDB;