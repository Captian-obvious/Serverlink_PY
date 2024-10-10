#!/usr/bin/env python
import os,platform,socket,sys,time;
import views;
import subprocess as sub;
#Prefix System
cmd_prefix="/";
global shell_type;
shell_type="unknown";
ver="4.35.0";
user_agent_stub="SL/OS";
if platform.system()=='Windows':
    cmd_prefix="> ";
    #shell_type="WinCMD";
    user_agent_stub="SL/Windows";
elif platform.system()=='Linux':
    cmd_prefix="$ ";
    #shell_type="Unix-like";
    user_agent_stub="SL/Linux";
##endif
def get_referring_shell():
    if os.name == 'nt':  # Windows
        ps_module_path=os.getenv('PSModulePath');
        if ps_module_path:
            return "WinPS";
        else:
            comspec=os.getenv('COMSPEC');
            if comspec and 'cmd.exe' in comspec:
                return "WinCMD";
            else:
                return "unknown";
            ##endif
        ##endif
    elif os.name == 'posix':  # Unix-like
        return "Unix-like";
    ##endif
##end
#Serverlink Client
class SL_Client:
    def __init__(self):
        self.isConnecting=False;
        self.isConnected=False;
        self.isInitialized=False;
        self.isVisualMode=False;
        self.isCLIInitialized=False;
        self.currentUrl="";
        self.sshConnection=None;
        self.isSSHConnected=False;
        self.curr_path="";
        self.curr_user="";
        self.creds="";
        self.page="";
        self.sl_user_agent="SL-Client/1.0 Mozilla/5.0 ("+user_agent_stub+") AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36";
        self.commands={
            "connect": {
                "desc": "initiates a SSH connection to provided hostname",
                "valid": ["connect"],
                "arguments": "[hostname] [port (opt)] <auth (-cred)(opt)>"
            },
            "config": {
                "desc": "open the configuration menu",
                "valid": ["cfg","config","configuration"],
                "arguments": "None"
            },
            "cinfo": {
                "desc": "displays information about the current connection",
                "valid": ["cinfo"],
                "arguments": "None"
            },
            "disconnect": {
                "desc": "Disconnects from the ssh connection provided by connect",
                "valid": ["dc","disconnect","discon","disconn"],
                "arguments":"None"
            },
            "info": {
                "desc": "displays information about the client",
                "valid": ["info"],
                "arguments": "None"
            },
            "visual": {
                "desc":"enters visual mode (not fully implemented)",
                "valid":["visual","gui","vis"],
                "arguments":"<page (opt)>"
            },
            "exit": {
                "desc": "exits the CLI",
                "valid": ["exit","quit","leave"],
                "arguments": "None"
            },
        };
        self.info={
            "version":ver,
            "sshVer":"OpenSSH-2",
            "shell":shell_type,
        };
        self.ip="";
        self.port=0;
    ##end
    def get_connection_info(self):
        if not self.isConnected:
            self.print_err("Not connected to a server, no connection info available.");
        else:
            conn_info={
                "ip":self.ip,
                "port":str(self.port),
                "url":self.currentUrl,
                "current_path":self.curr_path,
                "user":self.curr_user,
                "user-agent":f"'{self.sl_user_agent}'"
            };
            for key,value in conn_info.items():
                print(f"  {key}:{value}");
            ##end
        ##endif
    ##end
    def connect(self,host,port=80,credentials=""):
        global usr,hostname;
        usr="";
        hostname=host;
        if len(host.split('@'))>1:
            usr=host.split('@')[0];
            hostname=host.split('@')[1];
        ##endif
        if self.isConnected:
            self.print_err("Already connected to a server");
            return;
        ##endif
        if not self.isInitialized:
            self.print_err("Serverlink not initialized");
            return;
        ##endif
        if not self.isConnecting:
            self.isConnecting=True;
            self.curr_user=usr;
            self.creds=credentials;
            self.print_info(f"Connecting to https://{hostname} on port {port}. Please wait...");
            time.sleep(1);
            if self.hostname_resolves(hostname):
                self.print_info(f"Connected to https://{hostname}.");
                self.isConnecting=False;
                self.isConnected=True;
                self.ip=hostname;
                self.port=port;
                self.currentUrl=f"https://{hostname}:{port}";
                self.initialize_cli(hostname);
            else:
                self.print_err(f"Failed to connect to https://{hostname}.\nRequest failed or Hostname does not resolve.");
                self.isConnecting=False;
            ##endif
        else:
            self.print_err("Already connecting to a server");
        ##endif
    ##end
    def initialize_ssh(self,hostname,port,usr):
        cmd=f"ssh {usr}@{hostname}" if usr!="" else f"ssh {hostname}";
        try:
            self.sshConnection=sub.Popen(cmd,shell=True,stdin=sub.PIPE,stdout=sub.PIPE, stderr=sub.PIPE);
        except Exception as e:
            self.print_err("Failed to initialize SSH connection");
            return 1;
        ##endtry
        return 0;
    ##end
    def ssh_communicate(self,command):
        if not self.isConnected:
            self.print_err("Not connected to a server");
        elif self.isSSHConnected:
            self.sshConnection.stdin.write(command.encode());
            self.sshConnection.stdin.flush();
        ##endif
    ##end
    def ssh_close(self):
        if not self.isConnected:
            self.print_err("Not connected to a server");
        elif self.isSSHConnected:
            self.isSSHConnected=False;
            self.sshConnection.terminate();
            self.print_info("SSH connection closed");
        ##endif
    ##end
    def initialize_cli(self,hostname):
        if not self.isCLIInitialized:
            self.print_info("Serverlink CLI initializing. Please wait...")
            self.isCLIInitialized=True;
            time.sleep(0.1);
            self.print_info("<SHELL STARTING>");
            self.initialize_ssh(hostname,self.port,self.curr_user);
            time.sleep(0.9);
            while self.isConnected and self.sshConnection and self.sshConnection.poll() is None:
                output=self.sshConnection.stdout;
                for line in output:
                    print(line);
                ##end
                cmd=input(cmd_prefix);
                if cmd=='exit' or cmd=='quit' or cmd=='q':
                    self.ssh_close();
                    self.isConnected=False;
                ##endif
            ##end
        ##endif
    ##end
    def disconnect(self):
        if self.isConnected:
            self.print_info(f"Saving and disconnecting from https://{self.ip}.");
            time.sleep(1);
            self.print_info(f"Disconnected from https://{self.ip}.");
            self.isConnected=False;
        else:
            self.print_err("Not connected to a server.");
        ##endif
    ##end
    def begin_shell(self,hostname,port,credentials):
        return 0;
    ##ebd
    def get_command(self,cmd):
        result=""
        for cmd_name,cmd_info in self.commands.items():
            if cmd.lower() in cmd_info["valid"]:
                result=cmd_name;
                break;
            ##endif
        ##end
        return result;
    ##end
    def initialize(self):
        if not self.isInitialized:
            self.print_info(f"Serverlink v{ver} ({platform.machine()}) on {platform.system()}");
            self.isInitialized=True;
            self.isConnected=False;
            self.isConnecting=False;
            self.currentUrl="";
        else:
            self.print_err("Serverlink already initialized.");
        ##endif
    ##end
    def hostname_resolves(self,hostname):
        try:
            socket.gethostbyname(hostname);
            return True;
        except socket.error as e:
            self.print_err(f"Unable to get address info: {e}");
            return False;
        ##endif
    ##end
    def run_cmd(self,cmd,args):
        if cmd=="connect":
            if len(args)<1:
                self.print_err("No hostname provided, process exited.");
            elif len(args)<2:
                self.connect(args[0], 22, "");
            elif len(args)<3:
                self.connect(args[0], int(args[1]), "");
            elif len(args)==3:
                if args[2].startswith("-cred="):
                    self.connect(args[0], int(args[1]), args[2][6:]);
                else:
                    self.print_err("Invalid credentials provided, process exited.");
                ##endif
            else:
                self.print_err("Too many arguments provided, process exited.");
            ##endif
        elif cmd=="info":
            if len(args)<1:
                for key,value in self.info.items():
                    print(f"  {key}: {value}");
                ##end
            ##endif
        elif cmd=="cinfo":
            if len(args)<1:
                self.get_connection_info();
            ##endif
        elif cmd=="disconnect":
            if len(args)<1:
                self.disconnect();
            else:
                self.print_err("Too many arguments provided, process exited.");
            ##endif
        elif cmd=="config":
            if len(args)<1:
                self.isVisualMode=True;
                self.page="conf";
            else:
                self.print_err("Too many arguments provided, process exited.");
            ##endif
        elif cmd=="visual":
            if (len(args)<1):
                self.isVisualMode=True;
                self.print_info("Press <ENTER> to enter visual mode.");
                self.page="index";
            elif(len(args)<2):
                self.isVisualMode=True;
                self.page=args[0];
                self.print_info("Press <ENTER> to enter visual mode.");
            else:
                self.print_err("Too many arguments provided!");
            ##endif
        ##endif
    ##end
    def print_info(self,output):
        print(f"SL: {output}");
    ##end
    def print_err(self,output):
        print(f"\033[1;31mSL: {output}\033[0m");
    ##end
