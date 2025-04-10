
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


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



Base = declarative_base()


class Session(Base):
    __tablename__ = 'session'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_key = Column(String)



class Person(Base):
    __tablename__ = 'person'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    name = Column(String)
    cash = Column(Float)


class Resource(Base):
    __tablename__ = 'resource'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    type = Column(String)


class PersonResource(Base):
    __tablename__ = 'person_resource'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    resource_id = Column(Integer, ForeignKey('resource.id'))
    amount = Column(Integer)

class Sell(Base):
    __tablename__ = 'sell'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    resource_id = Column(Integer, ForeignKey('resource.id'))
    amount = Column(Integer)
    price = Column(Float)




# Set up the database
engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)

# Create a session
Session = sessionmaker(bind=engine)
session = Session()


# Add user and profile
# user = User(name='Alice')
# user.profile = UserProfile(bio='Hello, I love SQLAlchemy!')

# session.add(user)
# session.commit()





"""
# Define the SQL command to create the table
create_person_table_sql = '''
    CREATE TABLE IF NOT EXISTS person (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    name TEXT NOT NULL,
    cash REAL
);
'''

create_resource_table_sql = '''
    CREATE TABLE IF NOT EXISTS resource (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    type TEXT NOT NULL
);
'''

create_person_resource_table_sql = '''
    CREATE TABLE IF NOT EXISTS person_resource (
    session_id INTEGER,
    person_id INTEGER,
    resource_id INTEGER,
    amount INTEGER
);
'''

create_sell_table_sql = '''
    CREATE TABLE IF NOT EXISTS sell (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER,
    person_id INTEGER,
    resource_id INTEGER,
    amount INTEGER,
    price REAL
);
'''


create_session_table_sql = '''
    CREATE TABLE IF NOT EXISTS session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_key TEXT NOT NULL
);
'''


# Execute the SQL command
cursor.execute(create_person_table_sql)
cursor.execute(create_resource_table_sql)
cursor.execute(create_person_resource_table_sql)
cursor.execute(create_sell_table_sql)
cursor.execute(create_session_table_sql)



# Commit the changes
conn.commit()
"""

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
        command = 'UPDATE %s SET %s = %f WHERE %s;' %(table, col_name, value, criteria_str)

    cursor.execute(command)

    conn.commit()





def get_market(session_id, resource_type):

    resource_id = db_get('resource', 'id', column_list=['session_id', 'type'], value_list=[session_id, resource_type])

    # sort by price (low to high) and then by sell_id (low to high) when prices are equal
    command = '''SELECT name, sell.id, person_id, amount, price FROM sell
                INNER JOIN person ON sell.person_id = person.id
                WHERE person.session_id = %d AND resource_id = %d AND amount > 0 ORDER BY price, sell.id''' % (session_id, resource_id)

    cursor.execute(command)
    sell_table = cursor.fetchall()

    return sell_table


def get_num_products_for_sale(session_id, resource_type):

    resource_id = db_get('resource', 'id', column_list=['session_id', 'type'], value_list=[session_id, resource_type])

    command = 'SELECT SUM(amount) FROM sell WHERE session_id = %d AND resource_id = %d' % (session_id, resource_id)
    cursor.execute(command)
    num_products = cursor.fetchall()
    num_products = num_products[0][0]

    if num_products is None:
        num_products = 0

    return num_products

    





def create_person(session_key, name, cash, resource_dict):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    b_success = False

    # Check if person already exists in person table
    if not db_exists('person', column_list=['session_id', 'name'], value_list=[session_id, name]):
        db_add_row('person', column_list=['session_id', 'name', 'cash'], value_list=[session_id, name, cash])

        person_id = db_get('person', 'id', column_list=['session_id', 'name'], value_list=[session_id, name])

        # Add new resources to resource table
        for resource_type, resource_amount in resource_dict.items():
            # Check if that resource type is already in the resource table
            if not db_exists('resource', column_list=['session_id', 'type'], value_list=[session_id, resource_type]):
                # add type to resource table
                db_add_row('resource', column_list=['session_id', 'type'], value_list=[session_id, resource_type])

            # Add resource amounts to person_resource table
            resource_id = db_get('resource', 'id', column_list=['session_id', 'type'], value_list=[session_id, resource_type])
            db_add_row('person_resource', column_list=['session_id', 'person_id', 'resource_id', 'amount'], value_list=[session_id, person_id, resource_id, resource_amount])

        b_success = True
        message = 'Success (person): %s created' %name
    else:
        b_success = False
        message = 'Failure (person): %s already exists' % name

    return b_success, message


