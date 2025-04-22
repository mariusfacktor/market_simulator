
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, func
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


'''
SELECT SUM(cash) FROM person;
-- SELECT SUM(amount) FROM person_resource WHERE resource_id = 1;
-- SELECT SUM(amount) FROM sell WHERE resource_id = 1;
'''

'''
import sqlite3
# Connect to the database (or create it if it doesn't exist)
conn = sqlite3.connect('database.db', check_same_thread=False)

conn.row_factory = sqlite3.Row
# Create a cursor object to execute SQL commands
cursor = conn.cursor()
'''



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
Session_sqlalchemy = sessionmaker(bind=engine)
session = Session_sqlalchemy()




def get_market(session_id, resource_type):

    resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id


    # sort by price (low to high) and then by sell_id (low to high) when prices are equal
    query = (session.query(Person.name, Sell.id, Sell.person_id, Sell.amount, Sell.price).join(Person, Sell.person_id == Person.id)
                                       .filter(Person.session_id == session_id, Sell.resource_id == resource_id, Sell.amount > 0)
                                       .order_by(Sell.price, Sell.id)).all()

    sell_list = [dict(x._mapping) for x in query]

    return sell_list






def create_person(session_key, name, cash, resource_dict):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    b_success = False

    # Check if person already exists in person table
    if not session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():
        new_person = Person(session_id=session_id, name=name, cash=cash)
        session.add(new_person)
        session.commit()

        person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

        # Add new resources to resource table
        for resource_type, resource_amount in resource_dict.items():
            # Check if that resource type is already in the resource table
            if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
                # add type to resource table
                new_resource = Resource(session_id=session_id, type=resource_type)
                session.add(new_resource)
                session.commit()

            # Add resource amounts to person_resource table
            resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

            new_person_resource = PersonResource(session_id=session_id, person_id=person_id, resource_id=resource_id, amount=resource_amount)
            session.add(new_person_resource)
            session.commit()

        b_success = True
        message = 'Success (person): %s created' %name
    else:
        b_success = False
        message = 'Failure (person): %s already exists' % name

    return b_success, message


def give_or_take_product(session_id, person_id, resource_id, amount):
    # amount > 0: give
    # amount < 0: take

    if session.query(PersonResource).filter(PersonResource.session_id == session_id,
                                            PersonResource.person_id == person_id,
                                            PersonResource.resource_id == resource_id).all():

        previous_quantity = session.query(PersonResource).filter(PersonResource.session_id == session_id, 
                                                                 PersonResource.person_id == person_id, 
                                                                 PersonResource.resource_id == resource_id).one().amount
        new_quantity = previous_quantity + amount

        obj = session.query(PersonResource).filter(PersonResource.session_id == session_id, 
                                                   PersonResource.person_id == person_id,
                                                   PersonResource.resource_id == resource_id).one()
        obj.amount = new_quantity
        session.commit()

    else:

        previous_quantity = 0
        new_quantity = previous_quantity + amount
        new_person_resource = PersonResource(session_id=session_id, person_id=person_id, resource_id=resource_id, amount=new_quantity)
        session.add(new_person_resource)
        session.commit()


def pay_or_charge_person(session_id, person_id, dollars):
    # dollars > 0: pay
    # dollars < 0: charge

    # pay seller
    previous_cash = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one().cash
    new_cash = previous_cash + dollars

    obj = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one()
    obj.cash = new_cash
    session.commit()




