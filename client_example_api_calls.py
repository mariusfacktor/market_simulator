
import requests

# port = 5000
port = 8000

addr = 'http://127.0.0.1'
# addr = 'http://34.82.55.106'

url = addr + ':' + str(port) + '/'


nameA = 'Jean Rose'
nameB = 'Hank Tomford'

resources = ['apple', 'orange']

session_key = 'example'


def create_session():

    data = {'session_key': session_key}
    response = requests.post(url + 'create_session', json=data)
    print(response.json())


def create_person(name, cash, resource_dict={}):

    data = {'session_key': session_key, 'name': name, 'cash': cash, 'resource_dict': resource_dict}

    response = requests.post(url + 'create_person', json=data)
    print(response.json())

    return name


def sell_order(name, resource_type, quantity, price):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}

    response = requests.post(url + 'sell_order', json=data)
    print(response.json())


def buy(name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity}

    response = requests.post(url + 'buy', json=data)
    print(response.json())




def main():

    create_session()
    create_person(nameA, 100, resource_dict={'apple': 10})
    create_person(nameB, 100, resource_dict={'orange': 10})
    sell_order(nameA, 'apple', 10, 5)
    sell_order(nameA, 'apple', 6, 3)

    buy(nameB, 'apple', 2)




if __name__ == '__main__':
    main()





















