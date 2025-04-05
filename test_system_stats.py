import unittest
from unittest.mock import patch, MagicMock
import os
import datetime
import sys

# Try to import xmlrunner, but provide a fallback if it's not available
try:
    import xmlrunner
    XML_RUNNER_AVAILABLE = True
except ImportError:
    XML_RUNNER_AVAILABLE = False
    print("Warning: xmlrunner not available, using standard unittest runner")

# Add current directory to path
sys.path.append('.')

class TestSystemStats(unittest.TestCase):
    
    def setUp(self):
        # Verify the script file exists
        self.script_file = 'system_stats.py'
        self.assertTrue(os.path.exists(self.script_file), f"Script file {self.script_file} does not exist")
        
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
        
        # Create test globals namespace with mocks
        test_globals = {
            'psutil': MagicMock(),
            'mysql': MagicMock(),
            'datetime': mock_datetime,
            'os': os,
            'print': print  # Allow print statements to work
        }
        test_globals['psutil'].cpu_percent = mock_cpu_percent
        test_globals['psutil'].virtual_memory = mock_virtual_memory
        test_globals['mysql'].connector.connect = mock_db_connect
        
        # Read the script content
        with open(self.script_file, 'r') as f:
            script_content = f.read()
        
        # Execute the script in our namespace with mocks
        try:
            exec(script_content, test_globals)
            
            # Explicitly call the main function
            test_globals['main']()
            
            # Check that database operations were performed correctly
            mock_cursor.execute.assert_called_once_with(
                "INSERT INTO stats (timestamp, cpu_usage, memory_usage) VALUES (%s, %s, %s)",
                (test_timestamp, 45.2, 72.5)
            )
            mock_connection.commit.assert_called_once()
            mock_cursor.close.assert_called_once()
            mock_connection.close.assert_called_once()
            
        except Exception as e:
            self.fail(f"Script execution failed: {e}")

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
        mock_connection = MagicMock()
        mock_cursor = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_connection
        
        # Create test globals namespace with mocks
        test_globals = {
            'psutil': MagicMock(),
            'mysql': MagicMock(),
            'datetime': MagicMock(),
            'os': os,
            'print': print
        }
        test_globals['os'].getenv = mock_getenv
        test_globals['mysql'].connector.connect = mock_db_connect
        
        # Read the script content
        with open(self.script_file, 'r') as f:
            script_content = f.read()
        
        # Execute the script in our namespace with mocks
        try:
            exec(script_content, test_globals)
            
            # Explicitly call the main function
            test_globals['main']()
            
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
            mock_connection = MagicMock()
            mock_cursor = MagicMock()
            mock_connection.cursor.return_value = mock_cursor
            mock_db_connect.return_value = mock_connection
            
            # Create test globals namespace with mocks
            test_globals = {
                'psutil': MagicMock(),
                'mysql': MagicMock(),
                'datetime': MagicMock(),
                'os': os,
                'print': print
            }
            test_globals['mysql'].connector.connect = mock_db_connect
            
            # Read the script content
            with open(self.script_file, 'r') as f:
                script_content = f.read()
            
            # Execute the script in our namespace with mocks
            try:
                exec(script_content, test_globals)
                
                # Explicitly call the main function
                test_globals['main']()
                
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
    
    # Run tests with XMLRunner if available, otherwise use standard runner
    if XML_RUNNER_AVAILABLE:
        unittest.main(
            testRunner=xmlrunner.XMLTestRunner(output='target/surefire-reports'),
            failfast=False,
            buffer=False,
            catchbreak=False
        )
    else:
        unittest.main()