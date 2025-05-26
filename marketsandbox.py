
import requests
import random

# port = 5000
port = 8000

url = 'http://127.0.0.1' + ':' + str(port) + '/'
# addr = 'http://34.82.55.106' + ':' + str(port) + '/'
# addr = 'https://market-sim.serverpit.com' + '/'



def create_session():

    data = {'session_key': session_key}
    response = requests.post(url + 'create_session', json=data)
    print(response.json())


def create_person(name=None):
    if not name:
        name = names[random.randint(0, len(names) - 1)]
    cash = random.randint(100, 1000)
    resource_dict = {}

    for resource in resources:
        if random.randint(0, 1):
            resource_dict[resource] = random.randint(0, 60)

    data = {'session_key': session_key, 'name': name, 'cash': cash, 'resource_dict': resource_dict}

    response = requests.post(url + 'create_person', json=data)
    print(response.json())

    return name


def sell_order(name):

    resource_type = resources[random.randint(0, len(resources) - 1)]
    quantity = random.randint(1, 20)

    price = round(0.29 + (8.99 * random.random()), 2)


    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}

    response = requests.post(url + 'sell_order', json=data)
    print(response.json())


def buy_order(name):

    resource_type = resources[random.randint(0, len(resources) - 1)]
    quantity = random.randint(1, 15)

    price = round(0.29 + (8.99 * random.random()), 2)


    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}

    response = requests.post(url + 'buy_order', json=data)
    print(response.json())


def buy(name):

    resource_type = resources[random.randint(0, len(resources) - 1)]
    quantity = random.randint(1, 15)

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity}

    response = requests.post(url + 'buy_now', json=data)
    print(response.json())


def sell(name):

    resource_type = resources[random.randint(0, len(resources) - 1)]
    quantity = random.randint(1, 15)

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity}

    response = requests.post(url + 'sell_now', json=data)
    print(response.json())





def main():
    print('hi')



if __name__ == '__main__':
    main()





