def give_or_take_product(session_id, person_id, resource_id, amount):
    # amount > 0: give
    # amount < 0: take

    if db_exists('person_resource', column_list=['session_id', 'person_id', 'resource_id'], value_list=[session_id, person_id, resource_id]):

        previous_quantity = db_get('person_resource', 'amount', column_list=['session_id', 'person_id', 'resource_id'], value_list=[session_id, person_id, resource_id])
        new_quantity = previous_quantity + amount
        db_update('person_resource', 'amount', new_quantity, column_list=['session_id', 'person_id', 'resource_id'], value_list=[session_id, person_id, resource_id])

    else:

        previous_quantity = 0
        new_quantity = previous_quantity + amount
        db_add_row('person_resource', column_list=['session_id', 'person_id', 'resource_id', 'amount'], value_list=[session_id, person_id, resource_id, new_quantity])


def pay_or_charge_person(session_id, person_id, dollars):
    # dollars > 0: pay
    # dollars < 0: charge

    # pay seller
    previous_cash = db_get('person', 'cash', column_list=['session_id', 'id'], value_list=[session_id, person_id])
    new_cash = previous_cash + dollars
    db_update('person', 'cash', new_cash, column_list=['session_id', 'id'], value_list=[session_id, person_id])



def sell(session_key, name, resource_type, amount, price):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    b_success = False

    if db_exists('person', column_list=['session_id', 'name'], value_list=[session_id, name]):

        person_id = db_get('person', 'id', column_list=['session_id', 'name'], value_list=[session_id, name])

        if db_exists('resource', column_list=['session_id', 'type'], value_list=[session_id, resource_type]):

            resource_id = db_get('resource', 'id', column_list=['session_id', 'type'], value_list=[session_id, resource_type])

            if db_exists('person_resource', column_list=['session_id', 'person_id', 'resource_id'], value_list=[session_id, person_id, resource_id]):

                available_quantity = db_get('person_resource', 'amount', column_list=['session_id', 'person_id', 'resource_id'], 
                                                value_list=[session_id, person_id, resource_id])

                if available_quantity >= amount:

                    db_add_row('sell', column_list=['session_id', 'person_id', 'resource_id', 'amount', 'price'], 
                                value_list=[session_id, person_id, resource_id, amount, price])


                    # Take product from the seller
                    give_or_take_product(session_id, person_id, resource_id, -1 * amount)

                    b_success = True
                    message = 'Success (sale): %s sells %d %s for price %.2f' % (name, amount, resource_type, price)
                else:
                    b_success = False
                    message = 'Failure (sale): not enough %s' % resource_type
            else:
                b_success = False
                message = 'Failure (sale): %s has no %s' % (name, resource_type)
        else:
            b_success = False
            message = 'Failure (sale): resource %s does not exist' % resource_type

    else:
        b_success = False
        message = 'Failure (sale): %s does not exist' % name


    return b_success, message


def get_price(session_id, resource_type, amount):

    market = get_market(session_id, resource_type)

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



def get_price_toplevel(session_key, resource_type, amount=1):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    b_success = False
    price = None

    if db_exists('resource', column_list=['session_id', 'type'], value_list=[session_id, resource_type]):

        num_product = get_num_products_for_sale(session_id, resource_type)

        if amount <= num_product:

            price = get_price(session_id, resource_type, amount)

            b_success = True
            message = 'Success (price): price for %d %s is %.2f' % (amount, resource_type, price)

        else:
            b_success = False
            message = 'Failure (price): not enough %s for sale' % resource_type

    else:
        b_success = False
        message = 'Failure (price): resource type %s does not exist' % resource_type

    return b_success, message, price


def buy(session_key, name, resource_type, amount):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    b_success = False

    if db_exists('person', column_list=['session_id', 'name'], value_list=[session_id, name]):

        person_id = db_get('person', 'id', column_list=['session_id', 'name'], value_list=[session_id, name])

        if db_exists('resource', column_list=['session_id', 'type'], value_list=[session_id, resource_type]):

            resource_id = db_get('resource', 'id', column_list=['session_id', 'type'], value_list=[session_id, resource_type])

            num_product = get_num_products_for_sale(session_id, resource_type)
            if amount <= num_product:

                price = get_price(session_id, resource_type, amount)
                buyer_cash = db_get('person', 'cash', column_list=['session_id', 'id'], value_list=[session_id, person_id])

                if buyer_cash >= price:


                    market = get_market(session_id, resource_type)

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
                        db_update('sell', 'amount', updated_quantity, column_list=['session_id', 'id'], value_list=[session_id, curr_sale_id])

                        # pay seller
                        pay_or_charge_person(session_id, curr_seller, cost)

                        sell_idx += 1

                    # charge buyer
                    pay_or_charge_person(session_id, person_id, -1 * running_cost)

                    # give items to the buyer
                    give_or_take_product(session_id, person_id, resource_id, running_quantity)


                    b_success = True
                    message = 'Success (buy): %s buys %d %s for cost %.2f' % (name, amount, resource_type, running_cost)

                else:
                    b_success = False
                    message = 'Failure (buy): buyer %s cannot afford the cost %.2f for %s' % (name, price, resource_type)

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


