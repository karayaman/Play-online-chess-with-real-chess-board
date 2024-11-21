import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter import messagebox
import subprocess
import sys
from threading import Thread
import pickle
import os

running_process = None

token = ""


def lichess():
    global token
    new_token = askstring("Lichess API Access Token", "Please enter your Lichess API Access Token below.",
                          initialvalue=token)
    if new_token is None:
        pass
    else:
        token = new_token


def on_closing():
    if running_process:
        if running_process.poll() is None:
            running_process.terminate()
    save_settings()
    window.destroy()


def log_process(process, finish_message):
    global button_frame
    button_stop = tk.Button(button_frame, text="Stop", command=stop_process)
    button_stop.grid(row=0, column=0, columnspan=3, sticky="ew")
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
    diagnostic_button = tk.Button(button_frame, text="Diagnostic", command=diagnostic)
    diagnostic_button.grid(row=0, column=2)
    if promotion_menu.cget("state") == "normal":
        promotion.set(PROMOTION_OPTIONS[0])
        promotion_menu.configure(state="disabled")


def stop_process(ignore=None):
    if running_process:
        if running_process.poll() is None:
            running_process.terminate()


def diagnostic(ignore=None):
    arguments = [sys.executable, "diagnostic.py"]
    # arguments = ["diagnostic.exe"]
    # working_directory = sys.argv[0][:-3]
    # arguments = [working_directory+"diagnostic"]
    selected_camera = camera.get()
    if selected_camera != OPTIONS[0]:
        cap_index = OPTIONS.index(selected_camera) - 1
        arguments.append("cap=" + str(cap_index))
    selected_resolution = resolution.get()
    if selected_resolution != RESOLUTION_OPTIONS[0]:
        width, height = selected_resolution.split(" x ")
        arguments.append(f"width={width}")
        arguments.append(f"height={height}")
    selected_fps = fps.get()
    if selected_fps != FPS_OPTIONS[0]:
        arguments.append(f"fps={selected_fps}")
    if calibration_mode.get() == CALIBRATION_OPTIONS[-1]:
        arguments.append("calibrate")
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    # startupinfo = subprocess.STARTUPINFO()
    # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # process = subprocess.Popen(arguments, stdout=subprocess.PIPE,
    #                           stderr=subprocess.STDOUT, stdin=subprocess.PIPE, startupinfo=startupinfo)
    # process = subprocess.Popen(arguments, stdout=subprocess.PIPE,
    #                           stderr=subprocess.STDOUT, cwd=working_directory)
    global running_process
    running_process = process
    log_thread = Thread(target=log_process, args=(process, "Diagnostic finished.\n"))
    log_thread.daemon = True
    log_thread.start()


def board_calibration(ignore=None):
    if calibration_mode.get() == CALIBRATION_OPTIONS[-1]:
        messagebox.showinfo(
            "Board Calibration Not Required",
            "Calibration is not necessary for this mode. "
            "You can proceed directly without calibration."
        )
        return

    arguments = [sys.executable, "board_calibration.py", "show-info"]
    # arguments = ["board_calibration.exe", "show-info"]
    # working_directory = sys.argv[0][:-3]
    # arguments = [working_directory+"board_calibration", "show-info"]
    selected_camera = camera.get()
    if selected_camera != OPTIONS[0]:
        cap_index = OPTIONS.index(selected_camera) - 1
        arguments.append("cap=" + str(cap_index))
    selected_resolution = resolution.get()
    if selected_resolution != RESOLUTION_OPTIONS[0]:
        width, height = selected_resolution.split(" x ")
        arguments.append(f"width={width}")
        arguments.append(f"height={height}")
    selected_fps = fps.get()
    if selected_fps != FPS_OPTIONS[0]:
        arguments.append(f"fps={selected_fps}")
    if calibration_mode.get() == CALIBRATION_OPTIONS[1]:
        arguments.append("ml")
    process = subprocess.Popen(arguments, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT)
    # startupinfo = subprocess.STARTUPINFO()
    # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # process = subprocess.Popen(arguments, stdout=subprocess.PIPE,
    #                           stderr=subprocess.STDOUT, stdin=subprocess.PIPE, startupinfo=startupinfo)
    # process = subprocess.Popen(arguments, stdout=subprocess.PIPE,
    #                           stderr=subprocess.STDOUT, cwd=working_directory)
    global running_process
    running_process = process
    log_thread = Thread(target=log_process, args=(process, "Board calibration finished.\n"))
    log_thread.daemon = True
    log_thread.start()


