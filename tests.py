import unittest
import tempfile
import os
import app

class Tests(unittest.TestCase):
    def test_always_passes(self):
        self.assertTrue(True)

    def setUp(self):
        '''Creates Temporary runtime for application.
        This is used to test the application without needing to run it in a server.
        Called at the beginning of each unit test.'''
        app.app.config['SECRET_KEY'] = "TEMP"
        self.db_fd, app.app.config['DATABASE'] = tempfile.mkstemp()
        app.app.testing = True
        self.app = app.app.test_client()
        with app.app.app_context():
            app.init_db()

            db = app.get_db()

    def tearDown(self):
        '''Closes the temporary database file and removes it.
        Called at the end of each unit test.'''
        os.close(self.db_fd)
        os.unlink(app.app.config['DATABASE'])

    def test_main_page(self):
        '''test the main page loads correctly'''
        rv = self.app.get('/')
        assert b'Login' in rv.data

    def testRegister(self):
        rv = self.app.post('/add_user', data=dict(
        rfname='test',
        rlname='user',
        rpnum='123-456-7890',
        remail='test@user.com',
        rpwd='Testpassword12!',
        rcpwd='Testpassword12!'
        ), follow_redirects=True)
        assert b'Password must contain at least one uppercase letter.' not in rv.data
        assert b'Password must contain at least one lowercase letter.' not in rv.data
        assert b'Password must contain at least one digit.' not in rv.data
        assert b'Password must contain at least one special character.' not in rv.data
        assert b'Password must be at least 8 characters long.' not in rv.data
        assert b'Account created!' in rv.data

    def test_login_success(self):
        self.testRegister()
        rv = self.app.post('/auth', data=dict(
            lemail='test@user.com',
            lpwd='Testpassword12!'
        ), follow_redirects=True)
        assert b'Login Successful! Welcome test user' in rv.data
        assert b'Your username or password is incorrect.' not in rv.data

    def test_login_failure_wrongPWD(self):
        self.testRegister()
        rv = self.app.post('/auth', data=dict(
            lemail='test@user.com',
            lpwd='wrongpassword'
        ), follow_redirects=True)
        assert b'Your username or password is incorrect!' in rv.data
        assert b'Login Successful! Welcome test user' not in rv.data

    def test_login_failure_wrongEmail(self):
        self.testRegister()
        rv = self.app.post('/auth', data=dict(
            lemail='wrong@user.com',
            lpwd='testpassword'
        ), follow_redirects=True)
        assert b'Your username or password is incorrect!' in rv.data
        assert b'Login Successful! Welcome test user' not in rv.data

    def test_account_creation_failure_badEmail(self):
        rv = self.app.post('/add_user', data=dict(
            rfname='test',
            rlname='user',
            rpnum='123-456-7890',
            remail='testuser.com',  # Missing '@'
            rpwd='Testpassword12!',
            rcpwd='Testpassword12!'
        ), follow_redirects=True)
        assert b'Please enter a valid email address!' in rv.data

    def test_account_creation_failure_passwords_mismatch(self):
        rv = self.app.post('/add_user', data=dict(
            rfname='test',
            rlname='user',
            rpnum='123-456-7890',
            remail='test@user.com',
            rpwd='Testpassword12!',
            rcpwd='Testpasswd12111!'
        ), follow_redirects=True)
        assert b'Passwords do not match!' in rv.data

    def test_account_creation_for_existing_email(self):
        self.testRegister()
        rv = self.app.post('/add_user', data=dict(
            rfname='test',
            rlname='user',
            rpnum='123-456-7890',
            remail='test@user.com',
            rpwd='Testpassword12!',
            rcpwd='Testpassword12!'
        ), follow_redirects=True)
        assert b'Email already exists!' in rv.data
        assert b'Account created!' not in rv.data

    def test_logout(self):
        self.test_login_success()
        rv = self.app.get('/', follow_redirects=True)
        assert b'Login' in rv.data
        assert b'Email' in rv.data
        assert b'Password' in rv.data
        assert b"Don't have an account?" in rv.data
        assert b'Welcome test user!' not in rv.data

    def test_add_appointment(self):
        self.test_login_success()
        rv = self.app.post('/add_appt', data=dict(
            date='2023-10-01',
            time='10:00 PM'
        ), follow_redirects=True)
        assert b'Appointment Confirmed' in rv.data

    def test_add_appointment_already_exists(self):
        self.test_add_appointment()
        rv = self.app.post('/add_appt', data=dict(
            date='2023-10-01',
            time='10:00 PM'
        ), follow_redirects=True)
        assert b'You already have an appointment scheduled for this time' in rv.data

    def test_view_appointments(self):
        self.test_add_appointment()
        rv = self.app.get('/view', follow_redirects=True)
        assert b'2023-10-01' in rv.data
        assert b'10:00 PM' in rv.data

    def test_delete_appointment(self):
        self.test_add_appointment()
        with app.app.app_context():
            db = app.get_db()
            appt = db.execute('SELECT id FROM appointments').fetchone()[0]
        rv = self.app.post('/edit', data=dict(
            check='1',
            appt_num=appt
        ), follow_redirects=True)
        rv = self.app.post('/confirm_edit', data=dict(
            confirm='yes',
            appt=appt
        ), follow_redirects=True)
        assert b'Changes confirmed!' in rv.data

    def test_edit_appointment(self):
        self.test_add_appointment()
        with app.app.app_context():
            db = app.get_db()
            appt = db.execute('SELECT id FROM appointments').fetchone()[0]
        rv = self.app.post('/edit', data=dict(
            check='0',
            appt_num=appt
        ), follow_redirects=True)
        rv = self.app.post('/edit_data', data=dict(
            appt=appt,
            oldTime='10:00 PM',
            oldDate='2023-10-01',
            time='11:00 PM',
            date='2023-10-02'
        ), follow_redirects=True)
        rv = self.app.post('/confirm_edit', data=dict(
            confirm='yes',
            appt=appt,
            time='11:00 PM',
            date='2023-10-02'
        ), follow_redirects=True)
        assert b'Changes confirmed!' in rv.data
        assert b'2023-10-02' in rv.data
        assert b'11:00 PM' in rv.data

    def test_abort_edit(self):
        self.test_add_appointment()
        with app.app.app_context():
            db = app.get_db()
            appt = db.execute('SELECT id FROM appointments').fetchone()[0]
        rv = self.app.post('/edit', data=dict(
            check='0',
            appt_num=appt
        ), follow_redirects=True)
        rv = self.app.post('/edit_data', data=dict(
            appt=appt,
            oldTime='10:00 PM',
            oldDate='2023-10-01',
            time='11:00 PM',
            date='2023-10-02'
        ), follow_redirects=True)
        rv = self.app.post('/confirm_edit', data=dict(
            confirm='no',
            appt=appt,
            time='11:00 PM',
            date='2023-10-02'
        ), follow_redirects=True)
        assert b'Changes aborted!' in rv.data
        assert b'2023-10-01' in rv.data
        assert b'10:00 PM' in rv.data
        assert b'2023-10-02' not in rv.data
        assert b'11:00 PM' not in rv.data


if __name__ == '__main__':
    unittest.main()

