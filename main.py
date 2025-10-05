import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import requests
import os

PAPER_API_ROOT = "https://api.papermc.io/v2"

PROPERTY_DEFAULTS = {
    "server-port": "25565",
    "motd": "A Minecraft Server",
    "max-players": "20",
    "online-mode": "true",
    "level-name": "world",
    "gamemode": "survival",
    "difficulty": "1",
    "pvp": "true",
    "level-type": "default"
}

GAMEMODES = ["survival", "creative", "adventure", "spectator"]
DIFFICULTIES = {"peaceful": "0", "easy": "1", "normal": "2", "hard": "3"}
WORLD_TYPES = ["default", "flat", "largeBiomes", "amplified", "buffet"]

class SimpleMCSetup:
    def __init__(self, root):
        self.root = root
        root.title("Minecraft サーバーセットアップ")
        root.geometry("400x500")
        root.configure(bg="#f0f0f0")

        self.version = tk.StringVar()
        self.install_dir = tk.StringVar(value=str(Path.cwd()))
        self.ram = tk.StringVar(value="2048")
        self.port = tk.StringVar(value=PROPERTY_DEFAULTS["server-port"])
        self.gamemode = tk.StringVar(value=PROPERTY_DEFAULTS["gamemode"])
        self.difficulty = tk.StringVar(value="normal")
        self.world_type = tk.StringVar(value=PROPERTY_DEFAULTS["level-type"])
        self.eula_agree = tk.BooleanVar(value=False)

        self.create_input("バージョン", 0, self.version, button=("取得", self.fetch_versions))
        self.create_input("インストール先", 1, self.install_dir, button=("参照", self.browse_dir))
        self.create_input("割当メモリ(MB)", 2, self.ram)
        self.create_input("サーバーポート", 3, self.port)
        self.create_combobox("ゲームモード", 4, self.gamemode, GAMEMODES)
        self.create_combobox("難易度", 5, self.difficulty, list(DIFFICULTIES.keys()))
        self.create_combobox("ワールドタイプ", 6, self.world_type, WORLD_TYPES)
        tk.Checkbutton(root, text="EULAに同意する", variable=self.eula_agree, bg="#f0f0f0").grid(row=7, column=0, columnspan=2, pady=10, sticky="w")

        self.setup_btn = tk.Button(root, text="セットアップ", command=self.setup_server, bg="#4CAF50", fg="white", width=20)
        self.start_btn = tk.Button(root, text="サーバー起動", command=self.start_server, bg="#2196F3", fg="white", width=20)
        self.setup_btn.grid(row=8, column=0, columnspan=2, pady=10)
        self.start_btn.grid(row=9, column=0, columnspan=2, pady=10)

    def create_input(self, label, row, variable, button=None):
        ttk.Label(self.root, text=label, background="#f0f0f0").grid(row=row, column=0, padx=10, pady=6, sticky="w")
        entry = ttk.Entry(self.root, textvariable=variable, width=25)
        entry.grid(row=row, column=1, padx=10, pady=6, sticky="w")
        if button:
            tk.Button(self.root, text=button[0], command=button[1]).grid(row=row, column=2, padx=10, pady=6)

    def create_combobox(self, label, row, variable, values):
        ttk.Label(self.root, text=label, background="#f0f0f0").grid(row=row, column=0, padx=10, pady=6, sticky="w")
        ttk.Combobox(self.root, textvariable=variable, values=values, width=23).grid(row=row, column=1, padx=10, pady=6, sticky="w")

    def fetch_versions(self):
        try:
            r = requests.get(f"{PAPER_API_ROOT}/projects/paper", timeout=10)
            r.raise_for_status()
            versions = sorted(r.json().get("versions", []), reverse=True)
            self.version.set(versions[0] if versions else "")
        except Exception as e:
            messagebox.showerror("エラー", f"バージョン取得失敗:\n{e}")

    def browse_dir(self):
        d = filedialog.askdirectory(initialdir=self.install_dir.get())
        if d:
            self.install_dir.set(d)

    def setup_server(self):
        version = self.version.get().strip()
        dir_path = Path(self.install_dir.get())
        ram_mb = self.ram.get().strip()
        port = self.port.get().strip()
        gamemode = self.gamemode.get().strip()
        difficulty = self.difficulty.get().strip()
        world_type = self.world_type.get().strip()

        if not ram_mb.isdigit():
            ram_mb = "2048"
        if not port.isdigit():
            port = PROPERTY_DEFAULTS["server-port"]
        if gamemode not in GAMEMODES:
            gamemode = PROPERTY_DEFAULTS["gamemode"]
        if difficulty not in DIFFICULTIES:
            difficulty = "normal"
        if world_type not in WORLD_TYPES:
            world_type = PROPERTY_DEFAULTS["level-type"]
        if not version or not dir_path.exists():
            messagebox.showwarning("未設定", "バージョンやディレクトリを正しく設定してください")
            return
        if not self.eula_agree.get():
            messagebox.showwarning("EULA未同意", "EULAに同意する必要があります。")
            return

        try:
            dir_path.mkdir(parents=True, exist_ok=True)
            r = requests.get(f"{PAPER_API_ROOT}/projects/paper/versions/{version}", timeout=10)
            r.raise_for_status()
            builds = r.json().get("builds", [])
            if not builds:
                raise Exception("ビルドが見つかりません")
            build = max(builds)
            jar_url = f"{PAPER_API_ROOT}/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar"
            jar_name = f"paper-{version}-{build}.jar"
            jar_path = dir_path / jar_name
            with requests.get(jar_url, stream=True) as rjar:
                rjar.raise_for_status()
                with open(jar_path, "wb") as f:
                    for chunk in rjar.iter_content(chunk_size=8192):
                        f.write(chunk)

            (dir_path / "eula.txt").write_text("eula=true\n", encoding="utf-8")

            server_properties = PROPERTY_DEFAULTS.copy()
            server_properties.update({
                "server-port": port,
                "motd": f"Minecraft Server ({version})",
                "gamemode": gamemode,
                "difficulty": DIFFICULTIES[difficulty],
                "level-type": world_type
            })
            with open(dir_path / "server.properties", "w", encoding="utf-8") as f:
                for k, v in server_properties.items():
                    f.write(f"{k}={v}\n")

            bat_content = f"@echo off\njava -Xmx{ram_mb}M -Xms{ram_mb}M -jar {jar_name} nogui\npause\n"
            (dir_path / "start.bat").write_text(bat_content, encoding="utf-8")

            Path(dir_path / "plugins").mkdir(exist_ok=True)
            Path(dir_path / server_properties["level-name"]).mkdir(exist_ok=True)

            messagebox.showinfo("完了",
                                f"{dir_path} にサーバーファイルを生成しました。\nJAR: {jar_name}\nEULA: eula.txt\nstart.bat: start.bat\nserver.properties 作成済み")
        except Exception as e:
            messagebox.showerror("エラー", f"セットアップ失敗:\n{e}")

    def start_server(self):
        dir_path = Path(self.install_dir.get())
        jars = list(dir_path.glob("*.jar"))
        if not jars:
            messagebox.showwarning("未準備", "JARファイルが存在しません。セットアップを先に行ってください。")
            return
        os.startfile(dir_path / "start.bat")


if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleMCSetup(root)
    root.mainloop()