def start_game(ignore=None):
    arguments = [sys.executable, "main.py"]
    # arguments = ["main.exe"]
    # working_directory = sys.argv[0][:-3]
    # arguments = [working_directory+"main"]
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
    global token
    if token:
        arguments.append("token=" + token)
        promotion_menu.configure(state="normal")
        promotion.set(PROMOTION_OPTIONS[0])

    arguments.append("delay=" + str(values.index(default_value.get())))

    selected_camera = camera.get()
    if selected_camera != OPTIONS[0]:
        cap_index = OPTIONS.index(selected_camera) - 1
        arguments.append("cap=" + str(cap_index))
    selected_resolution = resolution.get()
    if selected_resolution != RESOLUTION_OPTIONS[0]:
        width, height = selected_resolution.split(" x ")
        arguments.append(f"width={width}")
        arguments.append(f"height={height}")
    selected_fps = fps.get()
    if selected_fps != FPS_OPTIONS[0]:
        arguments.append(f"fps={selected_fps}")
    selected_voice = voice.get()
    if selected_voice != VOICE_OPTIONS[0]:
        voice_index = VOICE_OPTIONS.index(selected_voice) - 1
        arguments.append("voice=" + str(voice_index))
        language = "English"
        languages = ["English", "German", "Russian", "Turkish", "Italian", "French"]
        codes = ["en_", "de_", "ru_", "tr_", "it_", "fr_"]
        for l, c in zip(languages, codes):
            if (l in selected_voice) or (l.lower() in selected_voice) or (c in selected_voice):
                language = l
                break
        arguments.append("lang=" + language)

    if calibration_mode.get() == CALIBRATION_OPTIONS[-1]:
        arguments.append("calibrate")

    process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # startupinfo = subprocess.STARTUPINFO()
    # startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    # process = subprocess.Popen(arguments, stdout=subprocess.PIPE,
    #                           stderr=subprocess.STDOUT, stdin=subprocess.PIPE, startupinfo=startupinfo)
    # process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=working_directory)
    global running_process
    running_process = process
    log_thread = Thread(target=log_process, args=(process, "Game finished.\n"))
    log_thread.daemon = True
    log_thread.start()


window = tk.Tk()
window.title("Play online chess with a real chess board by Alper Karayaman")

menu_bar = tk.Menu(window)
connection = tk.Menu(menu_bar, tearoff=False)
connection.add_command(label="Lichess", command=lichess)

menu_bar.add_cascade(label="Connection", menu=connection)

window.config(menu=menu_bar)

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
    import platform

    platform_name = platform.system()
    if platform_name == "Darwin":
        cmd = 'system_profiler SPCameraDataType | grep "^    [^ ]" | sed "s/    //" | sed "s/://"'
        result = subprocess.check_output(cmd, shell=True)
        result = result.decode()
        result = [r for r in result.split("\n") if r]
        OPTIONS.extend(result)
    elif platform_name == "Linux":
        cmd = 'for I in /sys/class/video4linux/*; do cat $I/name; done'
        result = subprocess.check_output(cmd, shell=True)
        result = result.decode()
        result = [r for r in result.split("\n") if r]
        OPTIONS.extend(result)
    else:
        from pygrabber.dshow_graph import FilterGraph

        OPTIONS.extend(FilterGraph().get_input_devices())
except:
    pass
camera.set(OPTIONS[0])
label = tk.Label(menu_frame, text='Select Webcam:')
label.grid(column=0, row=0, sticky=tk.W)
menu = tk.OptionMenu(menu_frame, camera, *OPTIONS)
menu.config(width=max(len(option) for option in OPTIONS), anchor="w")
menu.grid(column=1, row=0, sticky=tk.W)

resolution_frame = tk.Frame(window)
resolution_frame.grid(row=1, column=0, columnspan=2, sticky="W")
resolution = tk.StringVar()
RESOLUTION_OPTIONS = ["Default", "640 x 480", "1280 x 720", "1920 x 1080", "2560 x 1440", "3840 x 2160"]
resolution.set(RESOLUTION_OPTIONS[0])
resolution_label = tk.Label(resolution_frame, text='Select Webcam Resolution:')
resolution_label.grid(column=0, row=0, sticky=tk.W)
resolution_menu = tk.OptionMenu(resolution_frame, resolution, *RESOLUTION_OPTIONS)
resolution_menu.config(width=max(len(option) for option in RESOLUTION_OPTIONS), anchor="w")
resolution_menu.grid(column=1, row=0, sticky=tk.W)

fps_frame = tk.Frame(window)
fps_frame.grid(row=2, column=0, columnspan=2, sticky="W")
fps = tk.StringVar()
FPS_OPTIONS = ["Default", "15", "24", "30", "60", "120", "144", "240"]
fps.set(FPS_OPTIONS[0])
fps_label = tk.Label(fps_frame, text='Select Webcam FPS:')
fps_label.grid(column=0, row=0, sticky=tk.W)
fps_menu = tk.OptionMenu(fps_frame, fps, *FPS_OPTIONS)
fps_menu.config(width=max(len(option) for option in FPS_OPTIONS), anchor="w")
fps_menu.grid(column=1, row=0, sticky=tk.W)

calibration_frame = tk.Frame(window)
calibration_frame.grid(row=3, column=0, columnspan=2, sticky="W")
calibration_mode = tk.StringVar()
CALIBRATION_OPTIONS = ["The board is empty.", "Pieces are in their starting positions.",
                       "Just before the game starts."]
calibration_mode.set(CALIBRATION_OPTIONS[0])
calibration_label = tk.Label(calibration_frame, text='Board Calibration Mode:')
calibration_label.grid(column=0, row=0, sticky=tk.W)
calibration_menu = tk.OptionMenu(calibration_frame, calibration_mode, *CALIBRATION_OPTIONS)
calibration_menu.config(width=max(len(option) for option in CALIBRATION_OPTIONS), anchor="w")
calibration_menu.grid(column=1, row=0, sticky=tk.W)

