"""
PostgreSQL Database Setup Script
Initializes the database schema for the Petroleum Price Forecasting application
"""

import psycopg2
from psycopg2 import sql, Error
import sys
from datetime import datetime

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'forecast_DB',
    'user': 'postgres',
    'password': 'wense2703'  # Change this to your PostgreSQL password
}

# SQL statements to create tables
CREATE_TABLES_SQL = """
-- Admin table
CREATE TABLE IF NOT EXISTS admin (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) DEFAULT 'admin',
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Logs table (for tracking logins)
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    user_type VARCHAR(20) NOT NULL,
    user_id INT,
    username VARCHAR(255),
    email VARCHAR(255),
    login_status VARCHAR(20) NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    login_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    logout_time TIMESTAMP,
    session_duration INT,
    failure_reason VARCHAR(255)
);

-- Price data table
CREATE TABLE IF NOT EXISTS current_price (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    price DECIMAL(10, 2) NOT NULL,
    source VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forecasts table
CREATE TABLE IF NOT EXISTS forecasts (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id) ON DELETE SET NULL,
    forecast_date DATE NOT NULL,
    forecast_period_months INT NOT NULL,
    model_version VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Forecast predictions table
CREATE TABLE IF NOT EXISTS forecast_predictions (
    id SERIAL PRIMARY KEY,
    forecast_id INT NOT NULL REFERENCES forecasts(id) ON DELETE CASCADE,
    prediction_date DATE NOT NULL,
    predicted_price DECIMAL(10, 2),
    lower_bound DECIMAL(10, 2),
    upper_bound DECIMAL(10, 2)
);

-- Model metadata table
CREATE TABLE IF NOT EXISTS model_metadata (
    id SERIAL PRIMARY KEY,
    version VARCHAR(50) UNIQUE NOT NULL,
    training_rows INT,
    last_training_date DATE,
    rmse DECIMAL(10, 4),
    mape DECIMAL(10, 4),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_admin_username ON admin(username);
CREATE INDEX IF NOT EXISTS idx_admin_email ON admin(email);
CREATE INDEX IF NOT EXISTS idx_admin_active ON admin(active);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_logs_user_type ON logs(user_type);
CREATE INDEX IF NOT EXISTS idx_logs_user_id ON logs(user_id);
CREATE INDEX IF NOT EXISTS idx_logs_username ON logs(username);
CREATE INDEX IF NOT EXISTS idx_logs_login_time ON logs(login_time);
CREATE INDEX IF NOT EXISTS idx_logs_login_status ON logs(login_status);
CREATE INDEX IF NOT EXISTS idx_current_price_date ON current_price(date);
CREATE INDEX IF NOT EXISTS idx_forecasts_user_id ON forecasts(user_id);
CREATE INDEX IF NOT EXISTS idx_forecasts_created_at ON forecasts(created_at);
CREATE INDEX IF NOT EXISTS idx_forecast_predictions_forecast_id ON forecast_predictions(forecast_id);
CREATE INDEX IF NOT EXISTS idx_forecast_predictions_date ON forecast_predictions(prediction_date);
CREATE INDEX IF NOT EXISTS idx_model_metadata_version ON model_metadata(version);
"""


def connect_to_database(config):
    """Establish connection to PostgreSQL database"""
    try:
        connection = psycopg2.connect(**config)
        print("✓ Successfully connected to PostgreSQL database")
        return connection
    except Error as e:
        print(f"✗ Error connecting to database: {e}")
        return None


def create_database_if_not_exists(db_config):
    """Create the database if it doesn't exist"""
    try:
        # Connect to default 'postgres' database first
        temp_config = db_config.copy()
        temp_config['database'] = 'postgres'
        
        connection = psycopg2.connect(**temp_config)
        connection.autocommit = True
        cursor = connection.cursor()
        
        # Check if database exists
        cursor.execute(
            f"SELECT 1 FROM pg_database WHERE datname = '{db_config['database']}';"
        )
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(
                sql.SQL("CREATE DATABASE {}").format(
                    sql.Identifier(db_config['database'])
                )
            )
            print(f"✓ Database '{db_config['database']}' created successfully")
        else:
            print(f"✓ Database '{db_config['database']}' already exists")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"✗ Error creating database: {e}")
        return False
    
    return True


