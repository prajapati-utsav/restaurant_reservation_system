import mysql.connector

# MySQL connection configuration
config = {
    'user': 'root',
    'password': 'Utsav@12345',  # replace with your password
    'host': 'localhost',
    'port': 3306
}

# Path to your SQL file
sql_file_path = 'sql/init_mysql.sql'

def run_sql_file():
    try:
        # Connect to MySQL server
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        print("Connected to MySQL server.")

        # Read SQL file
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_commands = f.read()

        # Split commands by semicolon
        for command in sql_commands.split(';'):
            command = command.strip()
            if command:
                cursor.execute(command)
        
        conn.commit()
        print("SQL file executed successfully.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    run_sql_file()