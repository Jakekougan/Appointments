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

    def testRegister(self):
        rv = self.app.post('/add_user', data=dict(
            fname='test',
            lname='user',
            pnum='123-456-7890',
            email='test@user.com',
            pwd='testpassword',
            cpwd='testpassword'
        ), follow_redirects=True)
        assert b'Account Created!' in rv.data

    def test_login_success(self):
        self.testRegister()
        rv = self.app.post('/user_auth', data=dict(
            email='test@user.com',
            pwd='testpassword'
        ), follow_redirects=True)
        assert b'Welcome test user!' in rv.data
        assert b'Your username or password is incorrect.' not in rv.data

    def test_login_failure_wrongPWD(self):
        self.testRegister()
        rv = self.app.post('/user_auth', data=dict(
            email='test@user.com',
            pwd='wrongpassword'
        ), follow_redirects=True)
        assert b'Your username or password is incorrect.' in rv.data
        assert b'Welcome test user!' not in rv.data

    def test_login_failure_wrongEmail(self):
        self.testRegister()
        rv = self.app.post('/user_auth', data=dict(
            email='wrong@user.com',
            pwd='testpassword'
        ), follow_redirects=True)
        assert b'Your username or password is incorrect.' in rv.data
        assert b'Welcome test user!' not in rv.data

    def test_logout(self):
        self.test_login_success()
        rv = self.app.post('/main', follow_redirects=True)
        assert b'You have been logged out.' in rv.data
        assert b'Welcome test user!' not in rv.data

    def test_add_appointment(self):
        self.test_login_success()
        rv = self.app.post('/add_appt', data=dict(
            date='2023-10-01',
            time='10:00 PM'
        ), follow_redirects=True)
        assert b'Appointment Confirmed' in rv.data

    def test_view_appointments(self):
        self.test_add_appointment()
        rv = self.app.get('/view', follow_redirects=True)
        assert b'2023-10-01' in rv.data
        assert b'10:00 PM' in rv.data
