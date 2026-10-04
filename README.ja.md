[English](README.md) · [简体中文](README.zh-CN.md) · **日本語**

# SpeakLog（スピークログ）

**まず話す。直すのは、あとで。**

SpeakLog は語学学習者のための Mac アプリです。外国語で話した音声を読み込むか録音して、Mac 上で文字起こしし、話した文とより自然な言い方を見比べて、字幕・学習ブログ・単語ハイライト付きの字幕動画として書き出せます。

公式サイト：https://speak.erzhiqian.cc/ja/

## ダウンロード

| | |
|---|---|
| **インストーラ（おすすめ）** | [SpeakLog.pkg](https://github.com/erzhiqianyi/SpeakLog-releases/releases/latest/download/SpeakLog.pkg)：ダブルクリックで「アプリケーション」にインストール |
| ディスクイメージ | [Releases](https://github.com/erzhiqianyi/SpeakLog-releases/releases/latest) から `SpeakLog-<バージョン>.dmg` をダウンロードし、アプリを「アプリケーション」にドラッグ |
| 過去のバージョン | [すべての Releases](https://github.com/erzhiqianyi/SpeakLog-releases/releases)（各バージョンに `SHA256SUMS` 付き） |

0.1.1 には Apple silicon Mac（M シリーズ）と macOS 26 以降が必要です。現在のパッケージは Intel Mac に対応していません。インストーラとディスクイメージは Developer ID で署名され、Apple の公証を受けています。

## 使い方ガイド

- [使い始める](https://speak.erzhiqian.cc/ja/guides/getting-started/)
- [話す練習をする](https://speak.erzhiqian.cc/ja/guides/speaking-practice/)
- [字幕・ブログ・動画を書き出す](https://speak.erzhiqian.cc/ja/guides/export/)
- [プライバシーとデータ経路](https://speak.erzhiqian.cc/ja/privacy/)

文字起こし、描画、書き出しはローカルで実行します。クラウド AI は必要な文字や文脈を送り、映像分析は抽出フレームや写真を Claude Code または Codex に渡します。全体設定が端末内モデルでも同様です。自動 AI 校正は初期設定でオンのため、個人的な素材を読み込む前に「設定 → AI」を確認してください。

## このリポジトリの内容

- **Releases**：各バージョンの PKG、DMG、チェックサム、更新内容。
- **`website/`**：公式サイト speak.erzhiqian.cc の静的ページ（簡体字中国語・英語・日本語）。デプロイ方法は [`website/README.md`](website/README.md)（中国語）を参照してください。

アプリのソースコードはここにはありません。

## お問い合わせ

- X：[@itsuki_maer](https://x.com/itsuki_maer)
- メール：[speaklog@erzhiqian.cc](mailto:speaklog@erzhiqian.cc)

質問や要望は、このリポジトリの Issue でも受け付けています。
