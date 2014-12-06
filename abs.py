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
 "/bgnd/","bg"
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
okform=form.Form(
   form.Button("OK",type="OK",description="OK")
)
passform=form.Form(
   form.Password("Password",descrition="Password"),
   form.Button("submit",type="summit",description="OK")
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
}
Str='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
class bg:
 def GET(self):
   f=passform()
   return render.register("<p>Input in the password</p>", f)
 def POST(self):
   global tab
   input=web.input() ; #print input
   passw='smmap'
   if 'Password' in input :
      if input.Password!=passw :
         f=passform()
         return render.register("<p>Incorrect password</p>",f)
      else :
         f=regform()
         return render.register("<p>Input in the textbox</p>", f)
   if len(input.items())==1 :
      f=regform()
      return render.register("<p>Input in the textbox</p>", f)
   filename=input.Filename;serveraddr=input.server;pname=input.Program;
   rand=string.join(random.sample(Str,10))
   rand=rand.replace(' ','')
   suffix=filename.split('.')
   suffix='.'+suffix[len(suffix)-1]
   try:
      conttype= content_type[suffix]
   except KeyError:
      f=okform()
      return render.register("<p>File type error</p>",f)
   code=filename+'||'+serveraddr+'||'+rand;
   key='smmap' 
   key_len=len(key)
   for i in range(key_len, 16):
      key=key+'_'
   content_len=len(code)%16
   for i in range(content_len, 16):
      code=code+'_'
   obj=AES.new(key,AES.MODE_CBC,'')
   encrypt_code=obj.encrypt(code);
   url_code=base64.urlsafe_b64encode(encrypt_code);
   try :
     cur_tab=tab.cursor();cur_tab.execute("set names 'utf8'")
   except mysql.Error, e:
     print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
     if e.args[0]== 2006 :
       this.tab=mysql.connect('127.0.0.1','root','rtnet','abs',charset='utf8')
     raise web.seeother("/bgnd") 
   try: 
     cur_tab.execute("insert filelist(server,name,filename,mediatype,rand,\
     encryptstr,date) value('%s','%s','%s','%s','%s','%s','%s')" \
     %(serveraddr,pname, filename,conttype,rand,url_code, str(datetime.now())))
   except mysql.Error, e:
     exception=1
     print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
   cur_tab.execute("commit")
   cur_tab.close()
   content="<p>"+u"明文：  "+code.replace("_","")+"</p>";
   content=content+"<p>"+u"密文： "+url_code+"</p>"
   content=content+"<p>"+u"随机字符串： "+rand+"</p>"
   print content
   f=okform()
   return render.register(content,f)
class res:
   def GET(self,name) :
     global tab
     BUF=65535
     try:
       cur_tab=tab.cursor();cur_tab.execute("set names 'utf8'")
     except mysql.Error, e:
        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        if e.args[0]== 2006 :
             tab=mysql.connect('127.0.0.1','root','rtnet','abs',charset='utf8')
        raise web.seeother("/")
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
           raise web.seeother("/")
        else :
           cur_tab.execute("commit")
           cur_tab.close()
           f=okform()
           yield render.register("<p>URL parsing error.</p>",f)
     else :
       f=okform()
       yield render.register( "<p>URL error</p>",f)
   def POST(self):
       raise web.seeother("/")
class index:
    def GET(self):
      global tab
      try:
        cur_tab=tab.cursor();cur_tab.execute("set names 'utf8'")
      except mysql.Error, e:
        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        if e.args[0]==2006 :
          tab=mysql.connect('127.0.0.1','root','rtnet','abs',charset='utf8')
          raise web.seeother("/")
        else :
          f=okform()
          return render.register("<p>Internal Error, Try later</p>",f)
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

