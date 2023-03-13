from api import PetFriends
from settings import valid_email, valid_password, foreign_email, foreign_password

import os


class TestPets:
    def setup(self):
        self.pf = PetFriends()

    def test_get_api_key_for_valid_user(self, email=valid_email, password=valid_password):
        """ Проверяем что запрос api ключа возвращает статус 200 и в тезультате содержится слово key"""

        # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
        status, result = self.pf.get_api_key(email, password)

        # Сверяем полученные данные с нашими ожиданиями
        assert status == 200
        assert 'key' in result


    def test_get_all_pets_with_valid_key(self,filter=''):
        """ Проверяем что запрос всех питомцев возвращает не пустой список.
        Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
        запрашиваем список всех питомцев и проверяем что список не пустой.
        Доступное значение параметра filter - 'my_pets' либо '' """

        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        status, result = self.pf.get_list_of_pets(auth_key, filter)

        assert status == 200
        assert len(result['pets']) > 0


    def test_add_new_pet_with_valid_data(self,name='Опасный', animal_type='бультерьер',
                                         age='1', pet_photo='../images/bull.jpg'):
        """Проверяем что можно добавить питомца с валидными данными"""

        # Запрашиваем ключ api и сохраняем в переменую auth_key
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)

        # Добавляем питомца
        status, result = self.pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

        # Сверяем полученный ответ с ожидаемым результатом
        assert status == 200
        assert result['name'] == name


    def test_successful_delete_self_pet(self):
        """Проверяем возможность удаления питомца"""

        # Получаем ключ auth_key и запрашиваем список своих питомцев
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
        if len(my_pets['pets']) == 0:
            self.pf.add_new_pet(auth_key, "Случайная жертва", "нежаль", "3", "../images/bull.jpg")
            _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        # Берём id первого питомца из списка и отправляем запрос на удаление
        pet_id = my_pets['pets'][0]['id']
        status, _ = self.pf.delete_pet(auth_key, pet_id)

        # Ещё раз запрашиваем список своих питомцев
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
        assert status == 200
        assert pet_id not in my_pets.values()

    def test_successful_update_self_pet_info(self, name='Очень опасный', animal_type='кукурузник', age=10):
        """Проверяем возможность обновления информации о питомце"""

        # Получаем ключ auth_key и список своих питомцев
        _, auth_key = self.pf.get_api_key(valid_email, valid_password)
        _, my_pets = self.pf.get_list_of_pets(auth_key, "my_pets")

        # Если список не пустой, то пробуем обновить его имя, тип и возраст
        if len(my_pets['pets']) > 0:
            status, result = self.pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

            # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
            assert status == 200
            assert result['name'] == name
        else:
            # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
            raise Exception("There is no my pets")

    def teardown(self):
        print("Выполнен метод Teardown")