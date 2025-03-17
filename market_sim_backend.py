
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from collections import namedtuple
from functools import partial

'''
SELECT SUM(cash) FROM person;
-- SELECT SUM(amount) FROM person_resource WHERE resource_id = 1;
-- SELECT SUM(amount) FROM sell WHERE resource_id = 1;
'''

# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db', check_same_thread=False)

conn.row_factory = sqlite3.Row
# Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Define the SQL command to create the table
create_person_table_sql = '''
    CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    cash INTEGER
);
'''

create_resource_table_sql = '''
    CREATE TABLE IF NOT EXISTS resource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL
);
'''

create_person_resource_table_sql = '''
    CREATE TABLE IF NOT EXISTS person_resource (
    person_id INTEGER,
    resource_id INTEGER,
    amount INTEGER
);
'''

create_sell_table_sql = '''
    CREATE TABLE IF NOT EXISTS sell (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    person_id INTEGER,
    resource_id INTEGER,
    amount INTEGER,
    price INTEGER
);
'''

# Execute the SQL command
cursor.execute(create_person_table_sql)
cursor.execute(create_resource_table_sql)
cursor.execute(create_person_resource_table_sql)
cursor.execute(create_sell_table_sql)



# Commit the changes
conn.commit()

# Close the connection
# conn.close()



def where_str(column_list, value_list):
    num_criteria = len(column_list)
    criteria_str = ''
    for i in range(num_criteria):
        if isinstance(value_list[i], str):
            criteria_str += '%s = "%s"' %(column_list[i], value_list[i])
        else:
            criteria_str += '%s = %d' %(column_list[i], value_list[i])
        if i < num_criteria - 1:
            criteria_str += ' and '

    return criteria_str


def db_exists(table, column_list, value_list):

    criteria_str = where_str(column_list, value_list)

    command = 'SELECT EXISTS(SELECT 1 FROM %s WHERE %s);' %(table, criteria_str)
    cursor.execute(command)
    if cursor.fetchone()[0]:
        return True
    else:
        return False


def db_add_row(table, column_list, value_list):
    value_list = tuple(value_list)

    columns_str = '('
    question_mark_str = '('
    num_columns = len(column_list)
    for i in range(num_columns):
        columns_str += column_list[i]
        question_mark_str += '?'
        if i < num_columns - 1:
            columns_str += ', '
            question_mark_str += ', '
    columns_str += ')'
    question_mark_str += ')'

    command = 'INSERT INTO %s %s VALUES %s' %(table, columns_str, question_mark_str)
    cursor.execute(command, value_list)

    conn.commit()


def db_get(table, col_name, column_list, value_list):

    criteria_str = where_str(column_list, value_list)

    command = 'SELECT %s FROM %s WHERE %s;' %(col_name, table, criteria_str)

    cursor.execute(command)
    ret_id = cursor.fetchone()[0]
    return ret_id

def db_update(table, col_name, value, column_list, value_list):

    criteria_str = where_str(column_list, value_list)

    if isinstance(value, str):
        command = 'UPDATE %s SET %s = "%s" WHERE %s;' %(table, col_name, value, criteria_str)
    else:
        command = 'UPDATE %s SET %s = %d WHERE %s;' %(table, col_name, value, criteria_str)

    cursor.execute(command)

    conn.commit()





def get_market(resource_type):

    resource_id = db_get('resource', 'id', column_list=['type'], value_list=[resource_type])

    # sort by price (low to high) and then by sell_id (low to high) when prices are equal
    command = '''SELECT name, sell.id, person_id, amount, price FROM sell
                INNER JOIN person ON sell.person_id = person.id
                WHERE resource_id = %d and amount > 0 ORDER BY price, sell.id''' % resource_id

    cursor.execute(command)
    sell_table = cursor.fetchall()

    return sell_table


def get_num_products_for_sale(resource_type):

    resource_id = db_get('resource', 'id', column_list=['type'], value_list=[resource_type])

    command = 'SELECT SUM(amount) FROM sell WHERE resource_id = %d' % resource_id
    cursor.execute(command)
    num_products = cursor.fetchall()
    num_products = num_products[0][0]

    if num_products is None:
        num_products = 0

    return num_products

    





def create_person(name, cash, resource_dict):

    b_success = False

    # Check if person already exists in person table
    if not db_exists('person', column_list=['name'], value_list=[name]):
        db_add_row('person', column_list=['name', 'cash'], value_list=[name, cash])

        person_id = db_get('person', 'id', column_list=['name'], value_list=[name])

        # Add new resources to resource table
        for resource_type, resource_amount in resource_dict.items():
            # Check if that resource type is already in the resource table
            if not db_exists('resource', column_list=['type'], value_list=[resource_type]):
                # add type to resource table
                db_add_row('resource', column_list=['type'], value_list=[resource_type])

            # Add resource amounts to person_resource table
            resource_id = db_get('resource', 'id', column_list=['type'], value_list=[resource_type])
            db_add_row('person_resource', column_list=['person_id', 'resource_id', 'amount'], value_list=[person_id, resource_id, resource_amount])

        b_success = True
        message = 'Success (person): %s created' %name
    else:
        b_success = False
        message = 'Failure (person): %s already exists' % name

    return b_success, message


