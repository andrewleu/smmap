# -*- coding: utf-8 -*-  
import web
import os
import string
import base64
import sys
import random
from Crypto.Cipher import AES
import urllib, urllib2
import MySQLdb as mysql
from datetime import datetime
urls= (
 "/", "index",
 "/res/(.+)", "res",
 "/bg/","bg"
 )
from web import form
reload(sys)
sys.setdefaultencoding("utf-8")
tab=mysql.connect('127.0.0.1','root','rtnet','abs',charset='utf8')
render=web.template.render('templates')
regform=form.Form(
   form.Textbox("Program", description="Program name"),
   form.Textbox("Filename",description="File name"),
   form.Textbox("server",description="Server address"),
   form.Button("submit",type="summit",description="upload")
)
content_type={'.movie'	: 'video/x-sgi-movie', 
  '.wvx'	: 'video/x-ms-wvx', 
  '.wmx'	: 'video/x-ms-wmx',
  '.wmv'	: 'video/x-ms-wmv',
  '.wm'	: 'video/x-ms-wm',
  '.asf'	: 'video/x-ms-asf',
  '.asx'	: 'video/x-ms-asf',
  '.mpa'	: 'video/x-mpg',
  '.m2v'	: 'video/x-mpeg',
  '.mps'	: 'video/x-mpeg',
  '.m1v'	: 'video/x-mpeg',
  '.mpe'	: 'video/x-mpeg',
  '.ivf'	: 'video/x-ivf',
  '.rv'	: 'video/vnd.rn-realvideo',
  '.mpeg'	: 'video/mpg',
  '.mpv'	: 'video/mpg',
  '.mpg'	: 'video/mpg',
  '.m4e'	: 'video/mp4',
  '.mp4'	: 'video/mp4',
  '.mp2v'	: 'video/mpeg',
  '.mpv2'	: 'video/mpeg',
  '.avi'	: 'video/avi',
  '.mkv'	: 'video/x-matroska'
}
Str='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
class bg:
 def GET(self):
   f=regform()
   return render.register(f)
 def POST(self):
   input=web.input()
   filename=input.Filename;serveraddr=input.server;pname=input.Program;print pname
   rand=string.join(random.sample(Str,10))
   rand=rand.replace(' ','')
   suffix=filename.split('.')
   suffix='.'+suffix[len(suffix)-1]
   try:
      conttype= content_type[suffix]
   except e:
      return "File type error"
   code=filename+'||'+serveraddr+'||'+rand;
   key='absac' 
   key_len=len(key)
   for i in range(key_len, 16):
      key=key+'_'
   content_len=len(code)%16
   for i in range(content_len, 16):
      code=code+'_'
   obj=AES.new(key,AES.MODE_CBC,'')
   encrypt_code=obj.encrypt(code);
   url_code=base64.urlsafe_b64encode(encrypt_code);
   cur_tab=tab.cursor();cur_tab.execute("set names 'utf8'")
   try: 
     cur_tab.execute("insert filelist(server,name,filename,mediatype,rand,\
     encryptstr,date) value('%s','%s','%s','%s','%s','%s','%s')" \
     %(serveraddr,pname, filename,conttype,rand,url_code, str(datetime.now())))
   except mysql.Error, e:
     exception=1
     print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
   cur_tab.execute("commit")
   cur_tab.close()
   f=regform()
   return render.register(f)
class res:
   def GET(self,name) :
     BUF=65535
     cur_tab=tab.cursor();cur_tab.execute("set names 'utf8'")
     name=name.split("&"); lenerror=0;queryerror=0
     if len(name)==2 :
        query=cur_tab.execute("select filename,mediatype from filelist where rand='%s' and encryptstr='%s'" % (name[0], name[1]))
        if query!=0 :
           result=cur_tab.fetchone();
           filename=result[0]
           filepath=os.path.join('/opt',filename)
           web.header('Content-Type', result[1])
           web.header('Transfer-Encoding','chunked')
           f=open(filepath,'r')
           cur_tab.execute("commit")
           cur_tab.close()
           while True:
             c=f.read(BUF)
             if c :
               yield c
             else :
               break
           f.close();
           raise web.redirect("/")
        else :
           cur_tab.execute("commit")
           cur_tab.close()
           yield "URL parsing error"
     else :
       yield "URL error"
class index:
    def GET(self):
      cur_tab=tab.cursor();cur_tab.execute("set names 'utf8'")
      cur_tab.execute("select rand, encryptstr,name from filelist")
      lines=cur_tab.fetchall();cur_tab.execute("commit");cur_tab.close();
      return render.firstpg(lines)
if __name__ == "__main__":
    app = web.application(urls, globals())
    try:
      app.run()
    except KeyboardInterrupt :
      tab.close()
      print "exitting"
    finally :
      exit(0)

