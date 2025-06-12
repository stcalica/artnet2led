import unittest
from unittest.mock import patch, MagicMock
import socket

# Import functions and constants from the main script
from WS2812B_DMX_IntegrationIController import (
    make_chase_frame, make_strobe_frame, assign_universes_to_fixtures, WHITE, BLACK, discover_wled, send_artnet
)

class TestPatterns(unittest.TestCase):
    def test_make_chase_frame(self):
        frame = make_chase_frame(5, 2, color=(1,2,3))
        expected = list(BLACK) * 2 + [1,2,3] + list(BLACK) * 2
        self.assertEqual(frame, expected)

    def test_make_strobe_frame_on(self):
        frame = make_strobe_frame(3, True)
        self.assertEqual(frame, list(WHITE) * 3)

    def test_make_strobe_frame_off(self):
        frame = make_strobe_frame(3, False)
        self.assertEqual(frame, list(BLACK) * 3)

    def test_assign_universes_to_fixtures(self):
        fixtures = [
            ('1.2.3.4', {'leds': {'count': 10}}),
            ('1.2.3.5', {'leds': {'count': 20}})
        ]
        result = assign_universes_to_fixtures(fixtures)
        self.assertEqual(result, [
            {'ip': '1.2.3.4', 'pixel_count': 10, 'universe': 0},
            {'ip': '1.2.3.5', 'pixel_count': 20, 'universe': 1}
        ])

class TestNetwork(unittest.TestCase):
    @patch('WS2812B_DMX_IntegrationIController.socket.socket')
    def test_discover_wled(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        response = (b'{"leds":{"count":42}}', ('192.168.1.100', 21324))
        mock_socket.recvfrom.side_effect = [response, socket.timeout()]
        result = discover_wled(timeout=0.1)
        self.assertEqual(result, [('192.168.1.100', {'leds': {'count': 42}})])

    @patch('WS2812B_DMX_IntegrationIController.socket.socket')
    def test_send_artnet(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        send_artnet('1.2.3.4', 2, [1,2,3,4,5,6], 0)
        self.assertTrue(mock_socket.sendto.called)

if __name__ == '__main__':
    unittest.main() 