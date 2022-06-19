#!/usr/bin/env python

import PIL.Image
PIL.Image.MAX_IMAGE_PIXELS = 1058288540
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import os
from send2trash import send2trash
from pathlib import Path

try:
    from Tkinter import *
    import tkFileDialog as filedialog
except ImportError:
    from tkinter import *
    from tkinter import filedialog
import PIL.ImageTk, PIL.ImageSequence
from io import BytesIO
import webview
from decrypt import decrypt_single_file


class App(Frame):

    def invalidate(self):
        self.cancel()

        self.canvas.delete("all")
        if self.im is None:
            return

        w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        try:
            n_frames = self.im.n_frames
            max_amplifier = 2
        except:
            n_frames = 1
            max_amplifier = 1.5
        self.photoes = []
        for frame in PIL.ImageSequence.Iterator(self.im):
            imgWidth, imgHeight = frame.size
            if imgWidth > w or imgHeight > h:
                ratio = min(w/imgWidth, h/imgHeight)
            else:
                ratio = min(w/imgWidth, h/imgHeight, max_amplifier)
            imgWidth = int(imgWidth*ratio)
            imgHeight = int(imgHeight*ratio)

            frame = frame.resize((imgWidth,imgHeight))
            if self.im.mode == "1":  # bitmap image
                photo = PIL.ImageTk.BitmapImage(frame, foreground="white")
            elif self.im.mode == 'P':
                photo = PIL.ImageTk.PhotoImage(frame.convert('RGBA'))
            else:              # photo image
                photo = PIL.ImageTk.PhotoImage(frame)
            self.photoes.append(photo)

        if len(self.photoes) == 0:
            return

        print("totally %d frames" % len(self.photoes))
        self.canvas.create_image(w/2, h/2, image=self.photoes[0])
        if len(self.photoes) == 1:
            return

        photo_index = 0
        photoes = self.photoes
        try:
            delay = self.im.info['duration']
        except KeyError:
            delay = 100
        delay = max(delay, 100)

        def play():
            nonlocal photo_index, photoes, delay
            # self.canvas.delete("all")
            photo_index = (photo_index + 1) % len(photoes)
            self.canvas.create_image(w/2, h/2, image=photoes[photo_index])
            x_delay = delay
            if photo_index == len(photoes) - 1:
                x_delay = 200
            self.canceller = self.canvas.after(x_delay, play)

        self.canceller = self.canvas.after(delay, play)

    def cancel(self):
        if self.canceller is not None:
            self.canvas.after_cancel(self.canceller)
            self.canceller = None

    def open(self, event=None):
        self.cancel()

        _ = event
        filename = self.webview_file_dialog()
        #filename = filedialog.askopenfilename(initialdir=self.dirname, filetypes=[("image files", ".png .webp .jpg .jpeg .bmp .gif"), ("cipher files", ".cipher")])
        self.open_(filename, force_refresh=True)

    def webview_file_dialog(self):
        file = None
        def open_file_dialog(w):
            nonlocal file
            try:
                file = w.create_file_dialog(webview.OPEN_DIALOG, directory=self.dirname, file_types=("Image files (*.png;*.webp;*.jpg;*.jpeg;*.bmp;*.gif)", "cipher files (*.cipher)"))[0]
            except TypeError:
                pass  # user exited file dialog without picking
            finally:
                w.destroy()
        window = webview.create_window(self, hidden=True)
        webview.start(open_file_dialog, window)
        # file will either be a string or None
        return file

    def open_(self, filename=None, on_file_not_exists=None, force_refresh=False):
        if filename == None:
            filename = self.cur

        if type(filename) is int:
            if len(self.dir_images) == 0 or self.dirname == "":
                self.im = None
                self.invalidate()
                return

            filename = os.path.join(self.dirname, self.dir_images[filename%len(self.dir_images)])

        if type(filename) is not str:
            if filename != ():
                print("File name not string!")
                print(filename)
            return

        if filename == "":
            return

        if not self.image_pred(filename):
            print("Unsupported file type '%s'" % filename)
            return

        dirname = os.path.dirname(filename)
        basename = os.path.basename(filename)

        if dirname != self.dirname or force_refresh:
            self.chdir(dirname)

        self.cur = self.dir_images.index(basename)

        try:
            if filename.endswith(".cipher"):
                ret, jpgdata=decrypt_single_file(filename, self.D, self.N, memory_mode=True)
                if ret != 0:
                    print("decrypt file '%s' failed with ret value %d" % (filename, ret))
                    return

                file_jpgdata = BytesIO(jpgdata)
                self.im = PIL.Image.open(file_jpgdata)
            else:
                self.im = PIL.Image.open(filename)
        except FileNotFoundError or OSError:
            self.delete(keep_file=True)
            if on_file_not_exists is not None:
                on_file_not_exists()
            return

        print("Opened file '%s'" %  basename)
        self.invalidate()
        self.num_page=0
        self.num_page_tv.set(str(self.num_page+1))
        return

    def image_pred(self, fname):
        fname = fname.lower()
        if fname.endswith(".cipher"):
            return True

        return fname.endswith(".jpg") or fname.endswith(".jpeg") or fname.endswith(".bmp") or fname.endswith('png') or fname.endswith(".webp") or fname.endswith(".gif")

    def prev(self, key_event=None):
        if self.dirname == "" or len(self.dir_images) == 0 or (len(self.dir_images) == 1 and self.cur == 0):
            return
        self.cancel()
        self.open_(self.cur-1, on_file_not_exists=lambda: self.prev())

    def on_click(self, event):
        reserved = 47
        if event.x < self.canvas.winfo_width()/2-reserved:
            self.prev()
        elif event.x > self.canvas.winfo_width()/2+reserved:
            self.next()

    def next(self, key_event=None):
        if self.dirname == "" or len(self.dir_images) == 0 or (len(self.dir_images) == 1 and self.cur == 0):
            return
        self.cancel()
        self.open_(self.cur+1)

    def reload(self, key_event=None):
        if self.dirname == "":
            return

        cur_fname = ''
        if self.cur >= 0 and self.cur < len(self.dir_images):
            cur_fname = self.dir_images[self.cur]

        self.chdir(self.dirname)

        try:
            self.cur = self.dir_images.index(cur_fname)
        except:
            self.cur = 0
        self.open_()

    def delete(self, key_event=None, keep_file=False):
        self.cancel()

        if self.cur < 0 or self.cur >= len(self.dir_images):
            return

        filename = self.dir_images[self.cur]
        del self.dir_images[self.cur]
        if not keep_file:
            removing_fname = os.path.join(self.dirname, filename)
            send2trash(removing_fname)
            print("Trashed file '%s'" % removing_fname)
        
        self.open_()

    def switch_to_parent(self, key_event=None):
        self.cancel()

        if self.dirname == "":
            return

        p=str(Path(self.dirname).parent)
        if p == self.dirname:
            return
        self.chdir(p, True)

    def chdir(self, dirname, open_first=False):
        self.dirname = os.path.abspath(dirname)

        self.dir_images = []
        for f in os.listdir(dirname):
            if self.image_pred(f):
                self.dir_images.append(f)
        self.dir_images.sort()
        self.cur = 0

        print("Images in dir '%s'" % self.dirname)
        print(self.dir_images)

        if open_first:
            self.open_() 

    def key_handler(self, event):
        if event.char == 'h':
            self.prev(event)
        elif event.char == 'l':
            self.next(event)
        elif event.char == 'd':
            self.delete(event)
        elif event.char == 'u':
            self.switch_to_parent(event)
        elif event.char == 'r':
            self.reload(event)
        elif event.char == 'o':
            self.open(event)

    def __init__(self, dir, master=None):
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

        from pathlib import Path
        home = Path.home()
        initial_dir = dir
        if initial_dir == "":
            initial_dir = home
            pic_dir = os.path.join(home, "Pictures")
            if os.path.isdir(pic_dir):
                initial_dir = pic_dir
        print("initial_dir: %s" % initial_dir)

        self.im = None
        self.num_page = 0
        self.num_page_tv = StringVar()

        import config
        self.D, self.N = config.get_keys()
        print("D: %d, N: %d" % (self.D, self.N))

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
        self.canvas.bind("<ButtonPress-1>", self.on_click)

        fram.focus_set()

        self.pack()
        self.canceller = None
        self.chdir(initial_dir, True)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument('dir', nargs='?', default='')
    args = parser.parse_args()
    app = App(args.dir); app.mainloop()
