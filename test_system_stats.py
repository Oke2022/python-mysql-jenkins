import unittest
import system_stats
from unittest.mock import patch, MagicMock
from io import StringIO
import sys

class SystemStatsTest(unittest.TestCase):
    
    @patch('mysql.connector.connect')
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    def test_main_function(self, mock_virtual_memory, mock_cpu_percent, mock_db_connect):
        # Mock the CPU and memory values
        mock_cpu_percent.return_value = 50.0
        mock_memory = MagicMock()
        mock_memory.percent = 60.0
        mock_virtual_memory.return_value = mock_memory
        
        # Mock the database connection
        mock_cursor = MagicMock()
        mock_db = MagicMock()
        mock_db.cursor.return_value = mock_cursor
        mock_db_connect.return_value = mock_db
        
        # Capture the standard output
        captured_output = StringIO()
        sys.stdout = captured_output
        
        # Run the function
        system_stats.main()
        
        # Restore standard output
        sys.stdout = sys.__stdout__
        
        # Verify the database interaction
        self.assertTrue(mock_cursor.execute.called, "Database query was not executed")
        self.assertTrue(mock_db.commit.called, "Database commit was not called")
        
        # Verify output contains CPU and memory values
        output = captured_output.getvalue()
        self.assertIn("CPU: 50.0%", output)
        self.assertIn("MEM: 60.0%", output)

if __name__ == '__main__':
    unittest.main()