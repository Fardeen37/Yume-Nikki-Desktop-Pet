import os
import shutil
import subprocess
import sys

def run():
    print("Building exe...")
    subprocess.run([sys.executable, "-m", "PyInstaller", "Yume Nikki Pet.spec", "--noconfirm"])
    
    # Copy the newly built exe out of dist
    if os.path.exists("dist/Yume Nikki Pet.exe"):
        shutil.copy("dist/Yume Nikki Pet.exe", "Yume Nikki Pet.exe")
    elif os.path.exists("dist/Yume Nikki Pet/Yume Nikki Pet.exe"):
        shutil.copy("dist/Yume Nikki Pet/Yume Nikki Pet.exe", "Yume Nikki Pet.exe")

    github_dir = "../Yume_Nikki_AI_Pet_GitHub"
    print(f"Creating GitHub directory at {github_dir}...")
    if not os.path.exists(github_dir):
        os.makedirs(github_dir)
        
    files_to_copy = ["main.py", "ai_brain.py", "screen_tracker.py", "make_icon.py", "requirements.txt", "icon.ico", "Yume Nikki Pet.spec", "Yume Nikki Pet.exe"]
    dirs_to_copy = ["Images", "Sounds"]
    
    for f in files_to_copy:
        if os.path.exists(f):
            shutil.copy(f, os.path.join(github_dir, f))
            
    for d in dirs_to_copy:
        if os.path.exists(d):
            dest = os.path.join(github_dir, d)
            if os.path.exists(dest):
                shutil.rmtree(dest)
            shutil.copytree(d, dest)
            
    print("Done packaging.")

if __name__ == "__main__":
    run()
