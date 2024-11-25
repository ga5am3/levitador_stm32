import unittest
from unittest.mock import patch, MagicMock
from serial_handler import SerialHandler

# test_serial_handler.py


class TestSerialHandler(unittest.TestCase):

    @patch('serial_handler.list_ports.comports')
    @patch('serial_handler.serial.Serial')
    def test_initialize_port(self, mock_serial, mock_comports):
        mock_comports.return_value = [MagicMock(name='COM1'), MagicMock(name='COM2')]
        mock_serial_instance = mock_serial.return_value

        handler = SerialHandler()
        with patch('builtins.input', return_value='0'):
            result = handler.initialize_port()
        
        self.assertTrue(result)
        mock_serial.assert_called_once_with(port='COM1', baudrate=BAUDRATE, timeout=TIMEOUT)
        mock_serial_instance.flushInput.assert_called_once()
        mock_serial_instance.flushOutput.assert_called_once()

    @patch('serial_handler.serial.Serial')
    def test_read_data(self, mock_serial):
        mock_serial_instance = mock_serial.return_value
        mock_serial_instance.readline.return_value = b'123.45|some_other_data\x00\n'

        handler = SerialHandler()
        handler.port = mock_serial_instance
        result = handler.read_data()

        self.assertEqual(result, 123.45)
        mock_serial_instance.flush.assert_called_once()

    @patch('serial_handler.serial.Serial')
    def test_write_data(self, mock_serial):
        mock_serial_instance = mock_serial.return_value

        handler = SerialHandler()
        handler.port = mock_serial_instance
        handler.write_data(678.90)

        mock_serial_instance.write.assert_called_once_with(b'678.9')

if __name__ == '__main__':
    unittest.main()