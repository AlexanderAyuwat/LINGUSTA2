import shutil
import os

src_dir = r'C:\Users\UsEr\Downloads'
dest_dir = r'C:\Users\UsEr\Documents\GitHub\LINGUISTA\static\videos'

os.makedirs(dest_dir, exist_ok=True)

files = ['hungry', 'sleepy', 'drink', 'yes']

for name in files:
    src = os.path.join(src_dir, f'{name}.mp4')
    dst = os.path.join(dest_dir, f'{name}.mp4')
    if os.path.exists(src):
        shutil.copy2(src, dst)
        size = os.path.getsize(dst)
        print(f'Copied {name}.mp4  ({size:,} bytes)')
    else:
        print(f'NOT FOUND: {src}')

print('\nVideos folder contents:')
for f in os.listdir(dest_dir):
    print(f'  {f}  ({os.path.getsize(os.path.join(dest_dir, f)):,} bytes)')