def give_or_take_product(person_id, resource_id, amount):
    # amount > 0: give
    # amount < 0: take

    if db_exists('person_resource', column_list=['person_id', 'resource_id'], value_list=[person_id, resource_id]):

        previous_quantity = db_get('person_resource', 'amount', column_list=['person_id', 'resource_id'], value_list=[person_id, resource_id])
        new_quantity = previous_quantity + amount
        db_update('person_resource', 'amount', new_quantity, column_list=['person_id', 'resource_id'], value_list=[person_id, resource_id])

    else:

        previous_quantity = 0
        new_quantity = previous_quantity + amount
        db_add_row('person_resource', column_list=['person_id', 'resource_id', 'amount'], value_list=[person_id, resource_id, new_quantity])


def pay_or_charge_person(person_id, dollars):
    # dollars > 0: pay
    # dollars < 0: charge

    # pay seller
    previous_cash = db_get('person', 'cash', column_list=['id'], value_list=[person_id])
    new_cash = previous_cash + dollars
    db_update('person', 'cash', new_cash, column_list=['id'], value_list=[person_id])



def sell(name, resource_type, amount, price):

    b_success = False

    person_id = db_get('person', 'id', column_list=['name'], value_list=[name])

    if db_exists('resource', column_list=['type'], value_list=[resource_type]):

        resource_id = db_get('resource', 'id', column_list=['type'], value_list=[resource_type])

        if db_exists('person_resource', column_list=['person_id', 'resource_id'], value_list=[person_id, resource_id]):

            available_quantity = db_get('person_resource', 'amount', column_list=['person_id', 'resource_id'], 
                                            value_list=[person_id, resource_id])

            if available_quantity >= amount:

                db_add_row('sell', column_list=['person_id', 'resource_id', 'amount', 'price'], 
                            value_list=[person_id, resource_id, amount, price])


                # Take product from the seller
                give_or_take_product(person_id, resource_id, -1 * amount)

                b_success = True
                message = 'Success (sale): %s sells %d %s for price %d' % (name, amount, resource_type, price)
            else:
                b_success = False
                message = 'Failure (sale): not enough %s' % resource_type
        else:
            b_success = False
            message = 'Failure (sale): %s has no %s' % (name, resource_type)
    else:
        b_success = False
        message = 'Failure (sale): resource %s does not exist' % resource_type


    return b_success, message


def get_price(resource_type, amount):

    market = get_market(resource_type)

    running_quantity = 0
    running_cost = 0

    market_idx = 0
    while running_quantity < amount:

        curr_quantity = market[market_idx]['amount']
        curr_price = market[market_idx]['price']

        if curr_quantity + running_quantity <= amount:
            running_quantity += curr_quantity
            running_cost += curr_price * curr_quantity
        else:
            quantity = amount - running_quantity
            running_quantity += quantity
            running_cost += curr_price * quantity

        market_idx += 1


    price = running_cost

    return price



def get_price_toplevel(resource_type, amount=1):

    b_success = False
    price = None

    if db_exists('resource', column_list=['type'], value_list=[resource_type]):

        num_product = get_num_products_for_sale(resource_type)

        if amount <= num_product:

            price = get_price(resource_type, amount)

            b_success = True
            message = 'Success (price): price for %s is %d' % (resource_type, price)

        else:
            b_success = False
            message = 'Failure (price): not enough %s for sale' % resource_type

    else:
        b_success = False
        message = 'Failure (price): resource type %s does not exist' % resource_type

    return b_success, message, price


