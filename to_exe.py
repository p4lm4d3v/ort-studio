import subprocess
import shutil
import os

print("Cleaning and compilation started...")

if os.path.isdir("build"):
    shutil.rmtree("build", ignore_errors=True)
    print(" - Removed /build directory")

if os.path.isdir("dist"):
    shutil.rmtree("dist", ignore_errors=True)
    print(" - Removed /dist directory")

if os.path.exists("ort_studio.spec"):
    os.remove("ort_studio.spec")
    print(" - Removed ort_studio.spec")

subprocess.run(["py", "-3.12", "-m", "PyInstaller", "--noconsole", "--name", "ort_studio", "main.py"])
os.system('cls' if os.name == 'nt' else 'clear')
print("Clean succusfull!")
print("Compilation succusfull!")
