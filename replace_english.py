from pathlib import Path
import re
root = Path('.')
replacements = [
    (r'zh-CN', 'en'),
    (r'MiroFish', 'KephalosData'),
    (r'mirofish', 'kephalosdata'),
    (r'社交媒体舆论模拟系统', 'Social media opinion simulation system'),
    (r'简洁通用的群体智能引擎，预测万物', 'A clean and general collective intelligence engine, predicting everything'),
    (r'启动入口', 'startup entry point'),
    (r'路径', 'path'),
]
exts={'.html','.vue','.js','.ts','.json','.py','.md','.txt','.toml'}
changed=0
for p in root.rglob('*'):
    if p.is_file() and p.suffix in exts:
        try:
            text = p.read_text(encoding='utf-8')
        except Exception:
            continue
        new_text = text
        for pat, repl in replacements:
            new_text = re.sub(pat, repl, new_text)
        if new_text != text:
            p.write_text(new_text, encoding='utf-8')
            changed += 1
print(f'Updated {changed} files')
