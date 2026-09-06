import unittest
import json
import math
from app import app, get_client_ip, check_rate_limit
from database.db_helper import sanitize_fts_query

class TestSecurityHardening(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_security_headers_present(self):
        """Verify standard security headers and CSP are returned on all HTTP responses."""
        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(res.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertEqual(res.headers.get('X-XSS-Protection'), '1; mode=block')
        self.assertEqual(res.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertIn('Permissions-Policy', res.headers)
        self.assertIn('Content-Security-Policy', res.headers)
        csp = res.headers.get('Content-Security-Policy')
        self.assertIn("default-src 'self'", csp)
        self.assertIn("frame-ancestors 'self'", csp)

    def test_404_json_error_handler(self):
        """Verify 404 returns structured JSON without exposing server stack traces."""
        res = self.client.get('/api/non-existent-route-999')
        self.assertEqual(res.status_code, 404)
        data = json.loads(res.data)
        self.assertEqual(data.get('error'), 'Not Found')
        self.assertIn('message', data)

    def test_405_json_error_handler(self):
        """Verify method not allowed returns structured JSON."""
        res = self.client.get('/chat')  # Chat is POST only
        self.assertEqual(res.status_code, 405)
        data = json.loads(res.data)
        self.assertEqual(data.get('error'), 'Method Not Allowed')

    def test_client_ip_sanitization(self):
        """Verify get_client_ip sanitizes malicious injection headers."""
        class MockRequest:
            def __init__(self, forwarded=None, remote=None):
                self.headers = {'X-Forwarded-For': forwarded} if forwarded else {}
                self.remote_addr = remote

        # Valid IPv4
        req1 = MockRequest(forwarded="192.168.1.100, 10.0.0.1")
        self.assertEqual(get_client_ip(req1), "192.168.1.100")

        # Injection attempt with special characters
        req2 = MockRequest(forwarded="192.168.1.100<script>alert(1)</script>")
        self.assertEqual(get_client_ip(req2), "192.168.1.100cae1c")

        # Valid IPv6
        req3 = MockRequest(remote="2001:0db8:85a3:0000:0000:8a2e:0370:7334")
        self.assertEqual(get_client_ip(req3), "2001:0db8:85a3:0000:0000:8a2e:0370:7334")

    def test_lab_interpreter_nan_inf_defense(self):
        """Verify that NaN and Infinite float payloads are rejected with 400 Bad Request."""
        res = self.client.post('/api/interpret-lab', json={
            "test_key": "fasting_glucose",
            "value": "NaN"
        }, headers={'X-Benchmark-Test': 'true'})
        self.assertEqual(res.status_code, 400)

        res_inf = self.client.post('/api/interpret-lab', json={
            "test_key": "fasting_glucose",
            "value": "Infinity"
        }, headers={'X-Benchmark-Test': 'true'})
        self.assertEqual(res_inf.status_code, 400)

    def test_sanitize_fts_query_prevents_syntax_breakage(self):
        """Verify FTS query sanitization strips rogue SQL syntax and quotes tokens."""
        malicious_query = 'fever" OR 1=1 -- DROP TABLE health_info;'
        sanitized = sanitize_fts_query(malicious_query)
        self.assertNotIn("--", sanitized)
        self.assertNotIn(";", sanitized)
        self.assertIn('"fever"', sanitized)

    def test_rate_limiter_logic(self):
        """Verify sliding window rate-limiter rejects requests exceeding threshold."""
        test_ip = "192.0.2.1"
        # First request should pass
        allowed, _ = check_rate_limit(test_ip)
        self.assertTrue(allowed)
        # Immediate sub-cooldown request (0ms gap) should trigger rate limit
        allowed_fast, retry = check_rate_limit(test_ip)
        self.assertFalse(allowed_fast)
        self.assertGreaterEqual(retry, 1)

if __name__ == '__main__':
    unittest.main()
