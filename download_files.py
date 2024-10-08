import subprocess, os
cwd = os.getcwd()

directories = ["logs", "assets", "outputs", "assets/rmvpe", "assets/hubert", "audios", "assets/rmvpe","assets/weights"]

for directory in directories:
    os.makedirs(os.path.join(cwd, directory), exist_ok=True)

files = {
    "assets/rmvpe/rmvpe.pt": "https://huggingface.co/Rejekts/project/resolve/main/rmvpe.pt",
    "assets/hubert/hubert_base.pt": "https://huggingface.co/Rejekts/project/resolve/main/hubert_base.pt",
    "audios/someguy.mp3": "https://huggingface.co/Rejekts/project/resolve/main/someguy.mp3",
    "audios/somegirl.mp3": "https://huggingface.co/Rejekts/project/resolve/main/somegirl.mp3",
    "audios/unchico.mp3": "https://huggingface.co/Rejekts/project/resolve/main/unchico.mp3",
    "audios/unachica.mp3": "https://huggingface.co/Rejekts/project/resolve/main/unachica.mp3"
}

for file, link in files.items():
    file_path = os.path.join(cwd, file)
    if not os.path.exists(file_path):
        try:
            subprocess.run(['wget', '-O', file_path, link], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Error downloading {file}: {e}")
