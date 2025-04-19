#!/usr/bin/env python

import PIL.Image

PIL.Image.MAX_IMAGE_PIXELS = 1058288540
from PIL import ImageFile

ImageFile.LOAD_TRUNCATED_IMAGES = True
import os
from send2trash import send2trash
from pathlib import Path
import shutil

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

# 全局变量，用于追踪是否处于全屏状态
fullscreen = True


class Gif:
    def __init__(self, canvas, photoes, w, h, delay):
        self.canvas = canvas
        self.photoes = photoes
        self.w = w
        self.h = h
        self.delay = delay

        self.photo_index = 0
        self.canceller = None
        self.is_paused = False

    def play(self, draw_current=False):
        if draw_current:
            self.canvas.create_image(self.w / 2, self.h / 2, image=self.photoes[self.photo_index])

        photoes, delay = self.photoes, self.delay

        def next_frame():
            nonlocal photoes, delay
            self.photo_index = (self.photo_index + 1) % len(photoes)
            self.canvas.delete("all")
            self.canvas.create_image(self.w / 2, self.h / 2, image=photoes[self.photo_index])
            x_delay = delay
            if self.photo_index == len(photoes) - 1:
                x_delay = 200
            self.canceller = self.canvas.after(x_delay, next_frame)
        self.canceller = self.canvas.after(delay, next_frame)

    def cancel(self):
        if self.canceller is not None:
            self.canvas.after_cancel(self.canceller)
            self.canceller = None

    def pause(self):
        if self.is_paused:
            self.play()
        else:
            self.cancel()
        self.is_paused = not self.is_paused