def execute_sql_script(connection, script):
    """Execute SQL script with multiple statements"""
    try:
        cursor = connection.cursor()
        
        # Split script into individual statements
        statements = script.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement:  # Skip empty statements
                cursor.execute(statement)
        
        connection.commit()
        print("✓ All tables created successfully")
        cursor.close()
        return True
        
    except Error as e:
        print(f"✗ Error executing SQL: {e}")
        connection.rollback()
        return False


def insert_sample_data(connection):
    """Insert sample data for testing"""
    try:
        cursor = connection.cursor()
        
        # Insert sample admin user
        cursor.execute("""
            INSERT INTO admin (username, email, password_hash, role, active)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (username) DO NOTHING;
        """, ('admin_demo', 'admin@example.com', 'hashed_password_admin_demo', 'superadmin', True))
        
        # Insert sample regular user
        cursor.execute("""
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
            ON CONFLICT (username) DO NOTHING;
        """, ('demo_user', 'demo@example.com', 'hashed_password_demo'))
        
        print("✓ Sample admin and user inserted (optional)")
        
        connection.commit()
        cursor.close()
        
    except Error as e:
        print(f"⚠ Warning: Could not insert sample data: {e}")
        connection.rollback()


def verify_tables(connection):
    """Verify all tables were created"""
    try:
        cursor = connection.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        
        tables = cursor.fetchall()
        
        print("\n" + "="*50)
        print("Tables created in the database:")
        print("="*50)
        for table in tables:
            print(f"  • {table[0]}")
        
        cursor.close()
        
    except Error as e:
        print(f"✗ Error verifying tables: {e}")


def main():
    """Main setup function"""
    print("="*60)
    print("PostgreSQL Database Setup for Petroleum Price Forecasting")
    print("="*60)
    print()
    
    # Verify credentials
    print("Database Configuration:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Database: {DB_CONFIG['database']}")
    print()
    
    # Check if user wants to proceed
    response = input("Proceed with setup? (yes/no): ").lower().strip()
    if response not in ('yes', 'y'):
        print("Setup cancelled.")
        sys.exit(0)
    
    print()
    
    # Step 1: Create database if it doesn't exist
    print("Step 1: Creating database if needed...")
    if not create_database_if_not_exists(DB_CONFIG):
        print("Failed to create database. Exiting.")
        sys.exit(1)
    
    print()
    
    # Step 2: Connect to the database
    print("Step 2: Connecting to database...")
    connection = connect_to_database(DB_CONFIG)
    if not connection:
        print("Failed to connect to database. Exiting.")
        sys.exit(1)
    
    print()
    
    # Step 3: Create tables
    print("Step 3: Creating tables...")
    if not execute_sql_script(connection, CREATE_TABLES_SQL):
        print("Failed to create tables. Exiting.")
        connection.close()
        sys.exit(1)
    
    print()
    
    # Step 4: Insert sample data (optional)
    print("Step 4: Inserting sample data...")
    insert_sample_data(connection)
    
    print()
    
    # Step 5: Verify tables
    print("Step 5: Verifying setup...")
    verify_tables(connection)
    
    print()
    print("="*60)
    print("✓ Database setup completed successfully!")
    print("="*60)
    print()
    print("Next steps:")
    print("  1. Update DB_CONFIG in this script with your credentials")
    print("  2. Use SQLAlchemy ORM models in your Flask app")
    print("  3. Test the connection with your application")
    print()
    
    connection.close()


if __name__ == "__main__":
    main()
