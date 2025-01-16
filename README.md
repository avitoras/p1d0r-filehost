# p1d0r-music
## Для начала, установите и настройте docker
https://docs.docker.com/engine/install/


## Клонируйте репозиторий и соберите docker image
```sh
git clone https://github.com/avitoras/p1d0r-music
cd p1d0r-music
sudo docker build -t p1d0r_app .
```
## Получаем SECRET_KEY
```sh
python -c "import secrets; print(secrets.token_hex(16))
```
#### Полученный результат надо запомнить и указать в переменную окружения SECRET_KEY 
## Запуск
```sh
sudo docker run -p 5000:5000 -e SECRET_KEY="Ключик" -e SQLALCHEMY_DATABASE_URI='sqlite:///database.db' p1d0r_app
```
