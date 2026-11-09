import importlib.util
import json
import tempfile
import threading
import time
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from scripts.team import save, resume, digest
from test_team import sample
spec=importlib.util.spec_from_file_location("teaching_app",Path(__file__).parent/"fixtures/teaching_app.py")
app=importlib.util.module_from_spec(spec);spec.loader.exec_module(app)
class TeachingTests(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
  self.server=app.make_server(self.root/"app.db");self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start();self.url=f'http://127.0.0.1:{self.server.server_port}'
  # First request on Windows can race the fixture worker's serving loop.
  # Only retry the idempotent health preflight; never replay POST writes.
  for attempt in range(5):
   try:
    with urllib.request.urlopen(self.url+'/health',timeout=2) as response:
     self.assertEqual(response.status,200)
    break
   except (ConnectionAbortedError,ConnectionResetError,TimeoutError,urllib.error.URLError):
    if attempt==4:raise
    time.sleep(0.05)
 def tearDown(self):
  self.server.shutdown();self.server.server_close();self.thread.join();self.temp.cleanup()
 def call(self,path,data=None,allowed=True):
  headers={'Content-Type':'application/json'}
  if allowed:headers['X-Teaching-Write']='allowed'
  req=urllib.request.Request(self.url+path,data=json.dumps(data).encode() if data is not None else None,headers=headers)
  try:
   with urllib.request.urlopen(req,timeout=3) as r:return r.status,json.load(r)
  except urllib.error.HTTPError as e:return e.code,json.load(e)
 def test_new_project_api_database(self):
  self.assertEqual(self.call('/api/tasks',{'title':'Deliver feature'})[0],201)
  self.assertEqual(self.call('/api/tasks')[1][0]['title'],'Deliver feature')
 def test_invalid_input_and_authorization(self):
  self.assertEqual(self.call('/api/tasks',{'title':'x'},False)[0],403)
  self.assertEqual(self.call('/api/tasks',{'title':''})[0],400)
 def test_injection_stays_data(self):
  title="'); DROP TABLE tasks;--"
  self.assertEqual(self.call('/api/tasks',{'title':title})[0],201)
  self.assertEqual(self.call('/api/tasks')[1][0]['title'],title)
 def test_candidate_deployment_fault_and_rollback(self):
  self.server.version='v2';self.assertEqual(self.call('/health')[1]['version'],'v2')
  self.server.fault=True;self.assertEqual(self.call('/health')[0],503)
  self.server.version='v1';self.server.fault=False
  self.assertEqual(self.call('/health'),(200,{'version':'v1','healthy':True}))
 def test_checkpoint_new_session_revalidation(self):
  source=self.root/'user-file.txt';source.write_text('preserve user changes')
  state=sample(self.root);checkpoint=self.root/'checkpoint.json';save(checkpoint,state)
  reloaded=json.loads(checkpoint.read_text())
  self.assertTrue(resume(reloaded,self.root,{'user-file.txt':digest(source)})['authorization_recheck_required'])
  self.assertEqual(source.read_text(),'preserve user changes')
