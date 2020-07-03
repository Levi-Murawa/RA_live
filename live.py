#!/usr/bin/python
# -*- coding: utf-8 -*-

import subprocess
from tkinter import*
from tkinter import messagebox
import _thread

proc = None
conclicked = False
dcclicked = False
live = False
lost = False
timeout = 0


def Kill(proc, frame):
    global live
    global lost
    global dcclicked
    global conclicked

    proc.kill()
    live = False
    lost = False
    dcclicked = False
    conclicked = False

    frame.refresh()


def Run(command):
    proces = subprocess.Popen(command, bufsize=1, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    return proces


def Trace(proces, frame):
    global conclicked
    global dcclicked
    global live
    global lost
    global timeout

    while proces.poll() is None:
        linia = proces.stdout.readline()

        if (lost is True) and (timeout is 10):
            Kill(proces, frame)
            messagebox.showerror("BRAK POLACZENIA", "Brak polaczenia po 10 probach")
            break

        elif 'Connection setup was successful' in linia:
            conclicked = False
            print(linia)
            messagebox.showinfo("POLACZONO", "Polaczono!")
            live = True
            lost = False
            frame.insertmeta()
            frame.refresh()
        elif 'Connection failed: Not_found' in linia:
            print(linia)
            live = False
            Kill(proces, frame)
            messagebox.showinfo("PROBLEM Z INTERNETEM", "Brak polaczenia z internetem")
            frame.refresh()
        elif 'Connection refused in connect()' in linia:
            if live is True:
                messagebox.showerror("POLACZENIE PRZERWANE", "Polaczenie zostalo przerwane przez serwer")
                lost = True
            print(linia)
            live = False
            timeout += 1
            frame.refresh()

        elif 'connection timeout!' in linia:
            print(linia)
            messagebox.showerror("ROZLACZONO", "Polaczenie zerwane")
            live = False
            lost = True
            frame.refresh()

    timeout = 0
    return 0


class App:
    def __init__(self, master):
        frame = Frame(master)
        frame.pack()

        self.disconnect = Button(frame, text="ROZŁĄCZ", fg="red", command=self.dc)
        self.disconnect.pack(pady=5, ipady=10, padx=10, side=LEFT)

        self.live = Button(frame, text="POŁĄCZ", fg="green", command=self.go_live)
        self.live.pack(pady=5, ipady=10, padx=10, side=LEFT)

        frame2 = Frame(master)
        frame2.pack(fill=X)

        self.info = Message(frame2, text="...", bg="white", fg="black", width=1000)
        self.info.pack(fill=X, padx=10, pady=10, ipady=10)

        frame3 = Frame(master)
        frame3.pack(fill=X)

        self.podpis = Label(frame3, text="RDS:")
        self.podpis.pack(side=TOP)

        self.rds = Entry(frame3, text="...") ##wejscie RDS-a
        self.rds.pack(fill=X, side=TOP)

        self.wyslij = Button(frame3, text=">>>", state=DISABLED, command=self.insertmeta)
        self.wyslij.pack()

        self.refresh()

    def insertmeta(self):
        subprocess.call(["./meta.sh", self.rds.get()])

    def go_live(self):
        global conclicked
        global proc
        conclicked = True
        self.refresh()
        proc = Run(['liquidsoap', '-v', './radio.liq'])
        _thread.start_new_thread(Trace, (proc, self))

    def dc(self):
        global proc
        global live
        global dcclicked
        dcclicked = True
        self.refresh()
        Kill(proc, self)
        dcclicked = False

    def refresh(self):
        global lost
        global live
        global conclicked
        global dcclicked

        if conclicked is True or dcclicked is True:
            self.disconnect.config(state=DISABLED)
            self.live.config(state=DISABLED)
            self.wyslij.config(state=DISABLED)
            self.info.config(text="...", fg="black", bg="white")
        elif live is True:
            self.disconnect.config(state=NORMAL)
            self.live.config(state=DISABLED)
            self.wyslij.config(state=NORMAL)
            self.info.config(text="POŁĄCZONY", fg="white", bg="green")
        elif (live is False) and (lost is True):
            self.disconnect.config(state=NORMAL)
            self.live.config(state=DISABLED)
            self.wyslij.config(state=DISABLED)
            self.info.config(text="ROZŁĄCZONY", fg="white", bg="red")
        elif live is False:
            self.disconnect.config(state=DISABLED)
            self.live.config(state=NORMAL)
            self.wyslij.config(state=DISABLED)
            self.info.config(text="ROZŁĄCZONY", fg="white", bg="red")
        else:
            self.disconnect.config(state=NORMAL)
            self.wyslij.config(state=DISABLED)
            self.live.config(state=NORMAL)


def main():
    # proc = Run(['liquidsoap', "-v", "/home/realizator/RALive/radio.liq"])
    # Trace(proc)

    def wololo():
        if messagebox.askokcancel("Zamykanie", "Na pewno chcesz zamknac?"):
            root.destroy()
            if proc is not None:
                proc.kill()
    root = Tk()
    root.title("RALIVE")
    root.protocol("WM_DELETE_WINDOW", wololo)
    app = App(root)
    root.mainloop()


if __name__ == "__main__":
    main()
