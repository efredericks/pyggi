import os
import shutil

for dirpath, dirs, files in os.walk("out"):
    for f in files:
        if f.endswith("jpg"):
            shutil.copyfile(os.path.join(dirpath,f) , f"t/{f}")
