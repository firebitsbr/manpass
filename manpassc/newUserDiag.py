#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# generated by wxGlade 0.7.0 on Mon Jul 13 05:41:37 2015
#

import wx
import common
import os.path

# begin wxGlade: dependencies
import gettext
# end wxGlade
import genPassDiag
import shlex
import subprocess
import time
import threading
import Queue
import sys
import platform
import string



# begin wxGlade: extracode
# end wxGlade
_ = wx.GetTranslation

MINIMALPASSLEN=8
MINIMALUNAMELEN=3

def goodPass(upass,uname):
    #upass and uname must be unicode
    if len(upass)<MINIMALPASSLEN:
        raise ValueError(_("the password length must be >=")+unicode(MINIMALPASSLEN))
    if upass.find(uname)!=-1:
        raise ValueError(_("password can't contain user name"))
    hasdigit=0
    hasup=0
    haspunction=0
    haslow=0
    for c in upass:
        if c in string.digits:
            hasdigit=1
        if c in string.uppercase:
            hasup=1
        if c in string.punctuation:
            haspunction=1
        if c in string.lowercase:
            haslow=1
    if hasdigit+hasup+haspunction+haslow<=2:
        raise ValueError(_("password need to contain characters from at least 3 different kinds: uppercase, lowercase, digits and punctuation"))

    return True


def goodName(uname):
    if len(uname)<MINIMALUNAMELEN:
        raise ValueError(_("the username length must be >=")+unicode(MINIMALUNAMELEN))
    return True

class EnQThread(threading.Thread):
    def __init__(self,out,Q):
        threading.Thread.__init__(self)
        self.out=out
        self.Q=Q
        self.running=True

    def stop(self):
        self.running=False

    def run(self):
        for line in iter(self.out.readline, b''):
                self.Q.put(line)
                time.sleep(1)
                if self.running==False: break
        self.out.close()

