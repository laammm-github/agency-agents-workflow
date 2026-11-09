"""Loopback-only teaching service; no production credentials or deployment."""
from contextlib import closing
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HTML = b"""<!doctype html><html lang="en"><meta charset="utf-8"><title>Team teaching app</title><h1>Tasks</h1><form><label for="title">Task title</label><input id="title" required maxlength="120"><button>Add task</button></form><p role="status"></p><ul></ul><script>
const status=document.querySelector('[role=status]');
async function refresh(){const r=await fetch('/api/tasks');if(!r.ok)throw Error('Service unavailable');const items=await r.json();document.querySelector('ul').replaceChildren(...items.map(x=>{const li=document.createElement('li');li.textContent=x.title;return li}));}
document.querySelector('form').onsubmit=async e=>{e.preventDefault();try{const r=await fetch('/api/tasks',{method:'POST',headers:{'Content-Type':'application/json','X-Teaching-Write':'allowed'},body:JSON.stringify({title:document.querySelector('input').value})});if(!r.ok)throw Error('Save failed');await refresh();status.textContent='Saved';}catch(e){status.textContent=e.message;}};refresh().catch(e=>status.textContent=e.message);
</script></html>"""

def make_server(database):
 with closing(sqlite3.connect(database, isolation_level=None)) as db:
  db.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY, title TEXT NOT NULL)')
 class Handler(BaseHTTPRequestHandler):
  def log_message(self, *_):pass
  def send(self, status, value, html=False):
   data=value if html else json.dumps(value).encode()
   self.send_response(status);self.send_header('Content-Type','text/html; charset=utf-8' if html else 'application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
  def do_GET(self):
   if self.path=='/health':return self.send(503 if self.server.fault else 200,{'version':self.server.version,'healthy':not self.server.fault})
   if self.path=='/':return self.send(200,HTML,True)
   if self.path!='/api/tasks':return self.send(404,{'error':'not found'})
   if self.server.fault:return self.send(503,{'error':'unavailable'})
   with closing(sqlite3.connect(database, isolation_level=None)) as db:rows=db.execute('SELECT id,title FROM tasks ORDER BY id').fetchall()
   self.send(200,[{'id':x[0],'title':x[1]} for x in rows])
  def do_POST(self):
   if self.path!='/api/tasks':return self.send(404,{'error':'not found'})
   if self.headers.get('X-Teaching-Write')!='allowed':return self.send(403,{'error':'teaching write denied'})
   try:
    length=int(self.headers.get('Content-Length','0'))
    if not 0<length<=4096:raise ValueError()
    title=json.loads(self.rfile.read(length))['title']
    if not isinstance(title,str) or not 0<len(title.strip())<=120:raise ValueError()
   except (ValueError,KeyError,TypeError):return self.send(400,{'error':'invalid input'})
   if self.server.fault:return self.send(503,{'error':'unavailable'})
   with closing(sqlite3.connect(database, isolation_level=None)) as db:cursor=db.execute('INSERT INTO tasks(title) VALUES (?)',(title.strip(),));identifier=cursor.lastrowid
   self.send(201,{'id':identifier})
 server=ThreadingHTTPServer(('127.0.0.1',0),Handler);server.version='v1';server.fault=False
 return server
