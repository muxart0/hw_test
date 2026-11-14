import requests

url = "https://jsonplaceholder.typicode.com/posts"

response = requests.get(url)

if response.status_code == 200:
    posts = response.json()

    for post in posts[:5]:
        print("Заголовок:", post["title"])
        print("Текст:", post["body"])
        print("-" * 50)
else:
    print("Ошибка запроса:", response.status_code)
