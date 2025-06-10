from unittest import TestCase
import tempfile
import os

import app

class Tests(TestCase):
    def test_always_passes(self):
        self.assertTrue(True)

    def setUp(self):
        app.app.config['SECRET_KEY'] = "TEMP"
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()

            db = app.get_db()


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_login(self):
        with app.app.app_context():
            with self.app.session_transaction() as session:
                pass

