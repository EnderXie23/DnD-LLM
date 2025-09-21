import requests
import json
import os
import time
from config import Config
import io
import base64
from PIL import Image, PngImagePlugin


class ImageGenerator:

    def __init__(self):
        self.api_key = Config.STABLE_DIFFUSION_API_KEY
        self.ngrok_url = Config.NGROK_URL

    def get_image(self, prompt, counter, dir=None):
        print("Generating image...", end="")
        url = self.ngrok_url + "/sdapi/v1/txt2img"
        payload = {
            "prompt": "masterpiece, best-quality, ultra-detailed, very fine 8K CG wallpaper, " + prompt,
            "negative_prompt": "nsfw, owres, bad anatomy, bad hands, error, missing fingers, extra digit, fewer digits, cropped, worst quality, low quality, normal quality, jpeg artifacts, signature, watermark,text, username, blurry,missing fingers,bad hands,missing arms,ugly,duplicate,morbid,mutilated,tranny,mutated hands,poorly drawn hands,blurry,bad anatomy,bad proportions,extra limbs,cloned face,disfigured,more than 2 nipples,missing arms,extra legs,mutated hands,fused fingers,too many fingers,unclear eyes,lowers,bad anatomy,bad hands,text,error,missing fingers,extra digit,fewer digits,cropped,worst quality,low quality,normal quality,jpeg artifacts,signature,watermark,username,blurry,bad",
            "width": "400",
            "height": "400",
            "samples": "1",
            "num_inference_steps": "50",
            "safety_checker": "no",
            "enhance_prompt": "no",
            "seed": None,
            "guidance_scale": 7.5,
            "multi_lingual": "no",
            "panorama": "no",
            "self_attention": "no",
            "upscale": "no",
        }
        try:
            r = requests.post(url, data=json.dumps(payload))
            print("Generating...")
        except Exception as e:
            print(f"ERROR: Error generating image. {e}")
            return
        if r.status_code != 200:
            print(f"ERROR: Error generating image. Invalid response code {r.status_code}")
            return
        else:
            if "images" in r.json() and len(r.json()["images"]) > 0:
                image = Image.open(io.BytesIO(base64.b64decode(r.json()["images"][0].split(",",1)[0])))
                if dir is not None:
                    image.save(f"{dir}")
                else:
                    image.save(f"resources/images/img_generated_{counter}.png")
                print(f"Image saved to resources/images")
            else:
                if "id" not in r.json():
                    print("ERROR: Error generating image. No ID in response.")
                    print(r.json())
                    return
                count = 0
                while "status" in r.json() and r.json()["status"] == "processing" and count < 60:
                    try:
                        r = requests.post(url, data=json.dumps(payload))
                    except Exception as e:
                        print(f"ERROR: Error generating image. {e}")
                        return
                    if "images" in r.json() and len(r.json()["images"]) > 0:
                        image = Image.open(io.BytesIO(base64.b64decode(r.json()["images"][0].split(",",1)[0])))
                        image.save(f"resources/images/img_generated_{counter}.png")
                        print(f"Image saved to resources/images")
                        break
                    time.sleep(1)
                    count += 1
                print("ERROR: Wait time too long (60s).")
                print(r)

if __name__ == "__main__":
    ig = ImageGenerator()
    ig.get_image("a college soccer boy", 1)