##end

def main(argc:int,argv:list[str]):
    shell_type=get_referring_shell();
    slc=SL_Client();
    gui=views.SL_GUI();
    slc.initialize();
    gui.init(slc);
    magic_exit_code=False;
    if argc < 2:
        print("Welcome to Serverlink, what would you like to do?");
        print("Type 'help' for a list of commands");
        while not magic_exit_code:
            input_str=input(f"{cmd_prefix}");
            args=input_str.split(' ');
            if input_str == "":
                continue;
            elif args[0]=="help":
                print("Commands:");
                for cmd,details in slc.commands.items():
                    print(f"  {cmd} - {details['desc']}");
                    print(f"  Arguments: {details['arguments']}");
                ##end
            elif slc.get_command(args[0])!="":
                cmdname = slc.get_command(args[0]);
                if cmdname=="exit":
                    magic_exit_code=True;
                else:
                    args.pop(0)
                    slc.run_cmd(cmdname,args);
                    if slc.isVisualMode:
                        gui.start_ui(slc.page);
                        slc.isVisualMode=False;
                    ##endif
                ##endif
            else:
                print("\033[1;31mInvalid command.\033[0m");
            ##endif
        ##end
    elif argc > 1:
        args=argv[1:];
        cmd=args[0];
        if cmd=="help":
            print("Commands:")
            for cmd,details in slc.commands.items():
                print(f"  {cmd} - {details['desc']}");
                print(f"  Arguments: {details['arguments']}");
            ##end
        elif slc.get_command(cmd)!="":
            cmdname=slc.get_command(cmd);
            args.pop(0);
            slc.run_cmd(cmdname,args);
        else:
            print("Invalid command.");
        ##endif
    ##endif
##end
main(len(sys.argv),sys.argv);
