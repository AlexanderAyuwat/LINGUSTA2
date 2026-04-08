import os

filepath = r"C:\Users\UsEr\Documents\GitHub\LINGUISTA\static\index.html"
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

new_content = content.replace(r"\${", "${")

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"Replaced {content.count(r'\\${')} occurrences of \\${{")
