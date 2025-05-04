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


def get_image(breed):  # функция для получения изображений для породы
    url = f'https://dog.ceo/api/breed/{breed}/images'
    response = requests.get(url)
    image_urls = response.json().get('message')
    image_names = []
    for image_url in image_urls:
        image_names.append(str(image_url).split('/')[-1])
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
            'path': f'{breed}/{breed}_{str(image_url).split("/")[-1]}',
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

def backup_copying(breed, OAuth_token):  # функция для резервного копирования данных
    image_urls = get_image(breed)
    print(image_urls)
    put_folder(breed, OAuth_token)
    print(f'Изображения копируются на Яндекс.Диск. Пожалуйста, подождите.')
    post_image(breed, OAuth_token, image_urls)
    get_json(breed, OAuth_token)
    return 'Выполнено резервное копирование.'


breed_ = input("Введите название породы: ")
OAuth_token_ = input("Введите ваш OAuth_token: ")
print(backup_copying(breed_, OAuth_token_))