voice_frame = tk.Frame(window)
voice_frame.grid(row=4, column=0, columnspan=2, sticky="W")
voice = tk.StringVar()
VOICE_OPTIONS = ["Default"]
try:
    import platform

    if platform.system() == "Darwin":
        result = subprocess.run(['say', '-v', '?'], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8')
        for line in output.splitlines():
            if line:
                voice_info = line.split()
                VOICE_OPTIONS.append(f'{voice_info[0]} {voice_info[1]}')
    else:
        import pyttsx3

        engine = pyttsx3.init()
        for v in engine.getProperty('voices'):
            VOICE_OPTIONS.append(v.name)
except:
    pass
voice.set(VOICE_OPTIONS[0])
voice_label = tk.Label(voice_frame, text='Select Voice:')
voice_label.grid(column=0, row=0, sticky=tk.W)
voice_menu = tk.OptionMenu(voice_frame, voice, *VOICE_OPTIONS)
voice_menu.config(width=max(len(option) for option in VOICE_OPTIONS), anchor="w")
voice_menu.grid(column=1, row=0, sticky=tk.W)


def save_promotion(*args):
    outfile = open("promotion.bin", 'wb')
    pickle.dump(promotion.get(), outfile)
    outfile.close()


promotion_frame = tk.Frame(window)
promotion_frame.grid(row=5, column=0, columnspan=2, sticky="W")
promotion = tk.StringVar()
promotion.trace("w", save_promotion)
PROMOTION_OPTIONS = ["Queen", "Knight", "Rook", "Bishop"]
promotion.set(PROMOTION_OPTIONS[0])
promotion_label = tk.Label(promotion_frame, text='Select Promotion Piece:')
promotion_label.grid(column=0, row=0, sticky=tk.W)
promotion_menu = tk.OptionMenu(promotion_frame, promotion, *PROMOTION_OPTIONS)
promotion_menu.config(width=max(len(option) for option in PROMOTION_OPTIONS), anchor="w")
promotion_menu.grid(column=1, row=0, sticky=tk.W)
promotion_menu.configure(state="disabled")

c = tk.Checkbutton(window, text="Find chess board of online game without template images.", variable=no_template)
c.grid(row=6, column=0, sticky="W", columnspan=1)

c1 = tk.Checkbutton(window, text="Make moves of opponent too.", variable=make_opponent)
c1.grid(row=7, column=0, sticky="W", columnspan=1)

c2 = tk.Checkbutton(window, text="Make moves by drag and drop.", variable=drag_drop)
c2.grid(row=8, column=0, sticky="W", columnspan=1)

c2 = tk.Checkbutton(window, text="Speak my moves.", variable=comment_me)
c2.grid(row=9, column=0, sticky="W", columnspan=1)

c3 = tk.Checkbutton(window, text="Speak opponent's moves.", variable=comment_opponent)
c3.grid(row=10, column=0, sticky="W", columnspan=1)

values = ["Do not delay game start.", "1 second delayed game start."] + [str(i) + " seconds delayed game start." for i
                                                                         in range(2, 6)]
default_value = tk.StringVar()
s = tk.Spinbox(window, values=values, textvariable=default_value, width=max(len(value) for value in values))
default_value.set(values[-1])
s.grid(row=11, column=0, sticky="W", columnspan=2)
button_frame = tk.Frame(window)
button_frame.grid(row=12, column=0, columnspan=2, sticky="W")
start = tk.Button(button_frame, text="Start Game", command=start_game)
start.grid(row=0, column=0)
board = tk.Button(button_frame, text="Board Calibration", command=board_calibration)
board.grid(row=0, column=1)
diagnostic_button = tk.Button(button_frame, text="Diagnostic", command=diagnostic)
diagnostic_button.grid(row=0, column=2)
text_frame = tk.Frame(window)
text_frame.grid(row=13, column=0)
scroll_bar = tk.Scrollbar(text_frame)
logs_text = tk.Text(text_frame, background='gray', yscrollcommand=scroll_bar.set)
scroll_bar.config(command=logs_text.yview)
scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
logs_text.pack(side="left")

fields = [no_template, make_opponent, comment_me, comment_opponent, calibration_mode, resolution, fps, drag_drop,
          default_value, camera, voice]
save_file = 'gui.bin'


def save_settings():
    outfile = open(save_file, 'wb')
    pickle.dump([field.get() for field in fields] + [token], outfile)
    outfile.close()


def load_settings():
    if os.path.exists(save_file):
        infile = open(save_file, 'rb')
        variables = pickle.load(infile)
        infile.close()
        global token
        token = variables[-1]
        if variables[-2] in VOICE_OPTIONS:
            voice.set(variables[-2])

        if variables[-3] in OPTIONS:
            camera.set(variables[-3])

        for i in range(9):
            fields[i].set(variables[i])


load_settings()
window.protocol("WM_DELETE_WINDOW", on_closing)
window.mainloop()