def get_assets(session_key, name):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    cash = None
    resource_list = None

    if db_exists('person', column_list=['session_id', 'name'], value_list=[session_id, name]):

        cash = db_get('person', 'cash', column_list=['session_id', 'name'], value_list=[session_id, name])


        person_id = db_get('person', 'id', column_list=['session_id', 'name'], value_list=[session_id, name])

        command = '''SELECT type, resource_id, amount FROM person_resource 
                        INNER JOIN resource ON person_resource.resource_id = resource.id 
                        WHERE resource.session_id = %d AND person_id = %d ORDER BY resource.type''' % (session_id, person_id)

        cursor.execute(command)
        resource_arr = cursor.fetchall()

        resource_list = [{'resource': x['type'], 'quantity': x['amount']} for x in resource_arr]


        b_success = True
        message = 'Success (assets): got assets for %s' % name

    else:

        b_success = False
        message = 'Failure (assets): %s does not exist' % name

    return b_success, message, cash, resource_list



def get_market_toplevel(session_key, resource_type):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    sell_list = None

    if db_exists('resource', column_list=['session_id', 'type'], value_list=[session_id, resource_type]):
        sell_table = get_market(session_id, resource_type)
        sell_list = [{'sell_id': x['id'], 'name': x['name'], 'amount': x['amount'], 'price': x['price']} for i, x in enumerate(sell_table)]



        b_success = True
        message = 'Success (market): returned selling data for %s' % resource_type
    else:
        b_success = False
        message = 'Failure (market): resource type %s does not exist' % resource_type

    return b_success, message, sell_list



def get_people(session_key):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    command = '''SELECT name FROM person WHERE session_id = %d''' % session_id
    cursor.execute(command)
    person_rows = cursor.fetchall()

    person_list = [x['name'] for x in person_rows]
    
    b_success = True
    message = 'Success (people): got %d people' % len(person_list)

    return b_success, message, person_list


def get_resources(session_key):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    command = '''SELECT type FROM resource WHERE session_id = %d''' % session_id
    cursor.execute(command)
    resource_rows = cursor.fetchall()

    resource_list = [x['type'] for x in resource_rows]
    
    b_success = True
    message = 'Success (resource): got %d resources' % len(resource_list)

    return b_success, message, resource_list



def cancel_sell(session_key, sell_id):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    person_id = db_get('sell', 'person_id', column_list=['session_id', 'id'], value_list=[session_id, sell_id])
    resource_id = db_get('sell', 'resource_id', column_list=['session_id', 'id'], value_list=[session_id, sell_id])
    amount = db_get('sell', 'amount', column_list=['session_id', 'id'], value_list=[session_id, sell_id])

    # Give product back to the seller
    give_or_take_product(session_id, person_id, resource_id, amount)

    # Set amount to zero in sale row
    db_update('sell', 'amount', 0, column_list=['session_id', 'id'], value_list=[session_id, sell_id])

    b_success = True
    message = 'SUCCESS (cancel): sale %d canceled' % sell_id

    return b_success, message


def deposit_or_withdraw(session_key, name, option, dollars):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])
    person_id = db_get('person', 'id', column_list=['session_id', 'name'], value_list=[session_id, name])

    if option == 'withdraw':

        buyer_cash = db_get('person', 'cash', column_list=['session_id', 'id'], value_list=[session_id, person_id])

        if buyer_cash < dollars:
            b_success = False
            message = 'Failure (deposit): %s has not enough cash to withdraw %.2f' %(name, dollars)
            return b_success, message

        dollars = -1 * dollars

    pay_or_charge_person(session_id, person_id, dollars)

    b_success = True
    message = 'Success (deposit): %s %.2f with account %s' %(option, dollars, name)

    return b_success, message



