#!/usr/bin/env python
import json,os,platform,re,socket,sys,threading,time;
import tkinter as tk;
from tkinter import ttk;
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
    if (not dirExists('~/Serverlink')):
        os.mkdir('~/Serverlink');
    ##endif
##end
def createCFGFolderIfNotPresent():
    os_name=platform.system();
    if (os_name=='Linux'):
        createLinuxADFIfNotPresent();
        if (dirExists('~/Serverlink/conf')):
           return '~/Serverlink/conf';
        else:
            os.mkdir('~/Serverlink/conf');
            return '~/Serverlink/conf';
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
def configMenu():
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
    win=tk.Tk();
    win.geometry('640x480');
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