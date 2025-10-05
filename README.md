# SimpleMCSetup

**SimpleMCSetup** は、Minecraft サーバーを簡単にセットアップして起動できる **Python GUI ツール** です。
Windows 向けで、Python と `tkinter`、`requests` が必要です。

---

## Build方法
* pyinstallerを使用します。
```bash
pyinstaller --onefile --windowed main.py
```

## 機能

* Minecraft サーバーの最新バージョンを取得してダウンロード（デフォルトは PaperMC）
* サーバー用ディレクトリの作成
* メモリ設定、サーバーポート、ゲームモード、難易度、ワールドタイプの設定
* `eula.txt` と `server.properties` の自動生成
* `start.bat` で簡単にサーバー起動
* プラグインフォルダの自動生成

---

## 必要条件

* Python 3.8 以上
* `requests` ライブラリ
* `tkinter`（通常 Python に標準で含まれます）

インストール例:

```bash
pip install requests
```

---

## インストール方法

1. 本リポジトリをクローンまたは ZIP ダウンロード
2. Python 3.8 以上をインストール
3. `requests` ライブラリをインストール
4. スクリプトを実行して GUI を起動

```bash
python SimpleMCSetup.py
```

---

## 他のサーバーを利用する場合

デフォルトでは **PaperMC** サーバー用ですが、別のサーバー API を利用することも可能です。
スクリプト内の以下の変数を書き換えてください:

```python
# 例: PaperMC の API を他のサーバー API に変更
PAPER_API_ROOT = "https://api.papermc.io/v2"  # <- 使用したいサーバー API に書き換え
```

### 注意点

* 他のサーバー API が PaperMC と同じ JSON 形式を返す場合は、そのまま利用可能です。
* JSON 構造やダウンロード URL が異なる場合は、スクリプト内で解析やダウンロード処理を修正する必要があります。
* 完全に別サーバーを利用する場合は、ある程度スクリプト改修が必要です。

---

## 使い方

1. GUI でサーバーの保存先フォルダを指定
2. サーバータイプとバージョンを選択
3. メモリ設定やポート、ゲームモードなどを設定
4. 「サーバー作成」をクリックすると自動でファイルを準備
5. `start.bat` を実行してサーバー起動
