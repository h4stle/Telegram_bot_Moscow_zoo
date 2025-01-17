import json
from urllib.parse import quote



class WorkJSON:
    @staticmethod
    def add_to_bd(id):
        """
        Добавляет нового пользователя в базу данных или обновляет информацию
        для существующего пользователя.
        """
        id = str(id)
        try:
            with open('klients.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                data = json.loads(content) if content else {}
        except FileNotFoundError:
            # Если файл не найден, создаём новую структуру
            data = {}
        if id not in data:
            data[id] = {"kolvo_vopr": 1, "answers": [], "rezultat": '', "otzuv" : ''}
        else:
            # Если клиент уже существует, просто обновляем "kolvo_vopr"
            data[id]["kolvo_vopr"] = 1
        try:
            # Сохраняем изменения
            WorkJSON.save_json('klients.json', data)
        except IOError as e:
            print(f"Ошибка записи в файл: {e}")


    @staticmethod
    def proverka(id):
        """
        Проверяет, существует ли пользователь с данным идентификатором в базе данных 
        и имеется ли информация о количестве вопросов для этого пользователя.
        """
        id = str(id)
        klients = WorkJSON.load_json('klients.json')
        if str(id) in klients:
            return True
        return False
    

    @staticmethod
    def load_json(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading {file_path}: {e}")
            return {}
        

    @staticmethod
    def save_json(file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")



class Quiz:
    @staticmethod
    def get_nomer_voprosa(id):
        """
        Получает номер текущего вопроса для пользователя по его идентификатору.
        """
        id = str(id)
        klients = WorkJSON.load_json('klients.json')
        return str(klients[id]["kolvo_vopr"])



    @staticmethod
    def question(id):
        """
        Получает текущий вопрос викторины для пользователя по его идентификатору.
        """
        id = str(id)
        data = WorkJSON.load_json('que.json')
        questions = data['questions']
        num = Quiz.get_nomer_voprosa(id)
        return questions[str(num)]
    


    @staticmethod
    def uvel_vopr(id):
        """
        Увеличивает номер текущего вопроса для пользователя в базе данных.
        """
        id = str(id)
        klients = WorkJSON.load_json('klients.json')
        klients[id]["kolvo_vopr"] += 1
        WorkJSON.save_json('klients.json', klients)


    @staticmethod
    def vuvod_otvetov(id):
        """
        Возвращает список доступных ответов для текущего вопроса викторины для пользователя.
        """
        id = str(id)
        data = WorkJSON.load_json('que.json')
        num = Quiz.get_nomer_voprosa(id)
        data = data["answers"][num]
        return list(data.keys())
    


    @staticmethod
    def oblulenie_voprosov(id):
        """
        Сбрасывает все данные о викторине для конкретного пользователя, включая количество вопросов и ответы.
        """
        id = str(id)
        klients = WorkJSON.load_json('klients.json')
        klients[id]["kolvo_vopr"] = 1
        klients[id]["answers"] = []
        WorkJSON.save_json('klients.json', klients)



    @staticmethod
    def podschet_rezultatov(id):
        """
        Подсчитывает результат викторины на основе наиболее часто выбранных ответов пользователя.
        """
        id = str(id)
        klients = WorkJSON.load_json('klients.json')
        a = klients[id]["answers"]
        b = {}
        for i in range(0, len(a)):
            if a[i] in b:
                b[a[i]] += 1
            else:
                b[a[i]] = 1
        max_chislo = 1
        for key, value in b.items():
            if value > max_chislo:
                max_chislo = value
                max_key = key
        return max_key



    @staticmethod
    def zapis_rezultata(id):
        """
        Записывает результат викторины в базу данных пользователя.
        """
        id = str(id)
        klients = WorkJSON.load_json('klients.json')
        klients[id]['rezultat'] = Quiz.podschet_rezultatov(id)
        WorkJSON.save_json('klients.json', klients)



    @staticmethod
    def generate_share_links(id):
        """
        Генерирует ссылку для делания репоста в социальную сеть ВКонтакте с результатом викторины.
        """
        id = str(id)
        # Пример текста для кодирования
        animal = Quiz.podschet_rezultatov(id)
        text = f"Мною была пройдена викторина от Московского зоопарка. Наиболее подходящее для меня животное под опекунство - {animal}"
        url = "https://vk.com/share.php?"
        # Кодирование текста
        encoded_text = quote(text)
        encoded_url = (
            f"{url}url=https://t.me/efgh134_bot&"
            f"title={encoded_text}&"
            f"description={encoded_text}"
        )
        return encoded_url
