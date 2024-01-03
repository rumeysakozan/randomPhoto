import requests
from PIL import (
    Image, 
    ImageDraw,
    ImageFont,
    ImageFilter
)
import io
import os
import textwrap
import logging
import multiprocessing

logging.basicConfig(level=logging.INFO)

PHOTO_URL= "https://api.quotable.io/quotes?limit={}"
PICSUM_URL= "https://picsum.photos/500/300"
IMAGE_FOLDER= "images"
NUMBER_OF_IMAGES= 100

def get_photo(number_of_photos: int=1) -> list:
    url= PHOTO_URL.format(number_of_photos)
    response= requests.get(url)
    data= response.json()
    results= data["results"]
    contents= [result["content"] for result in results]
    return contents

def get_image() -> Image:
    response= requests.get(PICSUM_URL)
    image= Image.open(io.BytesIO(response.content))
    return image

def prepare_image(image: Image) -> Image:
    image= image.convert("RGBA")
    image= image.filter(ImageFilter.GaussianBlur(radius=2))
    image= image.point(lambda p: p*0.5)
    return image

def put_text_on_image(image: Image, text:str) -> Image:
    draw= ImageDraw.Draw(image)
    image_width, image_height= image.size
    
    font= ImageFont.truetype("arial.ttf", size=16)
    margin= 8
    x= margin
    y= image_height/2
    
    lines= textwrap.wrap(text, width=image_width/10)
    for Line in lines:
        draw.text((x,y), Line, font= font, fill="white")
        y+= font.getbbox(Line)[3]+margin
        
    return image

def save_image(image: Image, index: int):
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)
        
    file_path= os.path.join(IMAGE_FOLDER, "photo_image_{}.png".format(index+1))   
    image.save(file_path)
    logging.info(f"Image saved at {file_path}")
    
def process_image(index: int, text: str):
    image= get_image()
    image= prepare_image(image) 
    image= put_text_on_image(image , text)
    save_image(image, index)
    
def main():
    photos= get_photo(NUMBER_OF_IMAGES)
    with multiprocessing.Pool() as pool:
        pool.starmap(process_image, enumerate(photos))
        
if __name__ == "__main__":
    main()                 
   