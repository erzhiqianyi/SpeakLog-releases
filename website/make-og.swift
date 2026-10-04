// Draws the 1200×630 social preview images (og:image / twitter:image), one per language.
//
//     swift website/make-og.swift build/icon-1024.png website/assets
//
// Writes og.png (Chinese), og-en.png and og-ja.png.
import AppKit

let args = CommandLine.arguments
let iconPath = args.count > 1 ? args[1] : "build/icon-1024.png"
let outDir = args.count > 2 ? args[2] : "website/assets"

struct Copy {
    let file, brand, line1, line2, tagline, footnote: String
    let fontRegular, fontBold: String
    var titleSize: CGFloat = 76
}

let copies = [
    Copy(file: "og.png", brand: "SpeakLog", line1: "先说出来，", line2: "再慢慢改好。",
         tagline: "把你说的外语，变成字幕、博客和视频", footnote: "Mac 应用 · 本机转录 · 英语 / 日语 / 中文 / 韩语…",
         fontRegular: "PingFangSC-Regular", fontBold: "PingFangSC-Semibold"),
    Copy(file: "og-en.png", brand: "SpeakLog", line1: "Speak first.", line2: "Polish it later.",
         tagline: "Your spoken practice → subtitles, blogs, videos", footnote: "Mac app · On-device transcription · Japanese / English / Chinese / Korean…",
         fontRegular: "HelveticaNeue", fontBold: "HelveticaNeue-Bold", titleSize: 72),
    Copy(file: "og-ja.png", brand: "SpeakLog スピークログ", line1: "まず話す。", line2: "直すのは、あとで。",
         tagline: "話した外国語を、字幕・ブログ・動画に", footnote: "Mac アプリ · オンデバイス文字起こし · 英語 / 日本語 / 中国語 / 韓国語…",
         fontRegular: "HiraginoSans-W3", fontBold: "HiraginoSans-W7", titleSize: 70),
]

let w = 1200, h = 630
let icon = NSImage(contentsOfFile: iconPath)

func hex(_ v: UInt32, _ a: CGFloat = 1) -> NSColor {
    NSColor(srgbRed: CGFloat((v >> 16) & 0xFF) / 255, green: CGFloat((v >> 8) & 0xFF) / 255,
            blue: CGFloat(v & 0xFF) / 255, alpha: a)
}

for c in copies {
    let rep = NSBitmapImageRep(bitmapDataPlanes: nil, pixelsWide: w, pixelsHigh: h, bitsPerSample: 8,
                               samplesPerPixel: 4, hasAlpha: true, isPlanar: false,
                               colorSpaceName: .deviceRGB, bytesPerRow: 0, bitsPerPixel: 0)!
    NSGraphicsContext.saveGraphicsState()
    NSGraphicsContext.current = NSGraphicsContext(bitmapImageRep: rep)

    // Background: same purple gradient and warm glow as the icon and the page hero.
    NSGradient(starting: hex(0x3A2F7A), ending: hex(0x1B1838))!
        .draw(in: NSRect(x: 0, y: 0, width: w, height: h), angle: -90)
    NSGradient(colors: [hex(0xFF8A3D, 0.32), hex(0xFF8A3D, 0)])!
        .draw(fromCenter: NSPoint(x: 960, y: 420), radius: 0, toCenter: NSPoint(x: 960, y: 420), radius: 520, options: [])
    icon?.draw(in: NSRect(x: 790, y: 150, width: 350, height: 350))

    func text(_ s: String, _ size: CGFloat, bold: Bool, _ color: NSColor, at p: NSPoint) {
        let font = NSFont(name: bold ? c.fontBold : c.fontRegular, size: size)
            ?? .systemFont(ofSize: size, weight: bold ? .heavy : .regular)
        NSAttributedString(string: s, attributes: [.font: font, .foregroundColor: color]).draw(at: p)
    }

    text(c.brand, 34, bold: true, hex(0xFFC9A6), at: NSPoint(x: 80, y: 470))
    text(c.line1, c.titleSize, bold: true, .white, at: NSPoint(x: 76, y: 345))
    text(c.line2, c.titleSize, bold: true, hex(0xFFC928), at: NSPoint(x: 76, y: 245))
    text(c.tagline, 28, bold: false, hex(0xFFFFFF, 0.82), at: NSPoint(x: 80, y: 168))
    text(c.footnote, 20, bold: false, hex(0xFFFFFF, 0.55), at: NSPoint(x: 80, y: 112))

    NSGraphicsContext.restoreGraphicsState()
    let out = outDir + "/" + c.file
    try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: out))
    print("wrote \(out)")
}
