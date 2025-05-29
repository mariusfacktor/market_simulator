
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



def create_resource(session_key, resource_type):

    data = {'session_key': session_key, 'resource_type': resource_type}

    try:
        response = requests.post(url + 'new_resource', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        resource_id = response.json()['data']['resource_id']
    else:
        resource_id = None

    return resource_id




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



def get_ask_price(session_key, resource_type, quantity=1):
    # the lowest a seller is willing to accept

    params = {'session_key': session_key, 'resource_type': resource_type, 'quantity': quantity, 'b_sell_price': True}

    try:
        response = requests.get(url + 'get_price', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        price = response.json()['data']['price']
    else:
        price = None

    return price




def get_bid_price(session_key, resource_type, quantity=1):
    # the highest a buyer is willing to pay
    
    params = {'session_key': session_key, 'resource_type': resource_type, 'quantity': quantity, 'b_sell_price': False}

    try:
        response = requests.get(url + 'get_price', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        price = response.json()['data']['price']
    else:
        price = None

    return price




def deposit(session_key, name, money):

    data = {'session_key': session_key, 'name': name, 'dollars': money, 'b_deposit': True}


    try:
        response = requests.post(url + 'deposit_or_withdraw', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val


def withdraw(session_key, name, money):

    data = {'session_key': session_key, 'name': name, 'dollars': money, 'b_deposit': False}


    try:
        response = requests.post(url + 'deposit_or_withdraw', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def deliver_resource(session_key, name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity':quantity, 'b_deposit': True}


    try:
        response = requests.post(url + 'give_or_take_resource', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def receive_resource(session_key, name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity':quantity, 'b_deposit': False}


    try:
        response = requests.post(url + 'give_or_take_resource', json=data)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)


    b_success = response.json()['b_success']

    if b_success:
        return_val = b_success
    else:
        return_val = None

    return return_val



def get_assets(session_key, name):

    params = {'session_key': session_key, 'name': name}

    try:
        response = requests.get(url + 'get_assets', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        cash = response.json()['data']['cash']
        resource_list = response.json()['data']['resource_list']

        resource_dict = {x['type'] : x['quantity'] for x in resource_list}
    else:
        cash = None
        resource_dict = None

    return cash, resource_dict



def get_people(session_key):

    params = {'session_key': session_key}

    try:
        response = requests.get(url + 'get_people', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        person_list = response.json()['data']['people']
    else:
        person_list = None

    return person_list



def get_resources(session_key):

    params = {'session_key': session_key}

    try:
        response = requests.get(url + 'get_resources', params=params)
    except:
        raise RuntimeError('Cannot connect to server at address %s' %url)

    b_success = response.json()['b_success']

    if b_success:
        resource_list = response.json()['data']['resources']
    else:
        resource_list = None

    return resource_list



def main():

    session_key = 'bagel'

    nameA = 'Blake Johnson'
    nameB = 'Janice Hobbs'

    resourceA = 'apple'

    # session_key = create_session(session_key)

    # resource_id = create_resource(session_key, resourceA)

    # person_id = create_person(session_key=session_key, name=nameA, money=200.00, resource_dict={resourceA: 120})
    # person_id = create_person(session_key=session_key, name=nameB, money=1500.00)


    # order_id = sell_limit_order(session_key=session_key, name=nameA, resource_type=resourceA, quantity=8, price=2.50)
    # b_success = buy_market_order(session_key=session_key, name=nameB, resource_type=resourceA, quantity=3)

    # ask_price = get_ask_price(session_key=session_key, resource_type=resourceA, quantity=3)

    # bid_price = get_bid_price(session_key=session_key, resource_type=resourceA, quantity=1)


    # b_success = deposit(session_key=session_key, name=nameA, money=10.20)

    # b_success = withdraw(session_key=session_key, name=nameB, money=5.30)

    # b_success = deliver_resource(session_key=session_key, name=nameB, resource_type=resourceA, quantity=1)

    # b_success = receive_resource(session_key=session_key, name=nameA, resource_type=resourceA, quantity=3)

    # cash, resource_dict = get_assets(session_key=session_key, name=nameA)

    people_list = get_people(session_key=session_key)

    resource_list = get_resources(session_key=session_key)


if __name__ == '__main__':
    main()





















