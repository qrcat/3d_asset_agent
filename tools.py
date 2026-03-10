import time
import os

os.environ["HY3DGEN_MODELS"] = "."
import torch
import trimesh
from PIL import Image
from typing import Optional
from diffusers import DiffusionPipeline, QwenImageEditPipeline, StableDiffusion3Pipeline
from hy3dgen.rembg import BackgroundRemover
from hy3dgen.shapegen import Hunyuan3DDiTFlowMatchingPipeline
from hy3dgen.texgen import Hunyuan3DPaintPipeline


def _ensure_parent_dir(path: str) -> None:
    parent_dir = os.path.dirname(path)
    if parent_dir:
        os.makedirs(parent_dir, exist_ok=True)


def draw_image(prompt: str, output: str):
    print("draw_image:", prompt)

    pipe = StableDiffusion3Pipeline.from_pretrained(
        "stable-diffusion-3.5-large-turbo", torch_dtype=torch.bfloat16
    )
    pipe = pipe.to("cuda")

    image = pipe(
        prompt,
        num_inference_steps=4,
        guidance_scale=0.0,
    ).images[0]

    print("save image:", output)
    _ensure_parent_dir(output)
    image.save(output)


def edit_image(image: str, prompt: str, output: str):
    print("edit_image:", image, prompt)
    
    pipeline = QwenImageEditPipeline.from_pretrained("Qwen-Image-Edit")

    pipeline.to(torch.bfloat16)
    pipeline.to("cuda")
    pipeline.set_progress_bar_config(disable=None)

    image = Image.open(image).convert("RGB")
    inputs = {
        "image": image,
        "prompt": prompt,
        "generator": torch.manual_seed(0),
        "true_cfg_scale": 4.0,
        "negative_prompt": " ",
        "num_inference_steps": 50,
    }

    with torch.inference_mode():
        output_image = pipeline(**inputs).images[0]

    print("save image:", output)
    _ensure_parent_dir(output)
    output_image.save(output)


def generate_3d_model(
    front: str,
    output: str,
    left: Optional[str] = None,
    back: Optional[str] = None,
) -> str:
    if left is None and back is None:
        pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            "Hunyuan3D-2", subfolder="hunyuan3d-dit-v2-0", variant="fp16"
        )
    else:
        pipeline = Hunyuan3DDiTFlowMatchingPipeline.from_pretrained(
            "Hunyuan3D-2mv", subfolder="hunyuan3d-dit-v2-mv", variant="fp16"
        )

    images = {"front": front}
    if left is not None:
        images["left"] = left
    if back is not None:
        images["back"] = back

    for key in images:
        if images[key] is None: continue
        image = Image.open(images[key]).convert("RGBA")
        if image.mode == "RGB":
            rembg = BackgroundRemover()
            image = rembg(image)
        images[key] = image

    start_time = time.time()
    mesh = pipeline(
        image=images["front"] if left is None and back is None else images,
        num_inference_steps=50,
        octree_resolution=380,
        num_chunks=20000,
        generator=torch.manual_seed(12345),
        output_type="trimesh",
    )[0]
    print("--- %s seconds ---" % (time.time() - start_time))

    print("save shape model:", output)
    _ensure_parent_dir(output)
    mesh.export(output)


def textured_3d_model(image: str, model: str, output: str):
    pipeline_texgen = Hunyuan3DPaintPipeline.from_pretrained("Hunyuan3D-2")

    image = Image.open(image).convert("RGBA")
    if image.mode == "RGB":
        rembg = BackgroundRemover()
        image = rembg(image)

    mesh = trimesh.load(model)
    mesh = pipeline_texgen(mesh, image=image)

    print("save textured model:", output)
    _ensure_parent_dir(output)
    mesh.export(output)
