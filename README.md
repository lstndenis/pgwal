 # Описание
Кластер PostgreSQL состоит из трёх Docker-контейнеров (postgres:9.6 с установленными необходимыми библиотеками для Python): Master, Slave и Arbiter. В каждом контейнере запускается скрипт-агент на Python.

Если теряется сеть между Slave и Master, и Arbiter подтверждает эту потерю, Slave становится новым мастером.

Если же у Slave отсутствует связь как с Master, так и с Arbiter, промоут не выполняется.

Промоут осуществляется созданием триггер-файла "/tmp/promote_me".

Slave проверяет связь с Arbiter и Master каждую секунду.

Master проверяет связь с Slave и Arbiter каждые 5 секунд. При отсутствии обеих связей блокируются все входящие подключения на Master с помощью iptables, изменяя политику по умолчанию на DROP.

# Запуск
Чтобы запустить кластер, используйте команду: docker compose up.

Для тестирования кластера запустите на хосте скрипт: python writer.py

# Тестирование кластера
Тест №1: выход из строя Slave (в середине теста на хосте скрипт Writer останавливает контейнер с командой docker compose stop pg-slave).

При synchronous_commit = off: потерь нет.
При synchronous_commit = remote_apply: потерь нет.

Тест №2: выход из строя Master (в середине теста на хосте скрипт Writer останавливает контейнер с командой docker compose stop pg-master).

При synchronous_commit = off: потеряно 24 записи.
При synchronous_commit = remote_apply: потерь нет.