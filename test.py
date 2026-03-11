from tools import draw_image, edit_image, generate_3d_model, textured_3d_model

# draw_image("a cat", "output/cat.png")
# edit_image("output/cat.png", "a cat with a hat", "output/cat_with_hat.png")
# generate_3d_model("output/cat_with_hat.png", "output/cat_with_hat.glb")
textured_3d_model(
    "output/cat_with_hat.png",
    "output/cat_with_hat.glb",
    "output/cat_with_hat_textured.glb",
)