def sell(session_key, name, resource_type, amount, price):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    b_success = False

    if session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():

        person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

        if session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():

            resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

            if session.query(PersonResource).filter(PersonResource.session_id == session_id,
                                                    PersonResource.person_id == person_id,
                                                    PersonResource.resource_id == resource_id).all():

                available_quantity = session.query(PersonResource).filter(PersonResource.session_id == session_id, 
                                                                          PersonResource.person_id == person_id, 
                                                                          PersonResource.resource_id == resource_id).one().amount

                if available_quantity >= amount:

                    new_sell_order = Sell(session_id=session_id, person_id=person_id, resource_id=resource_id, amount=amount, price=price)
                    session.add(new_sell_order)
                    session.commit()


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

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    b_success = False
    price = None

    if session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():

        resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

        # Get the number of items currently for sale for that resource
        num_product = (session.query(func.coalesce(func.sum(Sell.amount), 0))
                              .filter(Sell.session_id == session_id, Sell.resource_id == resource_id)).one()[0]

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

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    b_success = False

    if session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():

        person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

        if session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():

            resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

            # Get the number of items currently for sale for that resource
            num_product = (session.query(func.coalesce(func.sum(Sell.amount), 0))
                                  .filter(Sell.session_id == session_id, Sell.resource_id == resource_id)).one()[0]

            if amount <= num_product:

                price = get_price(session_id, resource_type, amount)
                buyer_cash = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one().cash

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

                        obj = session.query(Sell).filter(Sell.session_id == session_id, Sell.id == curr_sale_id).one()
                        obj.amount = updated_quantity
                        session.commit()

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

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    cash = None
    resource_list = None

    if session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():

        cash = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().cash


        person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id



        # Get resources from person name and sort by resource type
        query = (session.query(Resource.type, PersonResource.amount).join(Resource, PersonResource.resource_id == Resource.id)
                        .filter(PersonResource.session_id == session_id, PersonResource.person_id == person_id)
                        .order_by(Resource.type)).all()

        resource_list = [dict(x._mapping) for x in query]



        b_success = True
        message = 'Success (assets): got assets for %s' % name

    else:

        b_success = False
        message = 'Failure (assets): %s does not exist' % name

    return b_success, message, cash, resource_list



def get_market_toplevel(session_key, resource_type):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    sell_list = None

    if session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        sell_list = get_market(session_id, resource_type)

        b_success = True
        message = 'Success (market): returned selling data for %s' % resource_type
    else:
        b_success = False
        message = 'Failure (market): resource type %s does not exist' % resource_type

    return b_success, message, sell_list



def get_people(session_key):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    query = session.query(Person.name).filter(Person.session_id == session_id).all()
    person_list = [x._mapping['name'] for x in query]
    
    b_success = True
    message = 'Success (people): got %d people' % len(person_list)

    return b_success, message, person_list


def get_resources(session_key):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    query = session.query(Resource.type).filter(Resource.session_id == session_id).all()
    resource_list = [x._mapping['type'] for x in query]
    
    b_success = True
    message = 'Success (resource): got %d resources' % len(resource_list)

    return b_success, message, resource_list



def cancel_sell(session_key, sell_id):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id
    resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id
    amount = session.query(Sell).filter(Sell.session_id == session_id, Sell.id == sell_id).one().amount

    # Give product back to the seller
    give_or_take_product(session_id, person_id, resource_id, amount)

    # Set amount to zero in sale row
    obj = session.query(Sell).filter(Sell.session_id == session_id, Sell.id == sell_id).one()
    obj.amount = 0
    session.commit()

    b_success = True
    message = 'SUCCESS (cancel): sale %d canceled' % sell_id

    return b_success, message


def deposit_or_withdraw(session_key, name, option, dollars):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id
    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

    if option == 'withdraw':

        buyer_cash = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one().cash

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

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id
    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id
    resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

    if option == 'withdraw':

        resource_amount = session.query(PersonResource).filter(PersonResource.session_id == session_id, 
                                                               PersonResource.person_id == person_id, 
                                                               PersonResource.resource_id == resource_id).one().amount

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

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        new_resource = Resource(session_id=session_id, type=resource_type)
        session.add(new_resource)
        session.commit()

        b_success = True
        message = 'Success (new_resource): %s added to resource table' %resource_type

    else:
        b_success = False
        message = 'Failure (new_resource): %s already exists in resource table' %resource_type

    return b_success, message



def create_session(session_key):

    if not session.query(Session).filter(Session.session_key == session_key).all():
        new_session = Session(session_key=session_key)
        session.add(new_session)
        session.commit()

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


def create_app():
    return app


def main():
    app.run(port=5000, debug=True)



if __name__ == '__main__':
    main()



