
import requests
import random

# port = 5000
port = 8000

addr = 'http://127.0.0.1'
# addr = 'http://34.82.55.106'

url = addr + ':' + str(port) + '/'


# random.seed(8)

names = ['Martin Tubins', 'Ryan Loaf', 'Andrew Harrington', 'Alicia Kind', 'Zara Barns', 'Trisha Hansen', 'Drake Reiner', 'Peter Thames', 'Thomas Bing',
        'George Christianson', 'Mary Eiger', 'Ronda Meere', 'Barney Opinheimer', 'Rick Zork', 'Walter Moon', 'Simon Baxter', 'Susan Nelson', 'Ed Yon',
        'Charlie Young', 'Mandy Poppins', 'Jon Phelps', 'Harry Platter', 'Sven Beans', 'Donna Waters', 'Neal Borgswith', 'Torance Miller', 'Rod Fried',
        'Ralph Gibbons', 'Scooter Coolidge', 'Jim Roberts', 'Ripley James', 'Ashley Summers', 'Andy Florence', 'Vanessa Craw', 'Ted Moe', 'Tia Alfred']

# resources = ['apple', 'orange', 'tomato']
resources = ['apple', 'orange', 'tomato', 'coconut', 'banana', 'mango']

session_key = 'debug'


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
    quantity = random.randint(1, 30)

    # price = random.randint(1, 15)
    price = round(0.01 + (14.99 * random.random()), 2)

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}

    response = requests.post(url + 'sell_order', json=data)
    print(response.json())


def buy_order(name):

    resource_type = resources[random.randint(0, len(resources) - 1)]
    quantity = random.randint(1, 10)

    # price = random.randint(1, 15)
    price = round(0.01 + (14.99 * random.random()), 2)

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



def examples(num_iter=1):

    for i in range(num_iter):

        print('')

        name = names[random.randint(0, len(names) - 1)]

        sell_order(name)
        buy_order(name)

        sell(name)
        buy(name)


def create_all_people():
    for name in names:
        create_person(name)



def main():

    create_session()

    create_all_people()

    num_iter = 100

    examples(num_iter)





if __name__ == '__main__':
    main()





