class NewUserDiag(wx.Dialog):
    def __init__(self, parent):
        # begin wxGlade: MainPannel.__init__
        style =  wx.CAPTION|wx.SYSTEM_MENU
        wx.Dialog.__init__(self,parent,style=style)
        self.text_ctrl_uname = wx.TextCtrl(self, wx.ID_ANY, "",size=(200,-1))
        self.label_uname = wx.StaticText(self, wx.ID_ANY,label=_("Username:"),style=wx.ALIGN_LEFT)
        self.text_ctrl_upass1 = wx.TextCtrl(self, wx.ID_ANY, "",size=(200,-1),style=wx.TE_PASSWORD)
        self.label_upass1 = wx.StaticText(self, wx.ID_ANY,label=_("Password:"),style=wx.ALIGN_RIGHT)
        self.text_ctrl_upass2 = wx.TextCtrl(self, wx.ID_ANY, "",size=(200,-1),style=wx.TE_PASSWORD)
        self.label_upass2 = wx.StaticText(self, wx.ID_ANY,label=_("Type Again:"),style=wx.ALIGN_RIGHT)

        self.__set_properties()
        self.__do_layout()


        okb=self.bsizer.GetAffirmativeButton()
        canb=self.bsizer.GetCancelButton()
        self.Bind(wx.EVT_BUTTON,self.OnOK,okb)
        self.Bind(wx.EVT_BUTTON,self.OnCancel,canb)


        self.Centre()
        # end wxGlade

    def __set_properties(self):
        # begin wxGlade: MainPannel.__set_properties
        self.SetTitle(_("Create new user"))
        #self.SetWindowStyle(wx.BORDER_DEFAULT)
        # end wxGlade

    def __do_layout(self):
        # begin wxGlade: MainPannel.__do_layout
        sizer_all=wx.BoxSizer(wx.VERTICAL)
        sizer_v = wx.FlexGridSizer(3,2,5,5)

        sizer_v.Add(self.label_uname,0,wx.FIXED_MINSIZE|wx.ALIGN_RIGHT|wx.TOP,5)
        sizer_v.Add(self.text_ctrl_uname,3,wx.TOP|wx.EXPAND,5)
        sizer_v.Add(self.label_upass1,0,wx.FIXED_MINSIZE|wx.ALIGN_RIGHT|wx.TOP,5)
        sizer_v.Add(self.text_ctrl_upass1,3,wx.TOP|wx.EXPAND,5)
        sizer_v.Add(self.label_upass2,0,wx.FIXED_MINSIZE|wx.ALIGN_RIGHT|wx.TOP,5)
        sizer_v.Add(self.text_ctrl_upass2,3,wx.TOP|wx.EXPAND,5)
        sizer_all.Add(sizer_v,0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.bsizer=self.CreateButtonSizer(wx.OK|wx.CANCEL)
        sizer_all.Add(self.bsizer,0, wx.ALL|wx.ALIGN_CENTER_HORIZONTAL, 5)
        self.SetSizer(sizer_all)
        sizer_all.Fit(self)
        self.Layout()
        # end wxGlade


    def disableMe(self):
        self.text_ctrl_uname.Disable()
        self.text_ctrl_upass1.Disable()
        self.text_ctrl_upass2.Disable()
        okb=self.bsizer.GetAffirmativeButton()
        canb=self.bsizer.GetCancelButton()
        okb.Disable()
        canb.Disable()

    def enableMe(self):
        self.text_ctrl_uname.Enable()
        self.text_ctrl_upass1.Enable()
        self.text_ctrl_upass2.Enable()
        okb=self.bsizer.GetAffirmativeButton()
        canb=self.bsizer.GetCancelButton()
        okb.Enable()
        canb.Enable()

    def OnCancel(self,evt):
        evt.Skip()

    def OnOK(self,evt):
        b=evt.GetEventObject()
        orig_label=b.GetLabel()
        b.SetLabel(_("Creating..."))
        self.disableMe()
        self.Update()
        self.uname=self.text_ctrl_uname.GetValue().strip()
        confdir=common.getConfDir(self.uname)
        if os.path.isdir(confdir):
            wx.MessageBox(_("User already exisits, choose a different username"),_("Error"),0|wx.ICON_ERROR,self)
            b.SetLabel(orig_label)
            self.enableMe()
            return
        try:
            goodName(self.uname)
        except Exception as Err:
            wx.MessageBox(_("Not a good username, choose a different username\n")+unicode(Err),_("Error"),0|wx.ICON_ERROR,self)
            b.SetLabel(orig_label)
            self.enableMe()
            return
        pass1=self.text_ctrl_upass1.GetValue().strip()
        pass2=self.text_ctrl_upass2.GetValue().strip()
        if pass1!=pass2:
            wx.MessageBox(_("Password of two typing doesn't match!"),_("Error"),0|wx.ICON_ERROR,self)
            b.SetLabel(orig_label)
            self.enableMe()
            return
        try:
            goodPass(pass1,self.uname)
        except Exception as Err:
            wx.MessageBox(_("Not a good password, choose a different password\n")+unicode(Err),_("Error"),0|wx.ICON_ERROR,self)
            b.SetLabel(orig_label)
            self.enableMe()
            return
        waitbox=wx.BusyInfo(_("Creating new user, please wait..."))
        uport=common.getNewPort()
        exename=common.getManpassdExeName()
        cmd=exename+" -username={uname} -create=true -pipepass=true -svrport={port}".format(uname=self.uname,port=uport)
        args=shlex.split(cmd)
        if platform.system()=="Windows":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags|= subprocess.STARTF_USESHOWWINDOW
        else:
            startupinfo = None
        ON_POSIX = 'posix' in sys.builtin_module_names
        p=subprocess.Popen(args,executable=exename,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,startupinfo=startupinfo,close_fds=ON_POSIX)
        def enqueue_output(out, queue):
            for line in iter(out.readline, b''):
                queue.put(line)
            out.close()
        outq=Queue.Queue()
        errq=Queue.Queue()
        t1=EnQThread(p.stdout,outq)
        t2=EnQThread(p.stderr,errq)
        t1.daemon=True
        t2.daemon=True
        t1.start()
        t2.start()
        p.stdin.write(pass1+"\n")
        p.stdin.close()
        def check_output(outq,errq):
            wx.GetApp().Yield()
            while True:
                try:
                    outline=outq.get_nowait()
                except Queue.Empty:
                    pass
                else:
                    #print "stdout:",outline
                    if outline.find("new user created") !=-1:
                        break
                try:
                    errline=errq.get_nowait()
                except Queue.Empty:
                    pass
                else:
                    #print "some err:",errline
                    break
            t1.stop()
            t2.stop()
            fp=open(os.path.join(confdir,"manpass.conf"),"w")
            fp.write('{"port": '+str(uport)+" }")
            fp.close()


        check_output(outq,errq)
        del waitbox
        self.Close()
        evt.Skip()
##        t3=threading.Thread(target=check_output,args=(outq,errq))
##        t3.daemon=True
##        t3.start()



##        self.meta=self.text_ctrl_meta.GetValue().strip()
##        self.upass=self.text_ctrl_upass.GetValue().strip()
##        if self.uname=="" or self.upass=="" or self.meta=="":
##            wx.MessageBox(_("Website/application/username/password can't be empty!"),_("Error"),0|wx.ICON_ERROR,self)
##        else:
##            evt.Skip()



# end of class MainPannel

if __name__ == "__main__":
    app = wx.App()
    diag=NewUserDiag(None)
    app.SetTopWindow(diag)
    diag.ShowModal()
    app.MainLoop()
