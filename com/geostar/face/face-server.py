#-*- coding:utf-8 -*-
'''
Created on 2013-3-13

@author: Administrator
'''
import asyncore,asynchat,socket,re,cStringIO,urllib2,os
from facecore import FaceCore #facecore is the moudle which implements the ac-engine

SEVER_PORT = 7777          #the port that FaceServer works on

class FaceHandler(asynchat.async_chat):
    global core
    def __init__(self, *args):
        asynchat.async_chat.__init__(self, *args)
        self.set_terminator('\r\n\r\n')
        self.data = cStringIO.StringIO()

    def send_headers(self):
        headers = """HTTP/1.1 200 OK
Cache-Control: no-cache
Content-Type: text/html; charset=UTF-8
Server: FACE Server
"""
        self.push(headers)

    def end_headers(self):
        self.push("\r\n")

    def collect_incoming_data(self, data):
        if self.data.tell()<1024:
            self.data.write(data)

    def welcome(self):
        self.send_headers()
        self.end_headers()
        self.push("<h1>It works</h1><p><I>Powered by FACE http server.</I></p>")
        self.close()

    def redirect(self,path):
        headers ="""HTTP/1.0 303 SEE OTHER
Server: FACEServer
Content-Type: text/html; charset=UTF-8
Location: /%s
Connection: close\r\n\r\n""" % (path)
        self.push(headers)
        self.close()

    def query(self,keyword):
        global core
        try:
            ukey = keyword.decode('utf-8')
        except:
            ukey = keyword.decode('gbk')
        result =[]
        got = core.query(ukey)
        for g in got:
            result.append('"'+g.encode('utf-8')+'"')
        return "["+",".join(result)+"]"

    def doGet(self,receivedData):
        mc = re.search(r"GET /(.*?) ",receivedData)
        if hasattr(mc,"group"):
            path = mc.group(1) #GET /$path
            path = urllib2.unquote(path)
            #self.log_info (path, 'GET')
            if path=="": #GET /
                self.welcome()
                return
            if os.path.isdir(path) and (not path.endswith("/")):#modify url
                self.redirect(path+"/")
                return
            if path.startswith("db/") or path.startswith("prepare/"):
                self.welcome()
                return

            #check whether the client wanted to search some thing
            mc = re.search(r"^s\?&?q=(.*?)$",path)
            if hasattr(mc,"group"):#do search
                keyword = mc.group(1)
                hits =  self.query(keyword)
                self.send_headers()
                self.push("Content-Length: "+str(len(hits))+"\r\n")
                self.end_headers()
                self.push(hits)
                self.close()
            else:
                #the client just wanted some file
                if os.path.exists(path):
                    self.putFile(path)
                elif os.path.exists(path.decode('utf-8').encode('gbk')):
                    self.putFile(path.decode('utf-8').encode('gbk'))
                else:
                    self.send_headers()
                    self.end_headers()
                    self.close()
        else:
            self.close()

    def putFile(self,fpath):
        if os.path.isfile(fpath): #request a file
            size = os.path.getsize(fpath)
            self.send_headers()
            self.push("Content-Length: "+str(size)+"\r\n")
            self.end_headers()
            f = file(fpath,"rb")
            sum = 0
            while True:
                s = f.read(2048)
                if s=="":
                    f.close()
                    break
                self.push(s)

        elif os.path.isdir(fpath): #list the directory to browser
            files = os.listdir(fpath)
            content = cStringIO.StringIO()
            content.write("<a href='../'>..</a><br/>")
            for fname in files:
                fullpath = fpath+"/"+fname
                if os.path.isdir(fullpath):
                    content.write("<a href='"+fname+"/'>"+fname+"</a><br/>")
                else:
                    content.write("<a href='"+fname+"'>"+fname+"</a><br/>")
            content.write("<p><I>Powered by FACE http server.</I></p>")
            s_content = content.getvalue()
            self.send_headers()
            self.push("Content-Length: "+str(len(s_content))+"\r\n")
            self.end_headers()
            self.push(s_content)

    def found_terminator(self):
        receivedData = self.data.getvalue()
        self.doGet(receivedData)
        self.data = cStringIO.StringIO()


    def handle_close(self):
        print "Disconnected from", self.getpeername( )
        self.close( )


class FaceServer(asyncore.dispatcher):
    """Copied from http_server in medusa"""
    def __init__ (self, ip, port):
        self.ip = ip
        self.port = port
        asyncore.dispatcher.__init__ (self)
        self.create_socket (socket.AF_INET, socket.SOCK_STREAM)
        self.bind ((ip, port))
        self.listen (15)


    def handle_accept (self):
        try:
            conn, addr = self.accept()
        except socket.error:
            self.log_info ('warning: server accept() threw an exception', 'warning')
            return
        except TypeError:
            self.log_info ('warning: server accept() threw EWOULDBLOCK', 'warning')
            return
        # creates an instance of the handler class to handle the request/response
        # on the incoming connexion
        print addr
        FaceHandler(conn)

if __name__=="__main__":
    # launch the server on the specified port
    print "Initializing....."
    core = FaceCore()
    s=FaceServer('',SEVER_PORT)
    print "FACEServer running on port %s" %SEVER_PORT
    try:
        asyncore.loop(timeout=2)
    except KeyboardInterrupt:
        print "Crtl+C pressed. Shutting down."

