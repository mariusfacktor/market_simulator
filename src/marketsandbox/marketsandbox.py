
import requests
import random

port = 8000

url = 'http://127.0.0.1' + ':' + str(port) + '/'
# addr = 'http://34.82.55.106' + ':' + str(port) + '/'
# addr = 'https://market-sim.serverpit.com' + '/'



def create_session(session_key):

    data = {'session_key': session_key}

    try:
        response = requests.post(url + 'create_session', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        return_session_key = response.json()['data']['session_key']
    else:
        return_session_key = None


    return return_session_key




def create_person(session_key, name, money, resource_dict={}):

    data = {'session_key': session_key, 'name': name, 'cash': money, 'resource_dict': resource_dict}

    try:
        response = requests.post(url + 'create_person', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        person_id = response.json()['data']['person_id']
    else:
        person_id = None

    return person_id


def sell_limit_order(session_key, name, resource_type, quantity, price):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}


    try:
        response = requests.post(url + 'sell_order', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        order_id = response.json()['data']['order_id']
    else:
        order_id = None

    return order_id



def sell_market_order(session_key, name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity}


    try:
        response = requests.post(url + 'sell_now', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def buy_limit_order(session_key, name, resource_type, quantity, price):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}


    try:
        response = requests.post(url + 'buy_order', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        order_id = response.json()['data']['order_id']
    else:
        order_id = None

    return order_id


def buy_market_order(session_key, name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity}


    try:
        response = requests.post(url + 'buy_now', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val




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

    session_key = 'bagel'

    nameA = 'Blake Johnson'
    nameB = 'Janice Hobbs'

    resourceA = 'apple'

    create_session(session_key)

    person_id = create_person(session_key=session_key, name=nameA, money=200.00, resource_dict={resourceA: 120})
    person_id = create_person(session_key=session_key, name=nameB, money=1500.00)


    order_id = sell_limit_order(session_key=session_key, name=nameA, resource_type=resourceA, quantity=8, price=2.50)
    b_success = buy_market_order(session_key=session_key, name=nameB, resource_type=resourceA, quantity=3)

    print(b_success)







if __name__ == '__main__':
    main()





















