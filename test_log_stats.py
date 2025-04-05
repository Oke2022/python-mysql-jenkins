import unittest
import os

class TestSystemStats(unittest.TestCase):
    """Basic tests for system_stats.py that don't require external dependencies."""
    
    def test_script_exists(self):
        """Verify that the system_stats.py file exists."""
        self.assertTrue(os.path.exists("system_stats.py"), 
                       "system_stats.py file exists")
    
    def test_script_has_required_imports(self):
        """Verify that the script contains the required import statements."""
        with open("system_stats.py", "r") as file:
            content = file.read()
            self.assertIn("import psutil", content, 
                         "Script should import psutil")
            self.assertIn("import mysql.connector", content, 
                         "Script should import mysql.connector")
            self.assertIn("import datetime", content, 
                         "Script should import datetime")
    
    def test_script_has_database_connection(self):
        """Verify that the script attempts to connect to a database."""
        with open("system_stats.py", "r") as file:
            content = file.read()
            self.assertIn("mysql.connector.connect", content, 
                         "Script should connect to MySQL database")
            self.assertIn("INSERT INTO", content, 
                         "Script should contain an INSERT statement")

if __name__ == "__main__":
    # Create directory for test reports
    os.makedirs("target/surefire-reports", exist_ok=True)
    
    # Run the tests
    unittest.main()