def give_or_take_resource(session_key, name, resource_type, option, amount):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])
    person_id = db_get('person', 'id', column_list=['session_id', 'name'], value_list=[session_id, name])
    resource_id = db_get('resource', 'id', column_list=['session_id', 'type'], value_list=[session_id, resource_type])

    if option == 'withdraw':

        resource_amount = db_get('person_resource', 'amount', column_list=['session_id', 'person_id', 'resource_id'], value_list=[session_id, person_id, resource_id])

        if resource_amount < amount:
            b_success = False
            message = 'Failure (give): %s has not enough %s to withdraw %d' %(name, resource_type, amount)
            return b_success, message

        amount = -1 * amount

    give_or_take_product(session_id, person_id, resource_id, amount)

    b_success = True
    message = 'Success (give): %s %d %s with account %s' %(option, amount, resource_type, name)

    return b_success, message


def new_resource(session_key, resource_type):

    session_id = db_get('session', 'id', column_list=['session_key'], value_list=[session_key])

    if not db_exists('resource', column_list=['session_id', 'type'], value_list=[session_id, resource_type]):
        db_add_row('resource', column_list=['session_id', 'type'], value_list=[session_id, resource_type])

        b_success = True
        message = 'Success (new_resource): %s added to resource table' %resource_type

    else:
        b_success = False
        message = 'Failure (new_resource): %s already exists in resource table' %resource_type

    return b_success, message



def create_session(session_key):

    if not db_exists('session', column_list=['session_key'], value_list=[session_key]):
        db_add_row('session', column_list=['session_key'], value_list=[session_key])

        b_success = True
        message = 'Success (session): session key %s created' %session_key

    else:
        b_success = True
        message = 'Success (session): session key %s already exists' %session_key

    return b_success, message





app = Flask(__name__)
CORS(app)


@app.route('/create_person', methods=['POST'])
def api_create_person():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        name = data['name']
        cash = data['cash']
        resource_dict = data['resource_dict']

        b_success, message = create_person(session_key, name, cash, resource_dict)

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

        session_key = data['session_key']
        name = data['name']
        resource_type = data['resource_type']
        amount = data['amount']
        price = data['price']

        b_success, message = sell(session_key, name, resource_type, amount, price)

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

        session_key = data['session_key']
        name = data['name']
        resource_type = data['resource_type']
        amount = data['amount']

        b_success, message = buy(session_key, name, resource_type, amount)

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

        session_key = request.args.get('session_key')
        resource_type = request.args.get('resource_type')
        if 'amount' in request.args:
            amount = int(request.args.get('amount'))

        b_success, message, price = get_price_toplevel(session_key, resource_type, amount)

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

        session_key = request.args.get('session_key')
        name = request.args.get('name')

        b_success, message, cash, resource_list = get_assets(session_key, name)


        return_data = {
                        'name': name,
                        'cash': cash,
                        'resource_list': resource_list
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405




@app.route('/get_market', methods=['GET'])
def api_get_market():
    if request.method == 'GET':

        session_key = request.args.get('session_key')
        resource_type = request.args.get('resource_type')

        b_success, message, sell_list = get_market_toplevel(session_key, resource_type)

        return_data = {
                        'resource_type': resource_type,
                        'sell_list': sell_list
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/get_people', methods=['GET'])
def api_get_people():
    if request.method == 'GET':

        session_key = request.args.get('session_key')

        b_success, message, person_list = get_people(session_key)
        
        return_data = {
                        'people': person_list
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/get_resources', methods=['GET'])
def api_get_resources():
    if request.method == 'GET':

        session_key = request.args.get('session_key')

        b_success, message, resource_list = get_resources(session_key)
        
        return_data = {
                        'resources': resource_list
                        }


        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/cancel_sell', methods=['POST'])
def api_cancel_sale():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        sell_id = data['sell_id']


        b_success, message = cancel_sell(session_key, sell_id)


        return_data = {
                        'sell_id': sell_id
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/deposit_or_withdraw', methods=['POST'])
def api_deposit_or_withdraw():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        name = data['name']
        option = data['option']
        dollars = data['dollars']

        b_success, message = deposit_or_withdraw(session_key, name, option, dollars)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/give_or_take_resource', methods=['POST'])
def api_give_or_take_resource():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        name = data['name']
        resource_type = data['resource_type']
        option = data['option']
        amount = data['amount']

        b_success, message = give_or_take_resource(session_key, name, resource_type, option, amount)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/new_resource', methods=['POST'])
def api_new_resource():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        resource_type = data['resource_type']

        b_success, message = new_resource(session_key, resource_type)

        return_data = {
                        'resource_type': resource_type
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/create_session', methods=['POST'])
def api_create_session():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']

        b_success, message = create_session(session_key)

        return_data = {
                        'session_key': session_key
                        }

        response = {'message': message, 'data': return_data}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405



def main():
    app.run(port=5000, debug=True)



if __name__ == '__main__':
    main()



