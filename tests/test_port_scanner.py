import unittest
from unittest.mock import patch, MagicMock
import socket
import queue
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import PortScanner

class TestPortScanner(unittest.TestCase):
    def setUp(self):
        self.scanner = PortScanner('localhost', 1, 100)

    def test_check_ip_valid_ip(self):
        with patch('socket.gethostbyname') as mock_gethostbyname:
            mock_gethostbyname.return_value = '127.0.0.1'
            self.scanner.target = '127.0.0.1'
            result = self.scanner.check_ip()
            self.assertEqual(result, '127.0.0.1')

    def test_check_ip_hostname(self):
        with patch('socket.gethostbyname') as mock_gethostbyname:
            mock_gethostbyname.return_value = '8.8.8.8'
            self.scanner.target = 'google.com'
            result = self.scanner.check_ip()
            self.assertEqual(result, '8.8.8.8')

    def test_check_ip_invalid_target(self):
        with patch('socket.gethostbyname', side_effect=socket.gaierror):
            self.scanner.target = 'invalid.nonexistent.domain'
            result = self.scanner.check_ip()
            self.assertIsNone(result)

    def test_scan_port_open(self):
        with patch('socket.socket') as mock_socket:
            instance = mock_socket.return_value.__enter__.return_value
            instance.connect_ex.return_value = 0
            instance.recv.return_value = b'Test Banner'

            self.scanner.open_ports = []

            self.scanner.scan_port('127.0.0.1', 80)

            self.assertEqual(len(self.scanner.open_ports), 1)
            self.assertEqual(self.scanner.open_ports[0]['port'], 80)
            self.assertEqual(self.scanner.open_ports[0]['banner'], 'Test Banner')

    def test_scan_port_closed(self):
        with patch('socket.socket') as mock_socket:
            instance = mock_socket.return_value.__enter__.return_value
            instance.connect_ex.return_value = 1 
            self.scanner.open_ports = []

            self.scanner.scan_port('127.0.0.1', 81)

            self.assertEqual(len(self.scanner.open_ports), 0)

    def test_worker_method(self):
        mock_queue = queue.Queue()
        mock_queue.put(80)
        mock_queue.put(443)
        
        with patch.object(self.scanner, 'scan_port') as mock_scan_port:
            self.scanner.thread_queue = mock_queue
            self.scanner.worker('127.0.0.1')

            self.assertEqual(mock_scan_port.call_count, 2)

def main():
    unittest.main()

if __name__ == '__main__':
    main()