def buy(name, resource_type, amount):

    b_success = False

    if db_exists('person', column_list=['name'], value_list=[name]):

        person_id = db_get('person', 'id', column_list=['name'], value_list=[name])

        if db_exists('resource', column_list=['type'], value_list=[resource_type]):

            resource_id = db_get('resource', 'id', column_list=['type'], value_list=[resource_type])

            num_product = get_num_products_for_sale(resource_type)
            if amount <= num_product:

                # _, _, price = get_price(resource_type, amount)
                price = get_price(resource_type, amount)
                buyer_cash = db_get('person', 'cash', column_list=['id'], value_list=[person_id])

                if buyer_cash >= price:


                    market = get_market(resource_type)

                    running_quantity = 0
                    running_cost = 0

                    sell_idx = 0
                    while running_quantity < amount:

                        curr_quantity = market[sell_idx]['amount']
                        curr_price = market[sell_idx]['price']
                        curr_seller = market[sell_idx]['person_id']
                        curr_sale_id = market[sell_idx]['id']

                        if curr_quantity + running_quantity <= amount:
                            used_quantity = curr_quantity
                            cost = curr_price * used_quantity
                            running_quantity += used_quantity
                            running_cost += cost
                        else:
                            used_quantity = amount - running_quantity
                            cost = curr_price * used_quantity
                            running_quantity += used_quantity
                            running_cost += cost

                        # buy from curr_seller
                        # subtract quantity bought from seller
                        updated_quantity = curr_quantity - used_quantity
                        db_update('sell', 'amount', updated_quantity, column_list=['id'], value_list=[curr_sale_id])

                        # pay seller
                        pay_or_charge_person(curr_seller, cost)

                        sell_idx += 1

                    # charge buyer
                    pay_or_charge_person(person_id, -1 * running_cost)

                    # give items to the buyer
                    give_or_take_product(person_id, resource_id, running_quantity)


                    b_success = True
                    message = 'Success (buy): %s buys %d %s for cost %d' % (name, amount, resource_type, running_cost)

                else:
                    b_success = False
                    message = 'Failure (buy): buyer %s cannot afford the cost %d for %s' % (name, price, resource_type)

            else:
                b_success = False
                message = 'Failure (buy): not enough %s for sale' % resource_type

        else:
            b_success = False
            message = 'Failure (buy): resource %s does not exist' % resource_type

    else:
        b_success = False
        message = 'Failure (buy): person %s does not exist' % name

    return b_success, message


def get_assets(name):

    cash = None
    resource_dict = None

    if db_exists('person', column_list=['name'], value_list=[name]):

        cash = db_get('person', 'cash', column_list=['name'], value_list=[name])


        person_id = db_get('person', 'id', column_list=['name'], value_list=[name])

        command = '''SELECT type, resource_id, amount FROM person_resource 
                        INNER JOIN resource ON person_resource.resource_id = resource.id WHERE person_id = %d''' % person_id

        cursor.execute(command)
        resource_arr = cursor.fetchall()

        resource_dict = {x['type']: x['amount'] for x in resource_arr}


        b_success = True
        message = 'Success (assets): got assets for %s' % name

    else:

        b_success = False
        message = 'Failure (assets): %s does not exist' % name

    return b_success, message, cash, resource_dict



def get_market_toplevel(resource_type):

    sell_dict = None

    if db_exists('resource', column_list=['type'], value_list=[resource_type]):
        sell_table = get_market(resource_type)
        sell_dict = {i: {'name': x['name'], 'amount': x['amount'], 'price': x['price']} for i, x in enumerate(sell_table)}


        b_success = True
        message = 'Success (market): returned selling data for %s' % resource_type
    else:
        b_success = False
        message = 'Failure (market): resource type %s does not exist' % resource_type

    return b_success, message, sell_dict





# TODO: allow person to cancel sell order

app = Flask(__name__)
CORS(app)


@app.route('/create_person', methods=['POST'])
def api_create_person():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        name = data['name']
        cash = data['cash']
        resource_dict = data['resource_dict']

        b_success, message = create_person(name, cash, resource_dict)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405



@app.route('/sell', methods=['POST'])
def api_sell():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        name = data['name']
        resource_type = data['resource_type']
        amount = data['amount']
        price = data['price']

        b_success, message = sell(name, resource_type, amount, price)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405



@app.route('/buy', methods=['POST'])
def api_buy():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        name = data['name']
        resource_type = data['resource_type']
        amount = data['amount']

        b_success, message = buy(name, resource_type, amount)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/get_price', methods=['GET'])
def api_get_price():
    if request.method == 'GET':

        amount = 1

        resource_type = request.args.get('resource_type')
        if 'amount' in request.args:
            amount = int(request.args.get('amount'))

        b_success, message, price = get_price_toplevel(resource_type, amount)

        return_data = {
                        'resource_type': resource_type,
                        'price': price
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/get_assets', methods=['GET'])
def api_get_assets():
    if request.method == 'GET':

        name = request.args.get('name')

        b_success, message, cash, resource_dict = get_assets(name)


        return_data = {
                        'name': name,
                        'cash': cash,
                        'resource_dict': resource_dict
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405




@app.route('/get_market', methods=['GET'])
def api_get_market():
    if request.method == 'GET':

        resource_type = request.args.get('resource_type')

        b_success, message, sell_dict = get_market_toplevel(resource_type)

        return_data = {
                        'resource_type': resource_type,
                        'sell_dict': sell_dict
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405





def main():
    app.run(port=5000, debug=True)



if __name__ == '__main__':
    main()