class App(Frame):

    def cancel(self):
        if self.gif is not None:
            self.gif.cancel()
            self.gif = None

    def invalidate(self):
        self.cancel()

        self.canvas.delete("all")
        if self.im is None:
            return


        self.canvas.update_idletasks()
        global fullscreen
        if fullscreen:
            w, h = self.master.winfo_screenwidth(), self.master.winfo_screenheight()
        else:
            w, h = self.canvas.winfo_width(), self.canvas.winfo_height()
        print(f"全屏模式: {fullscreen}, 当前窗口可用区域: {w}×{h}")

        # w, h = int(w*0.9), int(h*0.9)
        max_amplifier = 2
        photoes = []
        self.width = 0
        for frame in PIL.ImageSequence.Iterator(self.im):
            img_width, img_height = frame.size
            if img_width > w or img_height > h:
                ratio = min(w / img_width, h / img_height)
            else:
                ratio = min(w / img_width, h / img_height, max_amplifier)
            ori_img_width, ori_img_height = img_width, img_height
            img_width = int(img_width * ratio)
            img_height = int(img_height * ratio)
            self.width = img_width

            frame = frame.resize((img_width, img_height))
            print("resize to (%d, %d) from (%d, %d), screen_size: (%d, %d)" % (img_width, img_height, ori_img_width, ori_img_height, w, h))
            if self.im.mode == "1":  # bitmap image
                photo = PIL.ImageTk.BitmapImage(frame, foreground="white")
            elif self.im.mode == 'P':
                photo = PIL.ImageTk.PhotoImage(frame.convert('RGBA'))
            else:  # photo image
                photo = PIL.ImageTk.PhotoImage(frame)
            photoes.append(photo)

        if len(photoes) == 0:
            return
        

        if len(photoes) == 1:
            self.photo = photoes[0]
            self.canvas.create_image(w / 2, h / 2, anchor="center", image=self.photo)
            return

        print("Total %d frames" % len(photoes))

        try:
            delay = self.im.info['duration']
        except KeyError:
            delay = 100
        delay = max(delay, 100)
        self.gif = Gif(self.canvas, photoes, w, h, delay)
        self.gif.play(draw_current=True)

    def open(self, event=None):
        _ = event

        self.cancel()
        filename = self.webview_file_dialog()
        self.open_(filename, force_refresh=True)

    def pause(self, event=None):
        if self.gif is not None:
            self.gif.pause()

    def webview_file_dialog(self):
        file = None

        def open_file_dialog(w):
            nonlocal file
            try:
                file = w.create_file_dialog(webview.OPEN_DIALOG, directory=self.dirname,
                                            file_types=("All (*.png;*.webp;*.jpg;*.jpeg;*.bmp;*.gif;*.cipher)",
                                                        "Image files (*.png;*.webp;*.jpg;*.jpeg;*.bmp;*.gif)",
                                                        "cipher files (*.cipher)"))[0]
            except TypeError:
                pass  # user exited file dialog without picking
            finally:
                w.destroy()

        window = webview.create_window(self, hidden=True)
        webview.start(open_file_dialog, window)
        # file will either be a string or None
        return file

    def open_(self, filename=None, on_file_not_exists=None, force_refresh=False):
        self.gif = None
        self.width = 0

        if filename is None:
            filename = self.cur

        if type(filename) is int:
            if len(self.dir_images) == 0 or self.dirname == "":
                self.im = None
                self.invalidate()
                return

            filename = os.path.join(self.dirname, self.dir_images[filename % len(self.dir_images)])

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

        # Update current dir
        if (dirname != self.dirname and os.path.abspath(dirname) != self.dirname) or force_refresh:
            self.chdir(dirname)

        # Update cur.
        try:
            self.cur = self.dir_images.index(basename)
        except ValueError:
            self.cur = 0
            print("Can't find file '%s' in dir '%s'" % (filename, self.dirname))
            return

        try:
            if filename.endswith(".cipher"):
                ret, jpgdata = decrypt_single_file(filename, self.D, self.N, memory_mode=True)
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

        print("Opened file '%s'" % basename)
        self.master.title(filename)
        self.invalidate()
        return

    @staticmethod
    def image_pred(fname):
        fname = fname.lower()
        if fname.endswith(".cipher"):
            fname = fname[:len(fname) - len(".cipher")]
        return fname.endswith(".jpg") or fname.endswith(".jpeg") or fname.endswith(".bmp") or fname.endswith(
            'png') or fname.endswith(".webp") or fname.endswith(".gif")

    def prev(self, key_event=None):
        if self.dirname == "" or len(self.dir_images) == 0 or (len(self.dir_images) == 1 and self.cur == 0):
            return
        self.cancel()
        self.open_(self.cur - 1, on_file_not_exists=lambda: self.prev())

    def on_click(self, event):
        reserved = 67
        if event.x < self.canvas.winfo_width() / 2 - self.width / 6:
            self.prev(event)
        elif event.x > self.canvas.winfo_width() / 2 + self.width / 6:
            self.next(event)
        else:
            self.pause(event)

    def next(self, key_event=None):
        if self.dirname == "" or len(self.dir_images) == 0 or (len(self.dir_images) == 1 and self.cur == 0):
            return
        self.cancel()
        self.open_(self.cur + 1)

    def reload(self, key_event=None):
        if self.dirname == "":
            return

        cur_fname = ''
        if 0 <= self.cur < len(self.dir_images):
            cur_fname = self.dir_images[self.cur]

        self.chdir(self.dirname)
        self.cur = 0
        if cur_fname != '':
            try:
                self.cur = self.dir_images.index(cur_fname)
            except ValueError:
                pass
        self.open_()

    def delete(self, key_event=None, keep_file=False):
        self.cancel()

        if self.cur < 0 or self.cur >= len(self.dir_images):
            return

        filename = self.dir_images[self.cur]
        del self.dir_images[self.cur]
        if not keep_file:
            removing_fname = os.path.join(self.dirname, filename)

            if self.trash_dir == '':
                send2trash(removing_fname)
            else:
                shutil.move(removing_fname, self.trash_dir)
            print("Trashed file '%s'" % removing_fname)

        self.open_()

    def switch_to_parent(self, key_event=None):
        self.cancel()

        if self.dirname == "":
            return

        p = str(Path(self.dirname).parent)
        if p == self.dirname:
            return

        self.chdir(p)
        self.cur = 0
        self.open_()

    def chdir(self, dirname):
        self.dirname = os.path.abspath(dirname)

        self.dir_images = []
        for f in os.listdir(dirname):
            if self.image_pred(f):
                self.dir_images.append(f)
        self.dir_images.sort()

        print("Images in dir '%s': " % self.dirname)
        print(self.dir_images)

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
        elif event.char == 'p':
            self.pause(event)

    def __init__(self, dir, trash_dir, master=None):
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

        self.dirname = ""
        self.dir_images = []
        self.gif = None  # type: Gif
        self.photo = None
        self.width = 0
        self.cur = 0
        self.im = None
        self.trash_dir = trash_dir  # type: str
        if self.trash_dir != '':
            os.makedirs(self.trash_dir, exist_ok=True)

        from pathlib import Path
        home = Path.home()
        if dir == "":
            initial_dir = home
            pic_dir = os.path.join(home, "Pictures")
            if os.path.isdir(pic_dir):
                initial_dir = pic_dir
        else:
            if os.path.isdir(dir):
                initial_dir = dir
            elif os.path.isfile(dir):
                initial_dir = os.path.dirname(dir)
                if initial_dir == "":
                    initial_dir = "."
                self.cur = dir
            else:
                raise Exception("'%s' not exists" % dir)
        print("initial_dir: %s" % initial_dir)

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
        self.canvas = Canvas(fram, width=w, height=h)
        #self.canvas.pack()
        self.canvas.pack(expand=True, fill="both")
        self.canvas.configure(background='black')
        self.canvas.bind("<ButtonPress-1>", self.on_click)

        fram.focus_set()

        self.pack()
        self.canceller = None

        self.chdir(initial_dir)
        self.open_()



