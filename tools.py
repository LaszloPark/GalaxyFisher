import sys,os
import json
import cv2
from ImgUtil import match_image

def add_config(source_path:str,templater_path:str,json_path:str="./config.json"):

    source = cv2.imread(source_path)
    templater = cv2.imread(templater_path)

    templater_name = os.path.basename(templater_path)

    key = os.path.splitext(templater_name)[0]
    value_dict = {}
    
    # value_dict["name"] = key
    value_dict["enable"] = True
    value_dict["path"] = templater_name
    value_dict["rect"] = match_image(source,templater,0.95)
    value_dict["threshold"] = 0.95
    
    add_data_to_json(json_path,{key:value_dict})


def add_data_to_json(file_path, new_data):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        data.update(new_data)
        new_data = data
    except FileNotFoundError as e:
        print("未能找到config.json，将重新创建此文件。")
    except Exception as e:
        print("An error occured: {}".format(e))
        user_input = input("读取config.json时出现错误。将覆盖已存在的config.json，是否确定？（[Y/n]）")
        while user_input:
            if user_input in {None,'Y','y'}:
                break
            if user_input in {'N','n'}:
                sys.exit()

    with open(file_path, 'w') as file:
        json.dump(new_data, file,indent=4) 
    print("写入完成。")


if __name__ == "__main__":
    add_config("./images/bar&pull.png","./templaters/bar.png")