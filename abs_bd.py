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
import time
import telnetlib
urls= (
 "/", "index",
 "/res/(.+)", "res",
 "/bgnd/","bg",
 "/poor", "poor",
 "/auth", "auth"
 )
from web import form
reload(sys)
sys.setdefaultencoding("utf8")
def open_database() :
  table=mysql.connect('172.24.20.68','root','rtnet','abs',charset='utf8')
  return table
render=web.template.render('templates')
regform=form.Form(
   form.Textbox("Program", description="片名"),
   form.Textbox("Filename",description="文件名"),
   form.Textbox("Server",description="服务器地址"),
   form.Dropdown("Bandwith", ['10M','40M'], '10M',description="带宽"),
   form.Button("submit",type="summit",description="upload")
)
okform=form.Form(
   form.Button("OK",type="OK",description="OK")
)
authform=form.Form (
   form.Textbox("URL", description="输入URL"),
   form.Password("Key",id="加密密钥"),
   form.Button("OK",type="summit",description="OK")
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
key='smmap'

class auth :
   def GET(self):
     f=authform()
     return render.warning("URL验证","",f)
   def POST(self) :
     input=web.input();print input
     if "Key" not in input :
        raise web.seeother("/auth");
     if "URL" not in input :
        raise web.seeother("/auth")
     inputurl=input.URL;passwd=input.Key
     tag =inputurl.split("/");
     tag=tag[len(tag)-1]
     tag=tag.split("&")
     if len(tag)!=2 :
       f=okform()
       return render.warning("Input Error","" ,f)
     rand=tag[0];encryptstr=tag[1];print rand;print encryptstr
     key_len=len(passwd)
     if key_len>=16 :
        passwd=passwd[0:16]
     else:
       for i in range(key_len%16, 16):
         passwd=passwd+'_'
     obj=AES.new(passwd,AES.MODE_CBC,b'0000000000000000')
     try:
       code=obj.decrypt(base64.urlsafe_b64decode(encryptstr.encode()))
     except:
        f=okform()
        return render.warning("验证不正确","",f)
     codeparts=code.split("||");
     if len(codeparts)==4 :
        if codeparts[2].replace("_","")==rand:
           content="<p>"+u"明文：  "+code.rstrip("_")+"</p>";
           content=content+"<p>"+u"密文： "+tag[1]+"</p>"
           content=content+"<p>"+u"随机字符串： "+rand+"</p>"
           f=okform()
           return render.warning("验证正确",content,f)
     f=okform()
     return render.warning("验证不正确","",f) 
class bg : #background maintainance

 def GET(self):
   f=passform();print "init";
   print self
   return render.register("<p>按项目填写</p>", f)
 def POST(self):
   print self
   input=web.input() ; #print self.veryfied
   passw='smmap'       #very simple authentication
   if 'Password' in input :
      if input.Password!=passw :
         f=passform()
         return render.register("<p>Incorrect password</p>",f)
      else :
         f=regform();
         self.veryfied=1;
         return render.register("<p>按项目填写</p>", f)
    
   #if self.veryfied==0 :
    # f=passform()
    # return render.register("<p>按项目填写</p>", f)
   if len(input.items())==1 :
      f=regform()
      return render.register("<p>Input in the textbox</p>", f)
   filename=input.Filename; serveraddr=input.Server;
   pname=input.Program; bd=input.Bandwith   # read from input
   rand=string.join(random.sample(Str,10))
   # generating random string
   rand=rand.replace(' ','')                 
   suffix=filename.split('.')
   #check out the file name which should be avi, mp4 etc
   suffix='.'+suffix[len(suffix)-1]
   #if the suffix is in the list? 
   try:
      conttype= content_type[suffix]         
   except KeyError:
      f=okform()
      return render.warning("Warning","<p>File type error</p>",f)
   code=filename+'||'+serveraddr+'||'+rand+'||'+bd;
   #generate the code 
   key_len=len(key); #print key_len                     
   if key_len>=16 :
      #padding for AES
      enkey=key[0:16];#encryption key 
   else:
      enkey=key;                               
      for i in range(key_len%16, 16):
         enkey=enkey+'_';
      print enkey
   content_len=len(code)%16
   for i in range(content_len, 16):
      code=code+'_'
   #print len(code)
   obj=AES.new(enkey,AES.MODE_CBC,b'0000000000000000') ;   print obj;          #done with padding
   encrypt_code=obj.encrypt(code); 
   url_code=base64.urlsafe_b64encode(encrypt_code); 
   try :
     _tab=open_database()
     _cur_tab=_tab.cursor();
     _cur_tab.execute("set names 'utf8'")
   except mysql.Error, e:
     print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
     _cur_tab.close();raise web.seeother("/bgnd") 
   try: 
     _cur_tab.execute("insert filelist(server,name,filename,mediatype,rand,\
     encryptstr,bandwith,date) value('%s','%s','%s','%s','%s','%s','%s','%s')" \
     %(serveraddr,pname, filename,conttype,rand,url_code,bd, str(datetime.now())))
   except mysql.Error, e:
     print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
   _cur_tab.execute("commit")
   _cur_tab.close()
   _tab.close()
   content="<p>"+u"明文：  "+code.replace("_","")+"</p>";
   content=content+"<p>"+u"密文： "+url_code+"</p>"
   content=content+"<p>"+u"随机字符串： "+rand+"</p>"
   print content
   f=okform()
   return render.register(content,f)
class res:
   tel=' '
   def __init__(self) :
     self.tel=telnetlib.Telnet('192.168.0.1',23, 60)
     self.tel.set_debuglevel(2)
     self.tel.read_until('Password:'); #h3c switch
     self.tel.write('bstar'+'\n'); #password
     self.tel.read_until('>')
     self.tel.write('system'+'\n'); #configuration mode
     self.tel.read_until(']')
     self.tel.write('interface GigabitEthernet 1/0/25'+'\n')
     self.tel.read_until(']')
     self.tel.write('qos lr outbound cir 10240'+'\n');
     self.tel.read_until(']') 
     self.tel.write('quit');
     #self.tel.write('disp this'+'\n') #default bandwith is 1M
     #print self.tel.read_all()

      
   def GET(self,name ) :
     global tabl
     BUF=65535
        #print query
     try:
       cur_tab=tabl.cursor();cur_tab.execute("set names 'utf8'")
     except mysql.Error, e:
        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        if e.args[0]== 2006 :
             tabl=open_database()
        raise web.seeother("/")
     name=name.split("&"); lenerror=0; print name
     queryerror=0; 
     if len(name)==2 :
        query=cur_tab.execute("select filename,mediatype,bandwith from filelist where rand='%s' and encryptstr='%s'" % (name[0], name[1]))
     else :
        query=0
     if query!=0 :
        result=cur_tab.fetchone();
        bd=result[2]; print bd
        if bd=='40M' :
           print "bd 4M"
           self.tel.write('interface GigabitEthernet 1/0/25'+'\n')
           self.tel.read_until(']')
           self.tel.write('qos lr outbound cir 40960'+'\n'); 
           self.tel.read_until(']')     
           self.tel.write('quit');
     self.tel.close() 
     if query!=0 :
           filename=result[0]
           filepath=os.path.join('/opt', filename) ;
           print filepath; #for windows, 
           web.header('Content-Type', result[1])
           web.header('Transfer-Encoding','chunked')
           f=open(filepath,'r'); print f
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
           yield render.warning("Warning","<p>URL parsing error.</p>",f)

   def POST(self,path):
       raise web.seeother("/")
class index:
    
    def GET(self):
      global tabl
      try:
        cur_tab=tabl.cursor();cur_tab.execute("set names 'utf8'")
        print cur_tab
      except mysql.Error, e:
        print "MySQL Error [%d]: %s" % (e.args[0], e.args[1])
        if e.args[0]==2006 :
          tabl=open_database()
          raise web.seeother("/")
        else :
          f=okform()
          return render.register("<p>Internal Error, Try later</p>",f)
      cur_tab.execute("select rand, encryptstr,name,bandwith from filelist order by bandwith")
      lines=cur_tab.fetchall();#cur_tab.execute("commit");
      print lines
      cur_tab.execute('commit');
      cur_tab.close();
      return render.firstpg(lines)
class poor:
   tel=' '
   def __init__(self) :
     self.tel=telnetlib.Telnet('192.168.0.1',23, 60)
     self.tel.set_debuglevel(2)
     self.tel.read_until('Password:'); #h3c switch
     self.tel.write('bstar'+'\n'); #password
     self.tel.read_until('>')
     self.tel.write('system'+'\n'); #configuration mode
     self.tel.read_until(']')
     self.tel.write('interface GigabitEthernet 1/0/25'+'\n')
     self.tel.read_until(']')
     self.tel.write('qos lr outbound cir 10240'+'\n');
     self.tel.read_until(']')
     self.tel.write('quit');
     self.tel.close()
   def GET(self) :
     BUF=65535
     filepath="/opt/KARA.mp4"  ; # for windows
     web.header('Content-Type', 'video/mp4')
     web.header('Transfer-Encoding','chunked')
     f=open(filepath,'r')
     while True:
       c=f.read(BUF)
       if c :  #the bandwith will be limited by the hardware, so we don't have to degrade the quality of the stream
         #if random.randint(1,20)!=8 :
            yield c
         #else :
         #   time.sleep(1)
         #   yield c
       else :
          break

tabl=open_database(); 
if __name__ == "__main__":
    app = web.application(urls, globals())
    try:
      app.run()
    except KeyboardInterrupt :
      tabl.close()
      print "exitting"
    finally :
      exit(0)

