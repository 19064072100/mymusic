1. 功能说明

这个播放器能做的事：

选择文件夹 → 自动加载里面的音乐文件（支持 .mp3、.wav）

播放 / 暂停 / 继续

上一首 / 下一首

顺序播放 / 随机播放

显示当前播放时间 / 总时长

调整音量

显示歌词（如果有对应的 .lrc 文件）并高亮当前行
2. 代码讲解（带详细注释）
import tkinter as tk 
from tkinter import ttk, filedialog   # Tkinter 的 GUI 控件
import pygame                        # 用来播放音乐
import os, random                    # 处理文件和随机播放


tkinter：Python 自带的 GUI 库，用来做界面

pygame：多媒体库，用来播放音乐

os：处理文件和路径

random：用来随机选歌
class MusicPlayer(tk.Tk):
    def __init__(self):
        super().__init__()   # 初始化 Tkinter 窗口
        self.title("简易音乐播放器 🎵")   # 窗口标题
        self.geometry("500x600")        # 窗口大小
这里我们写了一个类 MusicPlayer 继承 tk.Tk，这样整个播放器就是一个窗口对象。
        pygame.mixer.init()  # 初始化 pygame 的音频模块

        self.playlist = []   # 播放列表
        self.current_index = -1  # 当前播放的歌曲索引
        self.playing = False     # 是否正在播放
        self.track_length = 0    # 当前歌曲总时长
        self.shuffle_on = tk.BooleanVar(value=False)  # 是否开启随机播放
python
复制代码
        # 歌词缓存
        self.lyrics = []

        # 音量（0.0 ~ 1.0）
        self.volume_var = tk.DoubleVar(value=0.5)
        pygame.mixer.music.set_volume(0.5)  # 默认音量 50%
python
复制代码
        self._build_ui()   # 构建界面
        self.update_time() # 开始更新时间显示
UI 部分
    def _build_ui(self):
        # 顶部工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="选择文件夹", command=self.choose_folder).pack(side=tk.LEFT)
        ttk.Checkbutton(toolbar, text="随机播放", variable=self.shuffle_on).pack(side=tk.LEFT, padx=10)


这里创建了顶部工具栏，包含：

“选择文件夹”按钮

“随机播放”复选框

        # 播放控制
        ctrl = ttk.Frame(self)
        ctrl.pack(side=tk.TOP, pady=10)
        self.play_btn = ttk.Button(ctrl, text="▶ 播放", command=self.play_pause)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text="⏮ 上一首", command=self.play_prev).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text="⏭ 下一首", command=self.play_next).pack(side=tk.LEFT, padx=5)


播放控制区：播放/暂停、上一首、下一首

        # 时间显示
        self.time_var = tk.StringVar(value="--:-- / --:--")
        ttk.Label(self, textvariable=self.time_var).pack(pady=5)


这里用 StringVar 来绑定显示文本，方便随时更新。

        # 音量调节
        vol_frame = ttk.Frame(self)
        vol_frame.pack(pady=5)
        ttk.Label(vol_frame, text="音量:").pack(side=tk.LEFT)
        vol_slider = ttk.Scale(vol_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                               variable=self.volume_var, command=self.set_volume, length=150)
        vol_slider.pack(side=tk.LEFT, padx=5)


音量控制滑块 → 调节范围 0 ~ 1，调用 set_volume。

        # 歌词显示
        self.lyrics_box = tk.Text(self, height=10, wrap="word", state="disabled")
        self.lyrics_box.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        # 播放列表
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind("<Double-Button-1>", lambda e: self.play_index(self.listbox.curselection()[0]))


歌词显示 → 用 Text 控件，支持高亮当前行。

播放列表 → 双击歌曲就能播放。

选择文件夹
    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.playlist = [os.path.join(folder, f) for f in os.listdir(folder)
                             if f.lower().endswith((".mp3", ".wav"))]
            self.listbox.delete(0, tk.END)
            for f in self.playlist:
                self.listbox.insert(tk.END, os.path.basename(f))


