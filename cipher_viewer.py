#!/usr/bin/env python

import PIL.Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os

try:
    from Tkinter import *
    import tkFileDialog as filedialog
except ImportError:
    from tkinter import *
    from tkinter import filedialog
from decrypt import decrypt_single_file
import PIL.ImageTk
from io import BytesIO

class App(Frame):
    def invalidate(self):
        im = self.im
        w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        imgWidth, imgHeight = im.size
        if imgWidth > w or imgHeight > h:
            ratio = min(w/imgWidth, h/imgHeight)
            imgWidth = int(imgWidth*ratio)
            imgHeight = int(imgHeight*ratio)
            im = im.resize((imgWidth,imgHeight))
        else:
            ratio = min(w/imgWidth, h/imgHeight)
            imgWidth = int(imgWidth*ratio)
            imgHeight = int(imgHeight*ratio)
            im = im.resize((imgWidth,imgHeight))
            

        if self.im.mode == "1": # bitmap image
            self.img = PIL.ImageTk.BitmapImage(im, foreground="white")
        else:              # photo image
            self.img = PIL.ImageTk.PhotoImage(im)
        imagesprite = self.canvas.create_image(w/2,h/2,image=self.img)

    def open(self, event=None):
        _ = event
        filename = filedialog.askopenfilename(initialdir=self.dirname)
        self.open_(filename)

    def open_(self, filename):
        if type(filename) is not str:
            if filename != ():
                print("File name not string!")
                print(filename)
            return

        if not self.image_pred(filename):
            print("Unsupported file type '%s'" % filename)
            return

        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)

        if dirname != self.dirname:
            self.collect_images(dirname)

        self.cur = self.dir_images.index(basename)

        if filename.endswith(".cipher"):
            ret, jpgdata=decrypt_single_file(filename, self.D, self.N, memory_mode=True)
            if ret != 0:
                print("decrypt file '%s' failed with ret value %d" % (filename, ret))
                return

            file_jpgdata = BytesIO(jpgdata)
            self.im = PIL.Image.open(file_jpgdata)
        else:
            self.im = PIL.Image.open(filename)

        self.invalidate()
        self.num_page=0
        self.num_page_tv.set(str(self.num_page+1))

    def collect_images(self, dirname):
        self.dirname = dirname
        self.dir_images = []
        dirfiles = os.listdir(dirname)
        for f in dirfiles:
            if self.image_pred(f):
                self.dir_images.append(f)
        self.dir_images.sort()
        print("Images in dir '%s'" % self.dirname)
        print(self.dir_images)

    def image_pred(self, fname):
        fname = fname.lower()
        return fname.endswith(".jpg") or fname.endswith(".jpeg") or fname.endswith(".bmp") or fname.endswith('png') or fname.endswith(".cipher")

    def prev(self, key_event=None):
        if self.dirname == "" or len(self.dir_images) == 0 or (len(self.dir_images) == 1 and self.cur == 0):
            return

        if self.cur == -1:
            self.cur = 0
        self.open_(os.path.join(self.dirname, self.dir_images[self.cur-1]))

    def next(self, key_event=None):
        if self.dirname == "" or len(self.dir_images) == 0 or (len(self.dir_images) == 1 and self.cur == 0):
            return

        self.open_(os.path.join(self.dirname, self.dir_images[(self.cur+1)%len(self.dir_images)]))

    def key_handler(self, event):
        if event.char == 'j':
            self.prev(event)
        elif event.char == 'k':
            self.next(event)

    def __init__(self, dir, D, N, master=None):
        Frame.__init__(self, master)
        self.master.title('Image Viewer')
        try:
            try:
                self.master.tk.call('tk_getOpenFile', '-foobarbaz')
            except TclError:
                pass

            self.master.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            self.master.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        except:
            pass

        initial_dir = dir
        if initial_dir == "":
            from pathlib import Path
            initial_dir = Path.home()
            pic_dir = os.path.join(initial_dir, "Pictures")
            if os.path.isdir(pic_dir): initial_dir = pic_dir
        self.collect_images(initial_dir)
        self.cur = -1

        self.num_page=0
        self.num_page_tv = StringVar()
        self.D = D
        self.N = N

        fram = Frame(self)
        fram.pack(side=TOP, fill=BOTH)

        fram.bind("<Key>", self.key_handler)
        fram.bind('<Left>', self.prev)
        fram.bind('<Right>', self.next)
        fram.bind('<Control-o>', self.open)

        w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        self.canvas = Canvas(fram,width=w,height=h)
        self.canvas.pack()
        self.canvas.configure(background='black')
        fram.focus_set()

        self.pack()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument('-d', type=int, dest='D', help='D', default=1157)
    parser.add_argument('-n', type=int, dest='N', help='N', default=61823)
    parser.add_argument('dir', nargs='?', default='')
    args = parser.parse_args()
    if args.N > 256**3:
        print("N must be not greater than 256*256*256")
        exit(1)
    if args.N < 32*256:
        print("N must be not less than 32*256")
        exit(1)
    app = App(args.dir, args.D, args.N); app.mainloop()
