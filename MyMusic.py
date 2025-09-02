import tkinter as tk
from tkinter import ttk, filedialog
import pygame
import os
import random

class MusicPlayer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("简易音乐播放器 🎵")
        self.geometry("500x600")

        pygame.mixer.init()

        self.playlist = []
        self.current_index = -1
        self.playing = False
        self.track_length = 0
        self.shuffle_on = tk.BooleanVar(value=False)

        # 歌词缓存
        self.lyrics = []

        # 音量（0.0 ~ 1.0）
        self.volume_var = tk.DoubleVar(value=0.5)
        pygame.mixer.music.set_volume(0.5)

        self._build_ui()
        self.update_time()

    def _build_ui(self):
        # 顶部工具栏
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        ttk.Button(toolbar, text="选择文件夹", command=self.choose_folder).pack(side=tk.LEFT)
        ttk.Checkbutton(toolbar, text="随机播放", variable=self.shuffle_on).pack(side=tk.LEFT, padx=10)

        # 播放控制
        ctrl = ttk.Frame(self)
        ctrl.pack(side=tk.TOP, pady=10)
        self.play_btn = ttk.Button(ctrl, text="▶ 播放", command=self.play_pause)
        self.play_btn.pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text="⏮ 上一首", command=self.play_prev).pack(side=tk.LEFT, padx=5)
        ttk.Button(ctrl, text="⏭ 下一首", command=self.play_next).pack(side=tk.LEFT, padx=5)

        # 时间显示
        self.time_var = tk.StringVar(value="--:-- / --:--")
        ttk.Label(self, textvariable=self.time_var).pack(pady=5)

        # 音量调节
        vol_frame = ttk.Frame(self)
        vol_frame.pack(pady=5)
        ttk.Label(vol_frame, text="音量:").pack(side=tk.LEFT)
        vol_slider = ttk.Scale(vol_frame, from_=0, to=1, orient=tk.HORIZONTAL,
                               variable=self.volume_var, command=self.set_volume, length=150)
        vol_slider.pack(side=tk.LEFT, padx=5)

        # 歌词显示
        self.lyrics_box = tk.Text(self, height=10, wrap="word", state="disabled")
        self.lyrics_box.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)

        # 播放列表
        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.listbox.bind("<Double-Button-1>", lambda e: self.play_index(self.listbox.curselection()[0]))

    def choose_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.playlist = [os.path.join(folder, f) for f in os.listdir(folder)
                             if f.lower().endswith((".mp3", ".wav"))]
            self.listbox.delete(0, tk.END)
            for f in self.playlist:
                self.listbox.insert(tk.END, os.path.basename(f))

    def play_pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.play_btn.config(text="▶ 播放")
            self.playing = False
        else:
            if not pygame.mixer.music.get_busy():
                self.play_index(self.current_index if self.current_index >= 0 else 0)
            else:
                pygame.mixer.music.unpause()
            self.play_btn.config(text="⏸ 暂停")
            self.playing = True

    def play_index(self, index):
        if 0 <= index < len(self.playlist):
            self.current_index = index
            file = self.playlist[index]
            pygame.mixer.music.load(file)
            pygame.mixer.music.play()

            # 获取音频时长（用 pygame 自带的方法）
            self.track_length = pygame.mixer.Sound(file).get_length()

            # 加载歌词（如果有 .lrc 文件）
            self.load_lyrics(file)

            self.play_btn.config(text="⏸ 暂停")
            self.playing = True

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

    def update_time(self):
        if self.playing and pygame.mixer.music.get_busy():
            pos = pygame.mixer.music.get_pos() / 1000
            self.time_var.set(f"{self.format_time(pos)} / {self.format_time(self.track_length)}")
            self.update_lyrics(pos)
        self.after(500, self.update_time)

    def format_time(self, seconds):
        if seconds <= 0: return "--:--"
        m, s = divmod(int(seconds), 60)
        return f"{m:02}:{s:02}"

    def set_volume(self, val):
        pygame.mixer.music.set_volume(float(val))

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


if __name__ == "__main__":
    app = MusicPlayer()
    app.mainloop()
