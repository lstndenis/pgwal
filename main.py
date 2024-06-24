import subprocess
import time
from agent import Agent
from flask import Flask, jsonify

app = Flask(__name__)

def runMaster():
    while True:
        print("Проверка наличия соединения с Арбитром...")
        statusA = agent.checkConn2Arbiter()
        statusS = agent.checkConn2Slave()
        if not statusA and not statusS:
            print("Соединения с Арбитром и Слейвом отсутствуют. Блокировка входящих соединений...")
            checkSuccessInsert = subprocess.run(["iptables", "-P", "INPUT", "DROP"], capture_output=True)
            checkSuccessSave = subprocess.run(["iptables-save", ">", "/etc/iptables/rules.v4"], capture_output=True, shell=True)
            if checkSuccessInsert.returncode == 0 and checkSuccessSave.returncode == 0:
                print('Входящие соединения успешно заблокированы')
                break
            else:
                print('Ошибка при вставке правила или сохранении iptables')
        time.sleep(5)

def runSlave():
    while True:
        print("Проверка наличия соединения между Арбитром и Мастером...")
        statusAM = agent.checkConnA2M()

        if statusAM or statusAM is None:
            time.sleep(1)
        else:
            statusM = agent.checkConn2Master()
            print("Проверка, жив ли Мастер: {}".format(statusM))
            if not statusM:
                print('Повышение себя до Мастера...')
                checkSuccess = subprocess.run(["touch", "/tmp/promote_me"], capture_output=True)
                if checkSuccess.returncode == 0:
                    print('Успешное повышение до Мастера')
                    break
                else:
                    print('Ошибка при создании файла-триггера')

def runArbiter():
    @app.route('/check/master', methods=['GET'])
    def checkMaster():
        if agent.checkConn2Master():
            return jsonify({"Master alive": True})
        else:
            return jsonify({"Master alive": False})

    @app.route('/check/arbiter', methods=['GET'])
    def checkArbiter():
        return jsonify({"Arbiter alive": True})

    # Запуск веб-сервера для обработки запросов от Арбитра и Мастер/Слейв
    app.run(debug=False, host='0.0.0.0')
    agent.initConnections()

if __name__ == '__main__':
    agent = Agent()

    if agent.role == "Master":
        runMaster()
    elif agent.role == "Slave":
        runSlave()
    else:
        runArbiter()
