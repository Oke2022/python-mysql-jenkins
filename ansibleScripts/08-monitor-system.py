import psutil
import mysql.connector
import socket

# Database Configuration
DB_HOST = "your-mysql-server-ip"
DB_USER = "monitoring_user"
DB_PASSWORD = "monitoring_password"
DB_NAME = "system_monitor"

def get_system_stats():
    """Collect system statistics."""
    hostname = socket.gethostname()
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    return hostname, cpu_usage, memory_usage

def insert_stats_to_db():
    """Insert system stats into MySQL database."""
    hostname, cpu_usage, memory_usage = get_system_stats()

    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()

        query = """
        INSERT INTO system_stats (hostname, cpu_usage, memory_usage) 
        VALUES (%s, %s, %s);
        """
        cursor.execute(query, (hostname, cpu_usage, memory_usage))
        conn.commit()
        print(f"Inserted: {hostname}, CPU: {cpu_usage}%, Memory: {memory_usage}%")

        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        print(f"Error: {err}")

if __name__ == "__main__":
    insert_stats_to_db()
