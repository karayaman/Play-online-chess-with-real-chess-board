import tkinter as tk
import subprocess
import sys
from threading import Thread

running_process = None


def on_closing():
    if running_process:
        if running_process.poll() is None:
            running_process.terminate()
    window.destroy()


def log_process(process, finish_message):
    global button_frame
    button_stop = tk.Button(button_frame, text="Stop", command=stop_process)
    button_stop.grid(row=0, column=0, columnspan=2, sticky="ew")
    while True:
        output = process.stdout.readline()
        if output:
            logs_text.insert(tk.END, output.decode())
        if process.poll() is not None:
            logs_text.insert(tk.END, finish_message)
            break
    global start, board
    start = tk.Button(button_frame, text="Start Game", command=start_game)
    start.grid(row=0, column=0)
    board = tk.Button(button_frame, text="Board Calibration", command=board_calibration)
    board.grid(row=0, column=1)


def stop_process(ignore=None):
    if running_process:
        if running_process.poll() is None:
            running_process.terminate()


def board_calibration(ignore=None):
    arguments = [sys.executable, "board_calibration.py", "show-info"]
    #arguments = ["board_calibration.exe", "show-info"]
    selected_camera = camera.get()
    if selected_camera != OPTIONS[0]:
        cap_index = OPTIONS.index(selected_camera) - 1
        arguments.append("cap=" + str(cap_index))
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    global running_process
    running_process = process
    log_thread = Thread(target=log_process, args=(process, "Board calibration finished.\n"))
    log_thread.daemon = True
    log_thread.start()


def start_game(ignore=None):
    arguments = [sys.executable, "main.py"]
    #arguments = ["main.exe"]
    if no_template.get():
        arguments.append("no-template")
    if make_opponent.get():
        arguments.append("make-opponent")
    if comment_me.get():
        arguments.append("comment-me")
    if comment_opponent.get():
        arguments.append("comment-opponent")
    if drag_drop.get():
        arguments.append("drag")
    arguments.append("delay=" + str(values.index(default_value.get())))
    selected_camera = camera.get()
    if selected_camera != OPTIONS[0]:
        cap_index = OPTIONS.index(selected_camera) - 1
        arguments.append("cap=" + str(cap_index))
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    global running_process
    running_process = process
    log_thread = Thread(target=log_process, args=(process, "Game finished.\n"))
    log_thread.daemon = True
    log_thread.start()


window = tk.Tk()
window.title("Play online chess with real chess board by Alper Karayaman")
no_template = tk.IntVar()
make_opponent = tk.IntVar()
drag_drop = tk.IntVar()
comment_me = tk.IntVar()
comment_opponent = tk.IntVar()

menu_frame = tk.Frame(window)
menu_frame.grid(row=0, column=0, columnspan=2, sticky="W")
camera = tk.StringVar()
OPTIONS = ["Default"]
try:
    from pygrabber.dshow_graph import FilterGraph

    OPTIONS.extend(FilterGraph().get_input_devices())
except:
    pass
camera.set(OPTIONS[0])
label = tk.Label(menu_frame, text='Webcam to be used:')
label.grid(column=0, row=0, sticky=tk.W)
menu = tk.OptionMenu(menu_frame, camera, *OPTIONS)
menu.config(width=max(len(option) for option in OPTIONS), anchor="w")
menu.grid(column=1, row=0, sticky=tk.W)

c = tk.Checkbutton(window, text="Find chess board of online game without template images.", variable=no_template)
c.grid(row=1, column=0, sticky="W", columnspan=1)

c1 = tk.Checkbutton(window, text="Make moves of opponent too.", variable=make_opponent)
c1.grid(row=2, column=0, sticky="W", columnspan=1)

c2 = tk.Checkbutton(window, text="Make moves by drag and drop.", variable=drag_drop)
c2.grid(row=3, column=0, sticky="W", columnspan=1)

c2 = tk.Checkbutton(window, text="Say my moves.", variable=comment_me)
c2.grid(row=4, column=0, sticky="W", columnspan=1)

c3 = tk.Checkbutton(window, text="Say opponent's moves.", variable=comment_opponent)
c3.grid(row=5, column=0, sticky="W", columnspan=1)

values = ["Do not delay game start.", "1 second delayed game start."] + [str(i) + " seconds delayed game start." for i
                                                                         in range(2, 6)]
default_value = tk.StringVar()
s = tk.Spinbox(window, values=values, textvariable=default_value, width=max(len(value) for value in values))
default_value.set(values[-1])
s.grid(row=6, column=0, sticky="W", columnspan=2)
button_frame = tk.Frame(window)
button_frame.grid(row=7, column=0, columnspan=2, sticky="W")
start = tk.Button(button_frame, text="Start Game", command=start_game)
start.grid(row=0, column=0)
board = tk.Button(button_frame, text="Board Calibration", command=board_calibration)
board.grid(row=0, column=1)
text_frame = tk.Frame(window)
text_frame.grid(row=8, column=0)
scroll_bar = tk.Scrollbar(text_frame)
logs_text = tk.Text(text_frame, background='gray', yscrollcommand=scroll_bar.set)
scroll_bar.config(command=logs_text.yview)
scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
logs_text.pack(side="left")

window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
