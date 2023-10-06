import gradio as gr
import os
import uuid
import subprocess
from PIL import Image
from dotenv import load_dotenv

TEMP_DIR = "temp"

load_dotenv()
rife_ncnn_vulkan_path = os.getenv("RIFE_NCNN_VULKAN_PATH")


def generate_intermediate_frame(img_path1, img_path2, output_path):
    cmd = [rife_ncnn_vulkan_path, "-0", img_path1, "-1", img_path2, "-o", output_path]
    subprocess.run(cmd)
    return output_path


def generate_gif_from_images(start_img, end_img, output_gif_path="output.gif"):
    image_paths = [start_img, end_img]

    # Generation a intermediate image
    for _ in range(6):
        new_imgs = []
        for j in range(len(image_paths) - 1):
            inter_img = generate_intermediate_frame(image_paths[j], image_paths[j+1], f"temp/generated_{uuid.uuid4().hex}.png")
            new_imgs.extend([image_paths[j], inter_img])

        new_imgs.append(image_paths[-1])
        image_paths = new_imgs

    image_objs = [Image.open(img_path) for img_path in image_paths]
    
    # make gif
    image_objs[0].save(output_gif_path,
                   save_all=True, append_images=image_objs[1:], duration=20, loop=0)
    
    return output_gif_path


def delete_all_files_in_dir(dir_path):
    if not os.path.exists(dir_path):
        print(f"The path {dir_path} does not exist.")
        return
    
    for filename in os.listdir(dir_path):
        file_path = os.path.join(dir_path, filename)
        if os.path.isfile(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error: {file_path} : {e.strerror}")


def process_images(img1, img2):
    # if not exists temp dir
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    output_gif_path = generate_gif_from_images(img1, img2)

    # clean
    delete_all_files_in_dir(TEMP_DIR)

    return output_gif_path


# gradio
image1 = gr.Image(shape=(224, 224), type="filepath", label="Image 1")
image2 = gr.Image(shape=(224, 224), type="filepath", label="Image 2")
output_image = gr.Image(type="filepath", label="Output Image")
gr.Interface(fn=process_images, inputs=[image1, image2], outputs=output_image).launch()