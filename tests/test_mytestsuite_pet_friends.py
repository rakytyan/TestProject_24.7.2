from api import PetFriends
from settings import valid_email, valid_password, foreign_email, foreign_password

import os

class TestPets:
    def setup(self):
        self.pf = PetFriends()

    def test_add_new_pet_without_photo(self,name='Опасный и без фото', animal_type='бультерьер',
                                         age='2', pet_photo=""):
        """Проверяем что можно добавить питомца с валидными данными"""

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    def test_add_photo_to_exist_pet_(self, name='Опасный', animal_type='бультерьер', age='1',
                                         pet_photo='../images/bull.jpg'):
        """Проверяем добавление фото уже зарегистрированного питомца, у которого еще нет фото"""

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age, pet_photo = "")
        assert status == 200

        # Сохраняем id добавленного питомца
        current_id = result['id']

        # Добавляем фото
        status, result = self.pf.add_photo_to_pet(auth_key, pet_id=current_id, pet_photo=pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200

        # Удаляем добавленного при запуске теста питомца, просто правило хорошего тона.
        self.pf.delete_pet(auth_key, pet_id=current_id)

    def test_add_photo_to_pet_with_photo(self,name='Опасный', animal_type='бультерьер', age='1',
                                         pet_photo1='../images/bull.jpg',
                                         pet_photo2='../images/bull2.jpg'):
        """Проверяем добавление фото питомца если у него уже есть фото"""

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo1)
        assert status == 200

        # Сохраняем id добавленного зверя
        current_id = result['id']

        # Добавляем фото поверх существующего
        status, result = self.pf.add_photo_to_pet(auth_key, pet_id=current_id, pet_photo=pet_photo2)

        # Так как в документации не указано, что нельзя добавить фото в карточку питомца с фото
        # то ожидаем, что тест будет успешно пройден.
        assert status == 200

    def test_SQL_injection(self,name='; DROP TABLE PETS', animal_type='бультерьер', age='1',
                                         pet_photo='../images/bull.jpg'):
        """Проверяем устойчивость к атакам SQL injection"""

        # Получаем полный путь изображений питомца и сохраняем в переменные pet_photo1 и pet_photo2
        pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца с опасным именем
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name

    def test_long_name(self,name = "Ужас", name_length=1000000, animal_type='бультерьер', age='1',
                                         pet_photo='../images/bull.jpg'):
        """Проверяем есть ли ограничения для длины имени питомца"""

        # Генерируем длинную строку
        name = name * name_length

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца с опасным именем
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # спасаем сайт "Дом пиомца"
        if status == 200:
            _, _ = self.pf.delete_pet(auth_key, result["id"])

        # Сверяем полученный ответ с ожидаемым результатом
        # В документации нет критериев валидности параметра имя питомца, кроме того что это строка.
        # Тем не менее ожидаем ответ со статусом 400, т.к.  в обратном случае риск того, что доступ
        # к сайту будет затруднен.
        assert status == 400

    def test_post_with_incorrect_photo(self,name='CSV file', animal_type='бультерьер', age='1',
                                         pet_photo='../images/bull.csv'):

        """Проверяем возможность добавления файла в невалидном формате
        (разрешенные JPG, JPEG or PNG) """

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца с неправильной фотографией
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        #  Сверяем полученный ответ с ожидаемым результатом.
        #  Ожидаем  статус 400, т.к. в документации указаны ограничения для формата фото файла.
        assert status == 400

    def test_post_with_string_age_post(self,name='string age', animal_type='бультерьер', age='one year old',
                                         pet_photo='../images/bull.jpg'):
        """Проверяем возможность использования в методе POST невалидных данных,
        а именно - строкового возраста  """

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца с неправильным возрастом
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом. Ожидаем статус 400,
        # т.к. данные в "возрасте" должны принадлежать к классу number
        assert status == 400

    def test_post_with_string_age_put(self,name='string age', animal_type='бультерьер', age='one year old',
                                         pet_photo='../images/bull.jpg'):

            """Проверяем возможность использования строкового возраста в методе PUT"""

            # Получаем ключ auth_key и список своих питомцев
            _, auth_key = self.pf.get_api_key(valid_email, valid_password)
            _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

            # Если список не пустой, то пробуем обновить его имя, тип и возраст
            if len(my_pets['pets']) > 0:
                status, result = self.pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

                # Проверяем что статус ответа = 400
                assert status == 400

            else:
                # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
                raise Exception("There is no my pets")


    def test_for_wrong_key_post_new_pet(self,name='wrong api', animal_type='бультерьер', age='1',
                                         pet_photo='../images/bull.jpg'):
        """Проверяем использование неправильного ключа при запуске метода POST для создания нового питомца.
         Создаем фейковый ключ api и сохраняем в переменую auth_key"""

        auth_key = {'key': '1234-asdf-4567'}

        # Добавляем питомца с неправильным ключем
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом.
        assert status == 403

    def test_for_wrong_api_post_photo(self,name='wrong api', animal_type='бультерьер', age='1',
                                         pet_photo='../images/bull.jpg'):
        """Проверяем использование неправильного ключа при запуске метода POST для
         добавления фото уже существующего питомца.
         """

       # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)


        # Добавляем питомца
        status, result = self.pf.add_new_pet_without_photo(auth_key, name, animal_type, age, pet_photo="")
        assert status == 200

        # Сохраняем id добавленного питомца
        current_id = result['id']

        # Создаем фейковый ключ api и сохраняем в переменую auth_key
        auth_key = {'key': '1234-asdf-4567'}

        # Добавляем фото питомца с неправильным ключем
        status, result = self.pf.add_photo_to_pet(auth_key, pet_id=current_id, pet_photo=pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 403


    def test_get_my_pets_with_valid_key(self,filter='my_pets'):
        """ Проверяем, что запрос на вывод списка с фильтром "my_pets" возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этот ключ
        и фильтр "my_pets" запрашиваем список "моих питомцев" и проверяем, что список не пустой."""

        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0:
            self.pf.add_new_pet(auth_key, "Случайная жертва", "нежаль", "3", "../images/bull.jpg")
            _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        status, result = self.pf.get_list_of_pets(auth_key, filter)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert len(result['pets']) > 0

    def test_add_new_pet_with_empty_data(self,name="", animal_type="тип",
                                         age="20", pet_photo="../images/bull.jpg"):
        """Проверяем, что можно добавить питомца с невалидными данными.
        Проверяем возможность добавления нового питомца с пустым полем "имя" """

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом. Ожидаем статус 400. Хотя в документации
        # не конкретизирован критерий валидности, кроме того, что это должна быть строка. Но очевидно, что
        # создание питомцев с пустыми параметрами приведет к дальнейшим проблемам в работе c api.
        assert status == 400

    def test_add_new_pet_with_empty_type(self, name="Опасный", animal_type="",
                                         age="20", pet_photo="../images/bull.jpg"):
        """Проверяем что можно добавить питомца с невалидными данными.
        Проверяем возможность добавления питомца с пустым полем "тип" """

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 400

    def test_add_new_pet_with_empty_age(self, name="Опасный", animal_type="тип",
                                         age="", pet_photo="../images/bull.jpg"):
        """Проверяем, что можно добавить питомца с невалидными данными, а именно
        возможность добавления питомца с пустым полем "возраст" """

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 400

    def test_delete_foreign_pet(self):
        """Проверяем возможность удаления чужого питомца"""
        # Для получения id чужого животного, регистрируем другой аккаунт с
        # foreign_email и foreign_password.
        # Получаем ключ чужого пользователя запрашиваем список чужих "своих" питомцев
        _, auth_key1 = self.pf.get_api_key(foreign_email, foreign_password)
        _, foreign_pets = self.pf.get_list_of_pets(auth_key1, "my_pets")

        # Проверяем - если список своих чужих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
        if len(foreign_pets['pets']) == 0:
            self.pf.add_new_pet(auth_key1, "Случайная жертва", "нежаль", "3", "../images/bull.jpg")
            _, foreign_pets = self.pf.get_list_of_pets(auth_key1, "my_pets")

        # Получаем id чужого питомца
        id=foreign_pets["pets"][0]["id"]

        # Получаем свой ключ auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Пробуем удалить чужого питомца
        status, _ = self.pf.delete_pet(auth_key, id)

        #  Проверяем действительно ли чужой питомец удален
        _, foreign_pets_after_delete = self.pf.get_list_of_pets(auth_key1, "my_pets")
        id_list = []
        for pet in foreign_pets_after_delete["pets"]:
            id_list.append(pet["id"])
        deleted = False
        if id not in id_list:
            deleted = True

        # Сверяем полученный ответ с ожидаемым результатом.
        # Я считаю, что удаление чужого питомца это серьезный баг, поэтому этот
        # тест не должен иметь статус 200
        assert status != 200
        assert not deleted

        def teardown(self):
            print("Выполнен метод Teardown")


        # # В процессе написания последнего тест первым возникло такое решение.
        # # Тест показал баг. Поэтому я не буду оставлять его для запуска,
        # # оставлю закомментированным, так как абсолютно недопустимо удалять при каждом
        # # тесте одного из 100 чужих питомцев.
        #    def test_delete_foreign_pet(self):
        # """Проверяем возможность удаления чужого питомца"""
        # #  Запрашиваем ключ api и сохраняем в переменую auth_key
        #   _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        # #   запрашиваем список  своих питомцев
        #   _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        # # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
        # if len(my_pets['pets']) == 0:
        #     self.pf.add_new_pet(auth_key, "Случайная жертва", "нежаль", "3", "../images/bull.jpg")
        #     _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        # _, all_pets = self.pf.get_list_of_pets(auth_key,'')
        # print(f"\n all_pets length={len(all_pets['pets'])}")
        # print(f"\n my_pets length={len(my_pets['pets'])}")
        # my_pets_ids = []
        # for my_pet in my_pets['pets']:
        #     my_pets_ids.append(my_pet['id'])
        # # print(my_pets_ids)
        # foreign_pet = ""
        # for pet in all_pets['pets']:
        #     pet_id = pet['id']
        #     # print(f"\n all pet id {pet_id}")
        #     if pet_id not in my_pets_ids:
        #         foreign_pet = pet_id
        #         print(f"Found!!!! {foreign_pet}")
        #     break
        # if len(foreign_pet) > 0:
        #     status, _ = self.pf.delete_pet(auth_key, foreign_pet)
        #     print(status)
        #     assert status == 200
        # else:
        #     assert True