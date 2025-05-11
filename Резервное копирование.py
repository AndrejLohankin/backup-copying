"""
Резервное копирование данных.

Программа выполняет следующие действия:
1. Получает картинки по API с сайта dog.ceo.
2. Создает соответствующую папку на Яндекс.Диске.
3. Сохраняет картинки в папку на Яндекс.Диске.
4. Выводит информацию по фотографиям в json-файл с результатами.
"""

import requests
from tqdm import tqdm
import json


def status_code_dog_ceo():  # проверка доступа к сайту
    url = 'https://dog.ceo/dog-api/'
    response = requests.get(url).status_code
    if response != 200:
        return f'Проблемы с доступом к https://dog.ceo/dog-api'

def status_code_yandex():  # проверка доступа к сайту
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    response = requests.get(url).status_code
    if response != 200:
        return f'Проблемы с доступом к https://cloud-api.yandex.net/v1/disk/resources'

def list_all_sub_breeds(breed):  # функция для получения под-пород
    url = f'https://dog.ceo/api/breed/{breed}/list'
    response = requests.get(url)
    return response.json().get('message')

def get_image(breed):  # функция для получения изображений для породы
    image_urls = []
    if (str(requests.get(f'https://dog.ceo/api/breed/{breed}/images').json().get('message')) !=
            'Breed not found (master breed does not exist)'):
        if len(list_all_sub_breeds(breed))==0:
            url = f'https://dog.ceo/api/breed/{breed}/images'
            response = requests.get(url)
            image_urls = response.json().get('message')
        else:
            for sub_breed in list_all_sub_breeds(breed):
                url = f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random'
                response = requests.get(url)
                image_urls.append(response.json().get('message'))
    else:
        print(f'Такой породы: {breed} не существует.')
        return image_urls
    print (f'С сайта получены изображения для породы: {breed}.')
    return image_urls

def put_folder(breed, OAuth_token):  # функция для создания папки
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    headers = {'Authorization': OAuth_token}
    params = {'path': breed}
    requests.put(url, params=params, headers=headers)
    print(f'Создана папка: {breed} на вашем Яндекс.Диске.')

def post_image(breed, OAuth_token, image_urls):  # функция для загрузки изображений
    url0 = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    headers = {'Authorization': OAuth_token}
    for image_url in tqdm(image_urls, ncols=80, desc='Post_image', colour='blue'):
        params = {
            'path': f'{breed}/{str(image_url).split('/')[-2] + '_' + str(image_url).split('/')[-1]}',
            'url': image_url
        }
        requests.post(url0, params=params, headers= headers)
    print (f'Изображения породы: {breed} скопированы на Яндекс.Диск.')

def get_json(breed, OAuth_token):  # функция для получения json-файла с результатами
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    params = {'path': f'{breed}/',
              'limit': 500
    }
    headers = {'Authorization': OAuth_token}
    response = requests.get(url, headers=headers, params=params)
    exit_json_list = []
    for element in range(len(response.json()["_embedded"]["items"])):
        exit_json_dict = {'file_name': response.json()["_embedded"]["items"][element]["name"]}
        exit_json_list.append (exit_json_dict)
    print(exit_json_list)
    with open(f"{breed}.json", "w", encoding="utf-8") as file:
        json.dump(exit_json_list, file, ensure_ascii=False)

def backup_copying(breed, OAuth_token):  # функция для резервного копирования данных
    status_code_dog_ceo()
    if len (get_image(breed)) == 0:
        exit()
    else:
        status_code_yandex()
        put_folder(breed, OAuth_token)
        print(f'Изображения копируются на Яндекс.Диск. Пожалуйста, подождите.')
        post_image(breed, OAuth_token, get_image(breed))
        get_json(breed, OAuth_token)
        return 'Выполнено резервное копирование.'


breed_ = input("Введите название породы: ")
OAuth_token_ = input("Введите ваш OAuth_token: ")
print(backup_copying(breed_, OAuth_token_))

