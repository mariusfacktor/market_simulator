
import requests
import sqlite3


# Instructions: Delete database.db before running tests

# port = 5000
port = 8000

addr = 'http://127.0.0.1'
# addr = 'http://34.82.55.106'

url = addr + ':' + str(port) + '/'


nameA = 'Jean Rose'
nameB = 'Hank Tomford'

resources = ['apple', 'orange']

session_key = 'example'

cursor = None


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


def buy_order(name, resource_type, quantity, price):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity, 'price': price}

    response = requests.post(url + 'buy_order', json=data)
    print(response.json())


def cancel_sell_order(sell_id):

    data = {'session_key': session_key, 'sell_id': sell_id}

    response = requests.post(url + 'cancel_sell_order', json=data)
    print(response.json())


def cancel_buy_order(buy_id):

    data = {'session_key': session_key, 'buy_id': buy_id}

    response = requests.post(url + 'cancel_buy_order', json=data)
    print(response.json())


def buy_now(name, resource_type, quantity):

    data = {'session_key': session_key, 'name': name, 'resource_type': resource_type, 'quantity': quantity}

    response = requests.post(url + 'buy_now', json=data)
    print(response.json())


def deposit_or_withdraw(name, dollars, b_deposit=True):

    data = {'session_key': session_key, 'name': name, 'b_deposit': b_deposit, 'dollars': dollars}

    response = requests.post(url + 'deposit_or_withdraw', json=data)
    print(response.json())



def connect_to_db():

    global cursor

    # Connect to the database (or create it if it doesn't exist)
    conn = sqlite3.connect('database.db', check_same_thread=False)

    conn.row_factory = sqlite3.Row
    # Create a cursor object to execute SQL commands
    cursor = conn.cursor()



def test_A():

    create_session()
    create_person(nameA, 100, resource_dict={'apple': 10})
    create_person(nameB, 100, resource_dict={'orange': 10})
    sell_order(nameA, 'apple', 10, 5)
    sell_order(nameA, 'apple', 6, 3)

    buy_now(nameB, 'apple', 2)


def test_B():

    buy_order(nameA, 'orange', 5, 1.49)
    deposit_or_withdraw(nameA, 20)


def test_C():

    cancel_buy_order(1)


def test_D():

    create_session()
    create_person(nameA, 100, resource_dict={'apple': 50})
    create_person(nameB, 100, resource_dict={'orange': 30})
    sell_order(nameA, 'apple', 10, 5.00)
    sell_order(nameA, 'apple', 6, 3.30)
    sell_order(nameA, 'apple', 4, 2.50)

    buy_order(nameB, 'apple', 8, 4.4)




def check_A1():

    query = cursor.execute('''SELECT cash FROM person WHERE session_id = 1 AND name = "%s" ''' % nameA)
    cash = query.fetchall()[0][0]
    assert cash == 106, '%s must have $112' % nameA


    query = cursor.execute('''SELECT cash FROM person WHERE session_id = 1 AND name = "%s" ''' % nameB)
    cash = query.fetchall()[0][0]
    assert cash == 94, '%s must have $94' % nameB




def check_A2():

    query = cursor.execute('''SELECT quantity FROM person_resource 
                              WHERE session_id = 1 AND person_id = 1 AND resource_id = 1 ''')
    quantity = query.fetchall()[0][0]
    assert quantity == 8, '%s must have 8 apples' % nameA


    query = cursor.execute('''SELECT quantity FROM person_resource 
                              WHERE session_id = 1 AND person_id = 2 AND resource_id = 1 ''')
    quantity = query.fetchall()[0][0]
    assert quantity == 2, '%s must have 2 apples' % nameB


    query = cursor.execute('''SELECT quantity FROM person_resource 
                              WHERE session_id = 1 AND person_id = 2 AND resource_id = 2 ''')
    quantity = query.fetchall()[0][0]
    assert quantity == 10, '%s must have 10 oranges' % nameB




def check_A3():

    query = cursor.execute('''SELECT quantity FROM sell_order 
                              WHERE session_id = 1 AND person_id = 1 AND resource_id = 1 AND id = 1 ''')
    quantity = query.fetchall()[0][0]
    assert quantity == 10, '%s must be selling 10 apples' % nameA


    query = cursor.execute('''SELECT quantity_available FROM sell_order 
                              WHERE session_id = 1 AND person_id = 1 AND resource_id = 1 AND id = 1 ''')
    quantity_available = query.fetchall()[0][0]
    assert quantity_available == 4, '%s must have 4 apples available in this sell_order' % nameA


    query = cursor.execute('''SELECT quantity FROM sell_order 
                              WHERE session_id = 1 AND person_id = 1 AND resource_id = 1 AND id = 2''')
    quantity = query.fetchall()[0][0]
    assert quantity == 4, '%s must be selling 4 apples' % nameA


    query = cursor.execute('''SELECT quantity_available FROM sell_order 
                              WHERE session_id = 1 AND person_id = 1 AND resource_id = 1 AND id = 2 ''')
    quantity_available = query.fetchall()[0][0]
    assert quantity_available == 4, '%s must have 4 apples available in this sell_order' % nameA



def check_A4():

    query = cursor.execute('''SELECT quantity FROM sell_history 
                              WHERE session_id = 1 AND person_id = 1 AND resource_id = 1 AND sell_id = 2 ''')
    quantity = query.fetchall()[0][0]
    assert quantity == 2, '%s must have sold 2 apples' % nameA


    query = cursor.execute('''SELECT total_price FROM sell_history 
                              WHERE session_id = 1 AND person_id = 1 AND resource_id = 1 AND sell_id = 2 ''')
    total_price = query.fetchall()[0][0]
    assert total_price == 6, '%s must have been paid $6' % nameA



def check_A5():

    query = cursor.execute('''SELECT quantity FROM buy_history 
                              WHERE session_id = 1 AND person_id = 2 AND resource_id = 1 ''')
    quantity = query.fetchall()[0][0]
    assert quantity == 2, '%s must have bought 2 apples' % nameB


    query = cursor.execute('''SELECT total_price FROM buy_history 
                              WHERE session_id = 1 AND person_id = 2 AND resource_id = 1 ''')
    total_price = query.fetchall()[0][0]
    assert total_price == 6, '%s must have paid $6' % nameB




def main():


    connect_to_db()

    # test_A()
    # check_A1()
    # check_A2()
    # check_A3()
    # check_A4()
    # check_A5()

    # test_B()

    # test_C()

    test_D()






if __name__ == '__main__':
    main()





















