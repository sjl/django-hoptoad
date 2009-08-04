from django.test import TestCase
from django.conf import settings

class BasicTests(TestCase):
    """Basic tests like setup and connectivity."""
    
    def test_api_key_present(self):
        self.assertTrue('HOPTOAD_API_KEY' in settings.get_all_members(),
            msg='The HOPTOAD_API_KEY setting is not present.')
        self.assertTrue(settings.HOPTOAD_API_KEY,
            msg='The HOPTOAD_API_KEY setting is blank.')
    
        