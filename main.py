#!/usr/bin/python3
# -*- coding: utf-8 -*-
import json
import mimetypes
import os

import requests
import pandas as pd
from optoins import HEADERS

POISION = False
FULL_NAME = False
MONEY = False
COMMENT = False
STATUS = False

path_to_base = r'C:\Users\Егор\PycharmProjects\test_huntflow\data_base\Тестовая база.xlsx'


def open_base(path_to_base):
    global POISION, FULL_NAME, MONEY, COMMENT, STATUS
    if path_to_base:
        data = pd.read_excel(path_to_base)

        POISION = data['Должность']
        FULL_NAME = data['ФИО']
        MONEY = data['Ожидания по ЗП']
        COMMENT = data['Комментарий']
        STATUS = data['Статус']


open_base(path_to_base)


class Vyxy:
    def __init__(self):
        self.headers = HEADERS
        self.organization_id = False
        self.company_id = False
        self.id_vacancy = False
        self.id_vacancie_frontend = False
        self.id_vacancie_sale = False
        self.id_resume = False
        self.status_candidate = False

    def get_company_id(self):
        response = requests.get("https://dev-100-api.huntflow.dev/accounts", headers=self.headers)
        data_company = json.loads(response.text)
        self.company_id = data_company['items'][0]['id']

    def get_status_candidate(self):
        response = requests.get(f'https://dev-100-api.huntflow.dev/account/{self.company_id}/vacancy/statuses',
                                headers=self.headers)
        self.status_candidate = json.loads(response.text)
        for i in self.status_candidate['items']:
            if i['name'] == STATUS[0]:
                status_2 = i['id']
            if i['name'] == STATUS[1]:
                status_4 = i['id']
            if i['name'] == STATUS[2]:
                status_7 = i['id']
            if i['name'] == STATUS[3]:
                status_10 = i['id']

        return [status_2, status_4, status_7, status_10]

    def get_list_vacancies(self):
        response = requests.get(f'https://dev-100-api.huntflow.dev/account/{self.company_id}/vacancies',
                                headers=self.headers)
        list_vacancies = json.loads(response.text)
        data_list_vacancies = list_vacancies['items']
        for i in data_list_vacancies:
            if i['position'] == 'Frontend-разработчик':
                self.id_vacancie_frontend = i['id']
            if i['position'] == 'Менеджер по продажам':
                self.id_vacancie_sale = i['id']

    def loading_files(self, name_file, path_file):
        mimetypes.init()
        ext_data = os.path.splitext(name_file)
        if len(ext_data) > 1:
            mime_type = mimetypes.types_map.get(ext_data[len(ext_data) - 1]) or 'application/zip'
        else:
            mime_type = 'application/zip'

        files = {'file': (name_file, open(path_file, 'rb'), mime_type)}

        headers = {
            "Authorization": "Bearer 71e89e8af02206575b3b4ae80bf35b6386fe3085af3d4085cbc7b43505084482",
            'X-File-Parse': 'true',
        }

        response = requests.post(f'https://dev-100-api.huntflow.dev/account/{self.company_id}/upload', headers=headers,
                                 files=files)

        return response.json()

    def adding_candidate_to_base_and_vacancy_and_add_file_candidate(self, file_name, file_path):

        data_file = self.loading_files(file_name, file_path)

        status_2, status_4, status_7, status_10 = self.get_status_candidate()
        if file_name == 'Глибин Виталий Николаевич.doc':
            k = 0
            comment = COMMENT[0]
            status = status_2
            money = MONEY[0]
        elif file_name == 'Танский Михаил.pdf':
            k = 1
            comment = COMMENT[1]
            status = status_4
            money = MONEY[1]
        elif file_name == 'Корниенко Максим.doc':
            k = 2
            comment = COMMENT[2]
            status = status_7
            money = MONEY[3]
        elif file_name == 'Шорин Андрей.pdf':
            k = 3
            comment = COMMENT[3]
            status = status_10
            money = MONEY[3]
        else:
            k = 0
            comment = 'начинаем работать'
            status = 1
            money = 80000
        package_apli = {
            "last_name": data_file["fields"]["name"]["last"],
            "first_name": data_file["fields"]["name"]["first"],
            "middle_name": data_file["fields"]["name"]["middle"],
            "phone": data_file["fields"]["phones"][0],
            "email": data_file["fields"]["email"],
            "position": data_file["fields"]["experience"][0]["position"],
            "company": None if data_file["fields"]["experience"][0]["company"] is None else
            data_file["fields"]["experience"][0][
                "company"],
            "money": money,
            "birthday_day": 11 if data_file["fields"]["birthdate"] is None else data_file["fields"]["birthdate"]["day"],
            "birthday_month": 11 if data_file["fields"]["birthdate"] is None else data_file["fields"]["birthdate"][
                "month"],
            "birthday_year": 1999 if data_file["fields"]["birthdate"] is None else data_file["fields"]["birthdate"][
                "year"],
            "photo": data_file["photo"]["id"],
            "externals": [{
                "data": {"body": data_file["text"]},
                "auth_type": "NATIVE",
                "files": [{"id": data_file["id"]}],
                "account_source": 1
            }
            ]}
        response = requests.post(f'https://dev-100-api.huntflow.dev/account/{self.company_id}/applicants',
                                 headers=self.headers, data=json.dumps(package_apli))
        data_response_base = json.loads(response.text)
        self.id_resume = int(data_response_base['id'])
        data_for_add_vacanci = {
            "vacancy": int(self.id_vacancie_frontend) if k == 0 or k == 1 else int(self.id_vacancie_sale),
            "status": status,
            "comment": comment,
            "files": [
                {
                    "id": data_file["id"]
                }
            ],
            "rejection_reason": None
        }
        response = requests.post(
            f'https://dev-100-api.huntflow.dev/account/{self.company_id}/applicants/{self.id_resume}/vacancy',
            headers=self.headers, data=json.dumps(data_for_add_vacanci))


if __name__ == '__main__':

    from sys import argv

    try:
        path_to_base = argv[1]
        name_to_file_resume = argv[2]
        path_to_file_resume = argv[3]
    except:
        path_to_base = r'C:\Users\Егор\PycharmProjects\test_huntflow\data_base\Тестовая база.xlsx'
        path_to_file_resume = r''
        name_to_file_resume = r''

    go = Vyxy()
    go.get_company_id()
    go.get_status_candidate()
    go.get_list_vacancies()
    if path_to_base and name_to_file_resume and path_to_file_resume:
        open_base(path_to_base)
        go.adding_candidate_to_base_and_vacancy_and_add_file_candidate(name_to_file_resume, path_to_file_resume)
    else:
        open_base(path_to_base)
        name_to_file_resume = 'Глибин Виталий Николаевич.doc'
        path_to_file_resume = r'C:\Users\Егор\PycharmProjects\test_huntflow\data_base\resume\Frontend-разработчик\Глибин Виталий Николаевич.doc'
        go.adding_candidate_to_base_and_vacancy_and_add_file_candidate(name_to_file_resume, path_to_file_resume)
