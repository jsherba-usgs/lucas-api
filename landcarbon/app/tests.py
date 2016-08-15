import io
import sqlite3
import tempfile
import zipfile

from django.core import management
from django.core.files.storage import default_storage
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, TestCase

from . import models, views

def sqlcreate():
    b = io.BytesIO()
    management.call_command('sqlmigrate', 'app', '0002', stdout=b)
    return [line for line in b.getvalue().splitlines()
            if line.startswith('CREATE TABLE')][1:]

def make_simdb():
    fp = tempfile.NamedTemporaryFile(suffix='.db')
    with sqlite3.connect(fp.name) as conn:
        conn.executescript('; '.join(sqlcreate()))
    return fp


class ViewsTestCase(TestCase):
    def test_api_root(self):
        response = self.client.get('/api/')
        self.assertEqual(response.status_code, 200)


class SyncroSimTestCase(TestCase):
    def test_unpack(self):
        fp = make_simdb()
        bio = io.BytesIO()
        with zipfile.ZipFile(bio, 'w') as zf:
            zf.write(fp.name, 'project/db.ssim')
        upload = SimpleUploadedFile('up.zip', bio.getvalue())
        obj = models.SyncroSim(upload=upload)
        obj.save()
        self.assertTrue(default_storage.exists(obj.upload))
        fp.close()
