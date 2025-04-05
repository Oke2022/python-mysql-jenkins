import unittest
from unittest.mock import patch, MagicMock
import os
import datetime
import xmlrunner  # This is needed for XML output compatible with Jenkins

# Import the script as a module (assuming it's saved as system_stats.py)
# If your script has a different name, adjust the import statements accordingly
import sys
sys.path.append('.')  # Add current directory to path if needed

class TestSystemStats(unittest.TestCase):
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('mysql.connector.connect')
    @patch('datetime.datetime')
    def test_data_logging(self, mock_datetime, mock_db_connect, mock_virtual_memory, mock_cpu_percent):
        """Test that system data is correctly collected and logged to the database."""
        # Setup mocks
        mock_cpu_percent.return_value = 45.2
        
        # Mock the virtual_memory object and its percent attribute
        mock_memory = MagicMock()
        mock_memory.percent = 72.5
        mock_virtual_memory.return_value = mock_memory
        
        # Mock datetime
        mock_now = MagicMock()
        test_timestamp = "2025-04-05 14:30:00"
        mock_now.strftime.return_value = test_timestamp
        mock_datetime.now.return_value = mock_now
        
        # Mock database connection and cursor
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_connection
        
        # Import and run the script's main function
        # We'll use exec to evaluate the script content instead of importing
        # This lets us test the script without requiring it to be structured as a module
        script_content = open('system_stats.py').read()
        # Replace the execution code with a function to be called
        script_content = script_content.replace('db = mysql.connector.connect', 
                                             'def main():\n    db = mysql.connector.connect')
        # Add indentation to the rest of the file
        script_content = script_content.replace('\n', '\n    ')
        # Add a return statement to get the output
        script_content = script_content + '\n    return timestamp, cpu, mem'
        
        # Create a namespace and execute the modified script
        namespace = {}
        exec(script_content, namespace)
        
        # Call the main function we created
        timestamp, cpu, mem = namespace['main']()
        
        # Verify the database interactions
        mock_cursor.execute.assert_called_once_with(
            "INSERT INTO stats (timestamp, cpu_usage, memory_usage) VALUES (%s, %s, %s)",
            (test_timestamp, 45.2, 72.5)
        )
        mock_connection.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_connection.close.assert_called_once()

    @patch('os.getenv')
    @patch('mysql.connector.connect')
    def test_database_connection(self, mock_db_connect, mock_getenv):
        """Test that database connection uses correct environment variables with fallbacks."""
        # Setup environment variable mocks
        def getenv_side_effect(var_name, default=None):
            env_vars = {
                "DB_HOST": "test-host",
                "DB_USER": "test-user",
                "DB_PASS": "test-password",
                "DB_NAME": "test-db"
            }
            return env_vars.get(var_name, default)
        
        mock_getenv.side_effect = getenv_side_effect
        
        # Mock the database connection
        mock_db_connect.return_value = MagicMock()
        
        # Test using exec approach to handle the script as-is
        script_content = open('system_stats.py').read()
        # Execute in a namespace with our mocks
        namespace = {'os': os, 'mysql': MagicMock(), 'psutil': MagicMock(), 
                    'datetime': MagicMock()}
        namespace['mysql'].connector.connect = mock_db_connect
        
        try:
            exec(script_content, namespace)
            # If we get here, the script ran without errors
            
            # Verify the connection was attempted with correct parameters
            mock_db_connect.assert_called_once_with(
                host="test-host",
                user="test-user",
                password="test-password",
                database="test-db"
            )
        except Exception as e:
            self.fail(f"Script execution failed: {e}")
    
    @patch('mysql.connector.connect')
    def test_database_connection_defaults(self, mock_db_connect):
        """Test that database connection uses default values when env vars are not set."""
        # Create a clean environment for testing defaults
        with patch.dict(os.environ, {}, clear=True):
            # Mock the database connection
            mock_db_connect.return_value = MagicMock()
            
            # Test using exec approach
            script_content = open('system_stats.py').read()
            # Execute in a namespace with our mocks
            namespace = {'os': os, 'mysql': MagicMock(), 'psutil': MagicMock(), 
                        'datetime': MagicMock()}
            namespace['mysql'].connector.connect = mock_db_connect
            
            try:
                exec(script_content, namespace)
                # If we get here, the script ran without errors
                
                # Verify the connection was attempted with default parameters
                mock_db_connect.assert_called_once_with(
                    host="172.31.31.235",
                    user="devops",
                    password="password",
                    database="syslogs"
                )
            except Exception as e:
                self.fail(f"Script execution failed: {e}")

if __name__ == '__main__':
    # Create target directory for test reports
    os.makedirs('target/surefire-reports', exist_ok=True)
    
    # Run tests with XMLRunner to generate reports in JUnit format
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output='target/surefire-reports'),
        failfast=False,
        buffer=False,
        catchbreak=False
    )