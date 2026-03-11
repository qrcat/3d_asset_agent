huggingface-cli download --repo-type model tencent/Hunyuan3D-2 --local-dir Hunyuan3D-2 --local-dir-use-symlinks False --resume-download
huggingface-cli download --repo-type model tencent/Hunyuan3D-2mv --local-dir Hunyuan3D-2mv --local-dir-use-symlinks False --resume-download
huggingface-cli download --repo-type model Qwen/Qwen-Image-Edit --local-dir Qwen-Image-Edit --local-dir-use-symlinks False --resume-download
huggingface-cli download --repo-type model stabilityai/stable-diffusion-3.5-large-turbo --local-dir stable-diffusion-3.5-large-turbo --local-dir-use-symlinks False --resume-download

cp -r Hunyuan3D-2 ~/
cp -r Hunyuan3D-2mv ~/
cp -r Qwen-Image-Edit ~/
cp -r stable-diffusion-3.5-large-turbo ~/