这里会扫描文件夹，把 .mp3 和 .wav 文件加到播放列表。

播放/暂停逻辑
    def play_pause(self):
        if self.playing:  # 如果正在播放 → 暂停
            pygame.mixer.music.pause()
            self.play_btn.config(text="▶ 播放")
            self.playing = False
        else:  # 如果没在播放 → 播放
            if not pygame.mixer.music.get_busy():
                self.play_index(self.current_index if self.current_index >= 0 else 0)
            else:
                pygame.mixer.music.unpause()
            self.play_btn.config(text="⏸ 暂停")
            self.playing = True

播放指定歌曲
    def play_index(self, index):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            file = self.playlist[index]
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()

            # 获取音频时长
            self.track_length = pygame.mixer.Sound(file).get_length()

            # 加载歌词
            self.load_lyrics(file)

            self.play_btn.config(text="⏸ 暂停")
            self.playing = True

上一首 / 下一首
    def play_next(self):
        if not self.playlist: return
        if self.shuffle_on.get():
            index = random.randint(0, len(self.playlist)-1)
        else:
            index = (self.current_index + 1) % len(self.playlist)
        self.play_index(index)

    def play_prev(self):
        if not self.playlist: return
        index = (self.current_index - 1) % len(self.playlist)
        self.play_index(index)

更新时间 & 歌词
    def update_time(self):
        if self.playing and pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos() / 1000  # 当前播放位置（秒）
            self.time_var.set(f"{self.format_time(pos)} / {self.format_time(self.track_length)}")
            self.update_lyrics(pos)
        self.after(500, self.update_time)  # 每 0.5 秒刷新一次

时间格式化
    def format_time(self, seconds):
        if seconds <= 0: return "--:--"
        m, s = divmod(int(seconds), 60)
        return f"{m:02}:{s:02}"

音量
    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

加载歌词
    def load_lyrics(self, music_file):
        self.lyrics = []
        lrc_file = os.path.splitext(music_file)[0] + ".lrc"
        if os.path.exists(lrc_file):
            with open(lrc_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("[") and "]" in line:
                        try:
                            t_str, lyric = line.split("]", 1)
                            t_str = t_str.strip("[]")
                            m, s = map(float, t_str.split(":"))
                            self.lyrics.append((m*60+s, lyric.strip()))
                        except:
                            continue
            self.lyrics.sort()

        # 显示歌词
        self.lyrics_box.config(state="normal")
        self.lyrics_box.delete(1.0, tk.END)
        for _, lyric in self.lyrics:
            self.lyrics_box.insert(tk.END, lyric + "\n")
        self.lyrics_box.config(state="disabled")

滚动高亮歌词
    def update_lyrics(self, pos):
        if not self.lyrics: return
        current_line = None
        for i, (t, lyric) in enumerate(self.lyrics):
            if pos >= t:
                current_line = i
        if current_line is not None:
            self.lyrics_box.config(state="normal")
            self.lyrics_box.tag_remove("highlight", "1.0", tk.END)
            line_start = f"{current_line+1}.0"
            line_end = f"{current_line+1}.end"
            self.lyrics_box.tag_add("highlight", line_start, line_end)
            self.lyrics_box.tag_config("highlight", background="yellow")
            self.lyrics_box.see(line_start)
            self.lyrics_box.config(state="disabled")

主程序入口
if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()


这部分是 Python 的标准入口。app.mainloop() 会让 Tkinter 窗口一直运行。

3. 学习要点总结

Tkinter → 窗口、按钮、标签、输入框、列表

pygame.mixer → 音乐播放（加载、播放、暂停、停止、音量控制）

文件处理 → os.listdir 获取目录里的文件

歌词同步 → 解析 .lrc 文件，时间戳 → 高亮显示

定时任务 → Tkinter 的 after 方法实现定时刷新
