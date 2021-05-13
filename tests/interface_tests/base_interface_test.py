import unittest

from modules.interface.blockchain import app, node


class BaseInterfaceTest(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['DEBUG'] = False
        self.client = app.test_client()
        node.initialize()

    def tearDown(self):
        self.client = None
        node.clear()
