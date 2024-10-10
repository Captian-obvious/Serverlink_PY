import json,os,platform,re,socket,sys,threading,time;
import tkinter as tk;
from tkinter import FALSE, ttk;
#HELPER FUNCTIONS
def dirExists(path):
    return os.path.exists(path);
##end
def createWinADFIfNotPresent():
    appDataPath=os.getenv('APPDATA');
    if (appDataPath!=None):
        if (not dirExists(f'{appDataPath}/Serverlink')):
            os.mkdir(f'{appDataPath}/Serverlink');
        ##endif
    else:
        print('Failed to find %APPDATA% directory..');
    ##endif
##end
def createLinuxADFIfNotPresent():
    home_directory=os.path.expanduser('~');
    directory_path=os.path.join(home_directory,'Serverlink');
    if (not dirExists(directory_path)):
        os.mkdir(directory_path);
    ##endif
##end
def createCFGFolderIfNotPresent():
    os_name=platform.system();
    if (os_name=='Linux'):
        home_directory=os.path.expanduser('~');
        directory_path=os.path.join(home_directory,'Serverlink');
        createLinuxADFIfNotPresent();
        conf_path=os.path.join(directory_path,'conf');
        if (dirExists(conf_path)):
           return conf_path;
        else:
            os.mkdir(conf_path);
            return conf_path;
        ##endif
    elif (os_name=='Windows'):
        appDataPath=os.getenv('APPDATA');
        createWinADFIfNotPresent();
        if (appDataPath!=None):
            if (dirExists(f'{appDataPath}/Serverlink/cfg')):
                return f'{appDataPath}/Serverlink/cfg';
            else:
                os.mkdir(f'{appDataPath}/Serverlink/cfg');
                return f'{appDataPath}/Serverlink/cfg';
            ##endif
        else:
            print('Failed to find %APPDATA% directory..');
        ##endif
    else:
        print('Unsupported OS, sorry.');
    ##endif
##end

