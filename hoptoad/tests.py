import urllib2
from django.test import TestCase
from django.conf import settings

class BasicTests(TestCase):
    """Basic tests like setup and connectivity."""
    
    def test_api_key_present(self):
        self.assertTrue('HOPTOAD_API_KEY' in settings.get_all_members(),
            msg='The HOPTOAD_API_KEY setting is not present.')
        self.assertTrue(settings.HOPTOAD_API_KEY,
            msg='The HOPTOAD_API_KEY setting is blank.')
    
    def test_hoptoad_connectivity(self):
        try:
            ht = urllib2.urlopen('http://hoptoadapp.com/')
        except urllib2.HTTPError:
            self.fail(msg='Could not reach hoptoadapp.com -- are you online?')
        self.assertEqual(ht.code, 200, msg='hoptoadapp.com is broken.')
    