if __name__ == "__main__":
    import signal
    import argparse

    def sigint_handler(signum, frame):
        print("检测到 ctrl + c，退出程序……")
        root.destroy()  # 或者使用 sys.exit(0)

    # 设置 SIGINT 的信号处理器
    signal.signal(signal.SIGINT, sigint_handler)


    parser = argparse.ArgumentParser(description='Parameters')
    parser.add_argument('dir', nargs='?', default='')
    parser.add_argument("--trash", dest="trash", default="", help="trash dir")
    parser.add_argument("--fullscreen", dest="fullscreen", type=bool, default=True, help="full screen")
    args = parser.parse_args()

    fullscreen = args.fullscreen

    root = Tk()
    root.attributes("-fullscreen", args.fullscreen)  # 设置全屏模式

    app = App(args.dir, args.trash, master=root)


    def exit_fullscreen(event=None):
        global fullscreen
        fullscreen = False

        root.attributes("-fullscreen", False)
        root.overrideredirect(False)

        def maximize():
            w, h = root.winfo_screenwidth(), root.winfo_screenheight()
            root.geometry(f"{w}x{h}")
            root.after(30, lambda: app.invalidate())

        root.after_idle(maximize)

    def toggle_fullscreen(event=None):
        global fullscreen
        if fullscreen:
            exit_fullscreen()
        else:
            root.attributes("-fullscreen", True)
            fullscreen = True
            app.invalidate()


    root.bind("<KeyPress-grave>", toggle_fullscreen)
    root.bind("<F11>", toggle_fullscreen)
    root.bind("<Escape>", exit_fullscreen)

    root.lift()                  # 将窗口提升到最前面
    root.attributes("-topmost", True)   # 设置为顶层窗口
    root.after(100, lambda: root.attributes("-topmost", False))  # 100ms 后取消置顶

    root.focus_force()           # 强制获取焦点
    
    def _heartbeat():
        # 仅仅为了让 Tk 的 select() 超时，回到 Python，去分发信号
        root.after(100, _heartbeat)

    _heartbeat()


    root.mainloop()
