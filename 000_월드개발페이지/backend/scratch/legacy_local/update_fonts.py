import re

file_path = r"c:\Users\ydh24\Desktop\밋업\python\antigravity\core\components\StylerDashboard.jsx"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Replace arbitrary tailwind sizes by adding 2px
content = re.sub(r'text-\[9px\]', 'text-[11px]', content)
content = re.sub(r'text-\[10px\]', 'text-[12px]', content)
content = re.sub(r'text-\[11px\]', 'text-[13px]', content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Font sizes in StylerDashboard.jsx upgraded successfully!")
