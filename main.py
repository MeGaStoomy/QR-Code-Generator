import os, random
from tkinter import *

class QRCode:
    def __init__(self):
        main = Tk()
        self.main = main
        main.title("QR Code Generator")
        main.configure(bg="#5a0088")
        SCREENW = main.winfo_screenwidth()-10
        SCREENH = main.winfo_screenheight()-10
        HEIGHT = int(SCREENH*0.8)
        WIDTH = int(SCREENW*0.6)
        X = SCREENW//2-WIDTH//2
        Y = SCREENH//2-HEIGHT//2-40
        main.geometry(f"{WIDTH}x{HEIGHT}+{X}+{Y}")
        self.area = Canvas(main, bg="white", height=HEIGHT-40, width=HEIGHT-40)
        self.area.place(x=20, y=20)

qr = QRCode()






