#VIEWS FUNCTIONS
class SL_GUI:
    def __init__(self):
        self.client=None;
        self.window_exists=False;
    ##end
    def init(self,slc):
        self.client=slc;
    ##end
    def start_ui(self,page):
        if (not self.client.isInitialized):
            print("SL: Initializing Client...");
            self.client.initialize();
        ##endif
        self.client.print_info("Preparing to enter visual mode..."); 
        self.print_info("Initializing application...");
        time.sleep(1);
        self.print_info("Loading window...");
        if (not self.window_exists):
            self.make_window();
        ##endif
        self.print_info("Loading page...");
        self.load_page(page);
    ##end
    def make_window(self):
        self.window_exists=True;
        self.print_info("Starting <main>...");
        time.sleep(.1);
        self.client.print_info("Exiting to visual mode...");
        self.print_info("Welcome to Serverlink!");
        self.root=tk.Tk();
        self.root.geometry('640x480');
        self.root.title('Serverlink');
    ##end
    def load_page(self,page):
        if page=="conf":
            self.configMenu();
        elif page=="index":
            self.root.title("Serverlink - Welcome");
            self.root.mainloop();
            self.window_exists=False;
        ##endif
    ##end
    def configMenu(self):
        global configFile,cfgdat;
        cfgdat={
            "isDarkMode":False,
            "fg":"default",
            "knownHosts":{},
        };
        cfgPath=createCFGFolderIfNotPresent();
        if (dirExists(f'{cfgPath}/main.cfg')):
            with open(f'{cfgPath}/main.cfg','r') as configFile:
                cfgdat=json.load(configFile);
                configFile.close();
            ##endwith
        else:
            with open(f'{cfgPath}/main.cfg','w+') as configFile:
                configFile.write(json.dumps(cfgdat));
                configFile.close();
            ##endwith
        ##endif
        win=self.root;
        win.title('Serverlink - Settings');
        win_h=win.winfo_height();
        win_w=win.winfo_width();
        styles=ttk.Style();
        if (cfgdat['fg']!="default"):
            fgColor=cfgdat['fg'];
        ##endif
        styles.theme_create('Light',parent="clam",settings={
            'TFrame':{
                'configure':{
                    "background":"#fff",
                },
            },
            'Main.TFrame':{
                'configure':{
                    "background":"#000",
                },
            },
            'SHS.TFrame':{
                'configure':{
                    'background':"#fff",
                },
            },
            'KH.TFrame':{
                'configure':{
                    'background':"#fff",
                },
            },
            'TNotebook':{
                'configure':{
                    'background':"#eee",
                },
            },
            'TNotebook.Tab':{
                'configure':{
                    'background':"#fff",
                    'foreground':"#000",
                    'lightcolor':"#fff",
                    'padding':5,
                },
                "map": {
                    "background": [("active", "#fff"), ("selected", "#fff"), ("!selected", "#eee")],
                },
            },
            'TCheckbutton':{
                'configure':{
                    'background':"#eee",
                    'foreground':"#000",
                    'indicatorbackground':"#eee",
                    'indicatorforeground':"#000",
                    'padding':5,
                },
            },
        });
        styles.theme_create('Dark',parent="clam",settings={
            'TFrame':{
                'configure':{
                    "background":"#fff",
                },
            },
            'Main.TFrame':{
                'configure':{
                    "background":"#000",
                },
            },
            'SHS.TFrame':{
                'configure':{
                    'background':"#333",
                },
            },
            'KH.TFrame':{
                'configure':{
                    'background':"#333",
                },
            },
            'TNotebook':{
                'configure':{
                    'background':"#000",
                },
            },
            'TNotebook.Tab':{
                'configure':{
                    'foreground':"#fff",
                    'lightcolor':"#333",
                    'padding':5,
                },
                "map": {
                    "background": [("active", "#333"), ("selected", "#333"), ("!selected", "#000")],
                },
            },
            'TCheckbutton':{
                'configure':{
                    'background':"#333",
                    'foreground':"#fa0",
                    'fieldbackground':"333",
                    'fieldforeground':"#fa0",
                    'indicatorbackground':"#fff",
                    'indicatorforeground':"#0f0",
                    'padding':5,
                },
            },
        });
        styles.theme_create('Default',parent="default",settings={
            'TFrame':{
                'configure':{
                    "background":"#fff",
                },
            },
            'Main.TFrame':{
                'configure':{
                    "background":"#000",
                },
            },
            'SHS.TFrame':{
                'configure':{
                    'background':"#fff",
                },
            },
            'KH.TFrame':{
                'configure':{
                    'background':"#fff",
                },
            },
            'TNotebook':{
                'configure':{
                    'background':"#eee",
                },
            },
            'TNotebook.Tab':{
                'configure':{
                    'background':"#000",
                    'lightcolor':"#fff",
                    'padding':5,
                },
                "map": {
                    "background": [("active", "#fff"), ("selected", "#fff"), ("!selected", "#eee")],
                },
            },
            'TCheckbutton':{
                'configure':{
                    'background':"#fff",
                    'foreground':"#000",
                    'indicatorbackground':"#eee",
                    'indicatorforeground':"#000",
                    'padding':5,
                },
            },
        });
        root=ttk.Frame(win,style='Main.TFrame');
        root.pack(expand=1,fill=tk.BOTH);
        notebook=ttk.Notebook(root);
        tab1=ttk.Frame(notebook,style="SHS.TFrame");
        tab2=ttk.Frame(notebook,style="KH.TFrame");
        notebook.add(tab1,text='Shell Settings');
        notebook.add(tab2,text='Known Hosts');
        var1=tk.IntVar();
        def setDarkMode(c1):
            if (var1.get()==1):
                cfgdat['isDarkMode']=True;
                styles.theme_use('Dark');
            else:
                cfgdat['isDarkMode']=False;
                styles.theme_use('Light');
            ##endif
        ##end
        def bindFn(fn,*args,**kwargs):
            def nfn(*args2,**kwargs2):
                fn(*args,*args2,**kwargs,**kwargs2);
            ##end
            return nfn;
        ##end
        c1=tk.Checkbutton(tab1,text="Dark Mode",variable=var1,onvalue=1,offvalue=0);
        c1['command']=bindFn(setDarkMode,c1);
        c1.pack(expand=1,fill=tk.X,anchor="n");
        notebook.pack(expand=1,fill=tk.BOTH);
        win.mainloop();
    ##end
    def print_info(self,output):
        print(f"VSL: {output}");
    ##end
    def print_err(self,output):
        print(f"\033[1;31mVSL: {output}\033[0m");
    ##end
##end
