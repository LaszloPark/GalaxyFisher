import cv2
import numpy as np

flags = cv2.IMREAD_COLOR
# flags = cv2.IMREAD_UNCHANGED

WHITE = [255,255,255]
BALCK = [0,0,0]
PURPLE = [128,0,128]


def read_from_path(image_path,flags=flags):
    return cv2.imread(image_path,flags)


def read_from_bytes(bytes):
    image = cv2.imdecode(np.fromstring(bytes, np.uint8), flags)
    return image


def read_from_bytearray(bytearray):
    image = cv2.imdecode(np.frombuffer(bytearray, np.uint8), flags)
    return image


def read_from_pil(image,rgba=False):
    if not rgba:
        return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGB2BGR)
    else:
        return cv2.cvtColor(np.asarray(image), cv2.COLOR_RGBA2BGRA)


def crop_image(image, rect):
    # TEST
    # cv2.imwrite("./source_image.jpg",image)
    # if rect:
    #     cv2.imwrite('./output_image.jpg', image[rect[1]:rect[3],rect[0]:rect[2]])
    # else:
    #     cv2.imwrite('./output_image.jpg', image)
    return image if rect is None else image[rect[1]:rect[3],rect[0]:rect[2]]


# def get_image_hash(image):
#     import imagehash
#     return imagehash.phash(image)


# def match_image_hash(image1, image2):
#     hash1 = get_image_hash(image1)
#     hash2 = get_image_hash(image2)
#     return 1 - (hash1 - hash2)/len(hash1.hash)**2


def match_image_mse(image1,image2):
    mse = ((image1 - image2) ** 2).mean()
    if mse >= 1:
        return 0
    else:
        return 1 - mse


def get_image_mask(image):
    if image.shape[2] == 4:
        channels = cv2.split(image)
        alpha_channel = np.array(channels[3]) 
        return cv2.merge([alpha_channel,alpha_channel,alpha_channel])
    elif image.shape[2] == 3:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        threshold = 1
        black_region =  cv2.threshold(gray_image, threshold, 255, cv2.THRESH_BINARY)[1]
        return cv2.merge([black_region,black_region,black_region])
    else:
        return None


def match_image(image,templater,threshold,mask=None):
    _image = image.copy()
    _templater = templater.copy()
    height,width,_ = _templater.shape
    if mask is None:
        _image = cv2.cvtColor(_image, cv2.COLOR_BGR2GRAY)
        _templater = cv2.cvtColor(_templater, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(_image, _templater, cv2.TM_CCOEFF_NORMED)
    else:
        # 在用 cv2.IMREAD_COLOR 读取 png 文件时，透明像素呈黑色。考虑到钓鱼需求，使用红通道
        _image[:,:,:2] = 255
        _templater[:,:,:2] = 255
        res = cv2.matchTemplate(_image, _templater, cv2.TM_CCOEFF_NORMED,None,mask)
    score = np.max(res)
    loc = np.where(res == score)
    if score > threshold:
        return [int(arr) for arr in [loc[1], loc[0], loc[1] + width, loc[0] + height]]
    else:
        return None


def match_pixel_color(image,color,tolerance=2):
    color = np.array(color)
    diff = np.abs(image - color)
    matches = np.all(diff <= tolerance, axis=-1)
    
    if matches.any():
        x, y = np.column_stack(np.where(matches))[0]
        return (x, y)
    return None