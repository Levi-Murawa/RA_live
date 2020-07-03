# coding=utf-8
#!/usr/bin/python


import subprocess
from tkinter import*
from tkinter import messagebox
import _thread
import sqlite3
import pygame.midi

proc = None
conclicked = False
dcclicked = False
live = False
lost = False
timeout = 0
pygame.midi.init()
inp = pygame.midi.Input(1)
bylo = True
do_RDSa = "Sztuka 01"
import time
zmiana = False




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


        global inp


        tlo = "dim grey"
        drugi_kolor = "medium aquamarine"
        frame = Frame(master, bg = tlo)
        frame.pack()

        self.disconnect = Button(frame, text="ROZŁĄCZ", fg="red", command=self.dc, cursor="hand2", bg = drugi_kolor)
        self.disconnect.pack(pady=5, ipady=10, padx=10, side=LEFT)

        self.live = Button(frame, text="POŁĄCZ", fg="dark green", command=self.go_live, cursor="hand2", bg = drugi_kolor)
        self.live.pack(pady=5, ipady=10, padx=10, side=LEFT)

        frame2 = Frame(master, bg = tlo)
        frame2.pack(fill=X)

        self.info = Message(frame2, text="...", bg="white", fg="black", width=1000)
        self.info.pack(fill=X, padx=10, pady=10, ipady=10)

        frame3 = Frame(master, bg = tlo)
        frame3.pack(fill=X)

        self.podpis = Label(frame3, text="RDS:", bg = tlo)
        self.podpis.pack(side=TOP)

        entry_text = StringVar()
        self.rds = Entry(frame3, text=entry_text, bg = drugi_kolor) ##wejscie RDS-a
        self.rds.pack(fill=X, side=TOP)
        entry_text.set("dziala")

        self.wyslij = Button(frame3, text=">>>", state=DISABLED, command=self.insertmeta, bg = drugi_kolor)
        self.wyslij.pack()

        self.agresja_zmian = Listbox(frame3, cursor="hand1", selectmode = "SINGLE", bg = drugi_kolor, height = 2, selectbackground = tlo)
        self.agresja_zmian.insert(1, "Zmieniaj")
        self.agresja_zmian.insert(2, "Tylko wpisuj")
        self.agresja_zmian.pack()

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

    def get_name_song(self, inp, entrry):
        global bylo
        global nazwa
        global do_RDSa
        global zmiana
        if inp.poll():
            # no way to find number of messages in queue
            # so we just specify a high max value
            a = inp.read(1000)
            b = a[0][0]
            if (b[1] == 20):
                if (b[2] <= 20):
                    if (bylo):
                        self.zaczytaj_nazwe(entrry)
                        utwur = self.zapytanie()
                        wejscie = nazwa + " " + utwur
                        bylo = False
                        zmiana = True
                        do_RDSa = wejscie
                else:
                    if (bylo == False):
                        self.zaczytaj_nazwe_po_wejsciu(entrry)
                        bylo = True
                        zmiana = True
                        do_RDSa = nazwa

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

    def zaczytaj_nazwe(self, czyt):
        global nazwa
        nazwa = czyt

    def zaczytaj_nazwe_po_wejsciu(self, czyt):
        global nazwa
        x = czyt
        ciecie = x.find("   ")
        nazwa = x[0:ciecie]

    def zapytanie(self):
        con = sqlite3.connect('C:\Users\Tomek\AppData\Local\Mixxx\mixxxdb.sqlite')
        con.row_factory = sqlite3.Row
        cur = con.cursor()
        cur.execute(
            """
             SELECT
             lib.artist as artysta, lib.title as tytul
             FROM PlaylistTracks plt
             INNER JOIN Playlists pl ON pl.id = plt.playlist_id
             INNER JOIN library lib ON lib.id = plt.track_id
             ORDER BY pl_datetime_added DESC
             LIMIT 1;
             """)
        wynik = cur.fetchall()
        zlaczone = "   " + str(wynik[0][1]) + "   wyk. " + str(wynik[0][0])
        return zlaczone


def main():
    # proc = Run(['liquidsoap', "-v", "/home/realizator/RALive/radio.liq"])
    # Trace(proc)
    global zmiana

    def wololo():
        if messagebox.askokcancel("Zamykanie", "Na pewno chcesz zamknac?"):
            root.destroy()
            if proc is not None:
                proc.kill()
    root = Tk()
    root.title("RALIVE")
    root.protocol("WM_DELETE_WINDOW", wololo)
    app = App(root)
    while True:
        app.get_name_song(inp, app.rds.get())
        if (zmiana):
            app.rds.delete(0, END)
            app.rds.insert(0, do_RDSa)
            zmiana = False

        root.update_idletasks()
        root.update()


if __name__ == "__main__":
    main()
