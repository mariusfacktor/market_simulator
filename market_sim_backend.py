
import random
import string
from flask import Flask, request, jsonify
from flask_cors import CORS
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, func, desc
from sqlalchemy.dialects.mysql import DATETIME
from sqlalchemy.orm import relationship, sessionmaker, declarative_base
from sqlalchemy_utc import utcnow


# gunicorn --bind 0.0.0.0:8000 -w 2 "market_sim_backend:app"


'''
SELECT SUM(cash) FROM person;
-- SELECT SUM(quantity) FROM person_resource WHERE resource_id = 1;
-- SELECT SUM(quantity) FROM sell WHERE resource_id = 1;
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
    quantity = Column(Integer)

class SellOrder(Base):
    __tablename__ = 'sell_order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    resource_id = Column(Integer, ForeignKey('resource.id'))
    quantity = Column(Integer)
    quantity_available = Column(Integer)
    price = Column(Float)

class BuyOrder(Base):
    __tablename__ = 'buy_order'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    resource_id = Column(Integer, ForeignKey('resource.id'))
    quantity = Column(Integer)
    quantity_available = Column(Integer)
    price = Column(Float)

class BuyHistory(Base):
    __tablename__ = 'buy_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    resource_id = Column(Integer, ForeignKey('resource.id'))
    quantity = Column(Integer)
    total_price = Column(Float)
    timestamp = Column(DATETIME(fsp=6), server_default=utcnow())

class SellHistory(Base):
    __tablename__ = 'sell_history'

    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey('session.id'))
    person_id = Column(Integer, ForeignKey('person.id'))
    resource_id = Column(Integer, ForeignKey('resource.id'))
    quantity = Column(Integer)
    total_price = Column(Float)
    timestamp = Column(DATETIME(fsp=6), server_default=utcnow())



# Set up the database
engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)

# Create a session
Session_sqlalchemy = sessionmaker(bind=engine)
session = Session_sqlalchemy()



def string_to_bool(value):
    return value.lower() == "true"


def get_sell_orders(session_id, resource_id, person_id=None, b_quantity_available=True, limit=None):


    query = (session.query(Person.name, SellOrder.id, SellOrder.person_id, SellOrder.quantity, SellOrder.quantity_available, SellOrder.price)
                        .join(Person, SellOrder.person_id == Person.id)
                        .filter(Person.session_id == session_id, SellOrder.resource_id == resource_id)
                        .order_by(SellOrder.price, SellOrder.id))

    if b_quantity_available:
        query = query.filter(SellOrder.quantity_available > 0)
    else:
        query = query.filter(SellOrder.quantity > 0)


    if person_id:
        query = query.filter(SellOrder.person_id == person_id)


    if limit:
        query = query.limit(limit)


    query = query.all()


    sell_list = [dict(x._mapping) for x in query]

    return sell_list


def get_buy_orders(session_id, resource_id, person_id=None, b_quantity_available=True, limit=None):


    query = (session.query(Person.name, BuyOrder.id, BuyOrder.person_id, BuyOrder.quantity, BuyOrder.quantity_available, BuyOrder.price)
                        .join(Person, BuyOrder.person_id == Person.id)
                        .filter(Person.session_id == session_id, BuyOrder.resource_id == resource_id)
                        .order_by(desc(BuyOrder.price), BuyOrder.id))


    if b_quantity_available:
        query = query.filter(BuyOrder.quantity_available > 0)
    else:
        query = query.filter(BuyOrder.quantity > 0)


    if person_id:
        query = query.filter(BuyOrder.person_id == person_id)


    if limit:
        query = query.limit(limit)


    query = query.all()

    buy_list = [dict(x._mapping) for x in query]

    return buy_list






def create_person(session_key, name, cash, resource_dict):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id


    # Check if person already exists in person table
    if session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():
        person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

        b_success = False
        message = 'Failure (person): %s already exists' % name

        return b_success, message, person_id


    new_person = Person(session_id=session_id, name=name, cash=cash)
    session.add(new_person)
    session.commit()

    person_id = new_person.id

    # Add new resources to resource table
    for resource_type, resource_quantity in resource_dict.items():
        # Check if that resource type is already in the resource table
        if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
            # add type to resource table
            new_resource = Resource(session_id=session_id, type=resource_type)
            session.add(new_resource)
            session.commit()

        # Add resource quantities to person_resource table
        resource_id = session.query(Resource).filter(Resource.session_id == session_id,
                                                     Resource.type == resource_type).one().id

        new_person_resource = PersonResource(session_id=session_id, person_id=person_id,
                                             resource_id=resource_id, quantity=resource_quantity)
        session.add(new_person_resource)
        session.commit()

    b_success = True
    message = 'Success (person): %s created' %name


    return b_success, message, person_id



def calculate_quantity_available_for_sell_order(session_id, person_id, resource_id):

    # Check if person has resource
    if session.query(PersonResource).filter(PersonResource.session_id == session_id,
                                            PersonResource.person_id == person_id,
                                            PersonResource.resource_id == resource_id).all():

        quantity = session.query(PersonResource).filter(PersonResource.session_id == session_id,
                                                        PersonResource.person_id == person_id,
                                                        PersonResource.resource_id == resource_id).one().quantity
    else:
        quantity = 0


    # Update quantity available for each sell_order ordered by price (low to high)
    query = session.query(SellOrder).filter(SellOrder.session_id == session_id,
                                            SellOrder.person_id == person_id,
                                            SellOrder.resource_id == resource_id).order_by(SellOrder.price, SellOrder.id).all()

    remaining_quantity = quantity

    for obj in query:
        obj.quantity_available = min(obj.quantity, remaining_quantity)
        remaining_quantity = max(remaining_quantity - obj.quantity, 0)
    session.commit()


def calculate_quantity_available_for_buy_order(session_id, person_id, resource_id=None):


    cash = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one().cash


    if resource_id is None:
        # Get list of resources for all person's buy_orders
        query = session.query(BuyOrder.resource_id).filter(BuyOrder.session_id == session_id,
                                               BuyOrder.person_id == person_id,
                                               ).all()
        resource_id_list = list(set([x[0] for x in query]))

    else:
        resource_id_list = [resource_id]


    for resource_id in resource_id_list:

        remaining_cash = cash # assume the person can spend all their money on each resource

        # Update quantity available for each buy_order for each resource ordered by price (high to low)
        query = session.query(BuyOrder).filter(BuyOrder.session_id == session_id,
                                               BuyOrder.person_id == person_id,
                                               BuyOrder.resource_id == resource_id).order_by(desc(BuyOrder.price), BuyOrder.id).all()

        for obj in query:

            if obj.price > 0:
                quantity_can_afford = remaining_cash / obj.price
            else:
                quantity_can_afford = obj.quantity

            quantity_available = min(int(quantity_can_afford), obj.quantity)
            obj.quantity_available = quantity_available
            total_price = quantity_available * obj.price

            remaining_cash = max(remaining_cash - total_price, 0)
        session.commit()



def give_or_take_product(session_id, person_id, resource_id, quantity):
    # quantity > 0: give
    # quantity < 0: take

    if session.query(PersonResource).filter(PersonResource.session_id == session_id,
                                            PersonResource.person_id == person_id,
                                            PersonResource.resource_id == resource_id).all():

        previous_quantity = session.query(PersonResource).filter(PersonResource.session_id == session_id, 
                                                                 PersonResource.person_id == person_id, 
                                                                 PersonResource.resource_id == resource_id).one().quantity
        new_quantity = previous_quantity + quantity

        obj = session.query(PersonResource).filter(PersonResource.session_id == session_id, 
                                                   PersonResource.person_id == person_id,
                                                   PersonResource.resource_id == resource_id).one()
        obj.quantity = new_quantity
        session.commit()

    else:

        previous_quantity = 0
        new_quantity = previous_quantity + quantity
        new_person_resource = PersonResource(session_id=session_id, person_id=person_id,
                                             resource_id=resource_id, quantity=new_quantity)
        session.add(new_person_resource)
        session.commit()


    calculate_quantity_available_for_sell_order(session_id, person_id, resource_id)

    # # Make transactions between existing orders if possible
    # transact_buy_and_sell_orders(session_id, resource_id)


def pay_or_charge_person(session_id, person_id, dollars):
    # dollars > 0: pay
    # dollars < 0: charge

    # pay seller
    previous_cash = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one().cash
    new_cash = previous_cash + dollars

    obj = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one()
    obj.cash = new_cash
    session.commit()

    calculate_quantity_available_for_buy_order(session_id, person_id)

    # query = session.query(BuyOrder.resource_id).filter(BuyOrder.session_id == session_id,
    #                                                    BuyOrder.person_id == person_id,
    #                                                    BuyOrder.quantity_available > 0).all()
    # resource_ids = list(set([x[0] for x in query]))

    # for resource_id in resource_ids:
    #     # Make transactions between existing orders if possible
    #     transact_buy_and_sell_orders(session_id, resource_id)


def process_transaction(session_id, resource_id, seller_id, buyer_id,
                        transaction_price, transaction_quantity,
                        sell_order_id=None, buy_order_id=None):

    cost = transaction_price * transaction_quantity

    if sell_order_id:
        obj = session.query(SellOrder).filter(SellOrder.session_id == session_id, SellOrder.id == sell_order_id).one()
        obj.quantity = max(obj.quantity - transaction_quantity, 0)
        session.commit()


    if buy_order_id:
        obj = session.query(BuyOrder).filter(BuyOrder.session_id == session_id, BuyOrder.id == buy_order_id).one()
        obj.quantity = max(obj.quantity - transaction_quantity, 0)
        session.commit()



    # Process the seller
    # take items from the seller
    give_or_take_product(session_id, seller_id, resource_id, -1 * transaction_quantity)

    # pay seller
    pay_or_charge_person(session_id, seller_id, cost)

    # add entry to sell_history table
    new_sell_history = SellHistory(session_id=session_id, person_id=seller_id, resource_id=resource_id,
                                   quantity=transaction_quantity, total_price=cost)
    session.add(new_sell_history)
    session.commit()



    # Process the buyer
    # charge buyer
    pay_or_charge_person(session_id, buyer_id, -1 * cost)

    # give items to the buyer
    give_or_take_product(session_id, buyer_id, resource_id, transaction_quantity)

    # add entry to buy_history table
    new_buy_history = BuyHistory(session_id=session_id, person_id=buyer_id, resource_id=resource_id,
                                 quantity=transaction_quantity, total_price=cost)
    session.add(new_buy_history)
    session.commit()





def transact_buy_and_sell_orders(session_id, resource_id):

    b_done = False

    while not b_done:

        sell_orders = get_sell_orders(session_id, resource_id, limit=1)
        buy_orders = get_buy_orders(session_id, resource_id, limit=1)


        if not sell_orders or not buy_orders:
            # End of buy orders or end of sell orders
            b_done = True

        else:
            curr_sell_price = sell_orders[0]['price']
            curr_buy_price = buy_orders[0]['price']

            if curr_sell_price > curr_buy_price:
                # No transaction to be made
                b_done = True

            else:
                # Transaction

                transaction_price = curr_sell_price

                curr_sell_quantity = sell_orders[0]['quantity_available']
                curr_seller_id = sell_orders[0]['person_id']
                curr_sell_order_id = sell_orders[0]['id']

                curr_buy_quantity = buy_orders[0]['quantity_available']
                curr_buyer_id = buy_orders[0]['person_id']
                curr_buy_order_id = buy_orders[0]['id']


                transaction_quantity = min(curr_sell_quantity, curr_buy_quantity)


                process_transaction(session_id=session_id, resource_id=resource_id,
                                    seller_id=curr_seller_id, buyer_id=curr_buyer_id,
                                    transaction_price=transaction_price, transaction_quantity=transaction_quantity,
                                    sell_order_id=curr_sell_order_id, buy_order_id=curr_buy_order_id)





def sell_order(session_key, name, resource_type, quantity, price):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id


    if not session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():
        b_success = False
        message = 'Failure (sell order): %s does not exist' % name

        return b_success, message, -1


    if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        b_success = False
        message = 'Failure (sell order): resource %s does not exist' % resource_type

        return b_success, message, -1



    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

    resource_id = session.query(Resource).filter(Resource.session_id == session_id,
                                                 Resource.type == resource_type).one().id


    new_sell_order = SellOrder(session_id=session_id, person_id=person_id, resource_id=resource_id,
                               quantity=quantity, quantity_available=0, price=price)
    session.add(new_sell_order)
    session.commit()

    sell_order_id = new_sell_order.id

    # Calculate quantity_available for each sell_order ordered by price (low to high)
    calculate_quantity_available_for_sell_order(session_id, person_id, resource_id)

    transact_buy_and_sell_orders(session_id, resource_id)


    b_success = True
    message = 'Success (sell order): %s makes sell order of %d %s for price %.2f' % (name, quantity, resource_type, price)


    return b_success, message, sell_order_id




def buy_order(session_key, name, resource_type, quantity, price):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id


    if not session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():
        b_success = False
        message = 'Failure (buy order): %s does not exist' % name

        return b_success, message, -1


    if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        b_success = False
        message = 'Failure (buy order): resource %s does not exist' % resource_type

        return b_success, message, -1


    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

    resource_id = session.query(Resource).filter(Resource.session_id == session_id,
                                                 Resource.type == resource_type).one().id


    new_buy_order = BuyOrder(session_id=session_id, person_id=person_id, resource_id=resource_id,
                             quantity=quantity, quantity_available=0, price=price)
    session.add(new_buy_order)
    session.commit()

    buy_order_id = new_buy_order.id

    # Calculate quantity_available for each sell_order ordered by price (high to low)
    calculate_quantity_available_for_buy_order(session_id, person_id, resource_id)

    transact_buy_and_sell_orders(session_id, resource_id)


    b_success = True
    message = 'Success (buy order): %s makes buy order of %d %s for price %.2f' % (name, quantity, resource_type, price)


    return b_success, message, buy_order_id



def get_price(session_id, resource_type, desired_quantity, b_sell_price=True):

    resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

    if b_sell_price:
        orders = get_sell_orders(session_id, resource_id)
    else:
        orders = get_buy_orders(session_id, resource_id)

    running_quantity = 0
    running_cost = 0

    order_idx = 0
    while running_quantity < desired_quantity:

        curr_quantity = orders[order_idx]['quantity_available']
        curr_price = orders[order_idx]['price']

        if curr_quantity + running_quantity <= desired_quantity:
            used_quantity = curr_quantity
        else:
            used_quantity = desired_quantity - running_quantity

        running_quantity += used_quantity
        running_cost += curr_price * used_quantity

        order_idx += 1

    return running_cost



def get_price_toplevel(session_key, resource_type, desired_quantity=1, b_sell_price=True):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    price = None

    if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        b_success = False
        message = 'Failure (price): resource type %s does not exist' % resource_type

        return b_success, message, price


    resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

    if b_sell_price:
        # Get the number of items currently for sale for that resource
        num_product = (session.query(func.coalesce(func.sum(SellOrder.quantity_available), 0))
                              .filter(SellOrder.session_id == session_id, SellOrder.resource_id == resource_id)).one()[0]
    else:
        # Get the number of items currently waiting to be bought for that resource
        num_product = (session.query(func.coalesce(func.sum(BuyOrder.quantity_available), 0))
                              .filter(BuyOrder.session_id == session_id, BuyOrder.resource_id == resource_id)).one()[0]


    if desired_quantity > num_product:
        b_success = False
        message = 'Failure (price): not enough %s for sale' % resource_type

        return b_success, message, price


    price = get_price(session_id, resource_type, desired_quantity, b_sell_price=b_sell_price)

    b_success = True
    message = 'Success (price): price for %d %s is %.2f' % (desired_quantity, resource_type, price)



    return b_success, message, price


def buy_now(session_key, name, resource_type, quantity):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id


    if not session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():
        b_success = False
        message = 'Failure (buy now): person %s does not exist' % name

        return b_success, message


    if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        b_success = False
        message = 'Failure (buy now): resource %s does not exist' % resource_type

        return b_success, message


    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

    resource_id = session.query(Resource).filter(Resource.session_id == session_id,
                                                 Resource.type == resource_type).one().id

    # Get the number of items currently for sale for that resource
    num_product = (session.query(func.coalesce(func.sum(SellOrder.quantity_available), 0))
                          .filter(SellOrder.session_id == session_id, SellOrder.resource_id == resource_id)).one()[0]


    if quantity > num_product:
        b_success = False
        message = 'Failure (buy now): not enough %s for sale' % resource_type

        return b_success, message


    price = get_price(session_id, resource_type, quantity, b_sell_price=True)
    buyer_cash = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one().cash


    if buyer_cash < price:
        b_success = False
        message = 'Failure (buy now): buyer %s cannot afford the cost %.2f for %s' % (name, price, resource_type)

        return b_success, message



    sell_orders = get_sell_orders(session_id, resource_id)

    running_quantity = 0
    running_cost = 0

    sell_idx = 0
    while running_quantity < quantity:

        curr_quantity = sell_orders[sell_idx]['quantity']
        curr_quantity_available = sell_orders[sell_idx]['quantity_available']
        curr_price = sell_orders[sell_idx]['price']
        curr_seller = sell_orders[sell_idx]['person_id']
        curr_sell_order_id = sell_orders[sell_idx]['id']

        if curr_quantity_available + running_quantity <= quantity:
            used_quantity = curr_quantity_available
        else:
            used_quantity = quantity - running_quantity

        cost = curr_price * used_quantity
        running_quantity += used_quantity
        running_cost += cost

        process_transaction(session_id=session_id, resource_id=resource_id,
                            seller_id=curr_seller, buyer_id=person_id,
                            transaction_price=curr_price, transaction_quantity=used_quantity,
                            sell_order_id=curr_sell_order_id, buy_order_id=None)

        sell_idx += 1


    # Make transactions between existing orders if possible
    transact_buy_and_sell_orders(session_id, resource_id)

    b_success = True
    message = 'Success (buy now): %s buys %d %s for cost %.2f' % (name, quantity, resource_type, running_cost)


    return b_success, message



def sell_now(session_key, name, resource_type, quantity):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id


    if not session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():
        b_success = False
        message = 'Failure (sell now): person %s does not exist' % name

        return b_success, message


    if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        b_success = False
        message = 'Failure (sell now): resource %s does not exist' % resource_type

        return b_success, message


    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

    resource_id = session.query(Resource).filter(Resource.session_id == session_id,
                                                 Resource.type == resource_type).one().id

    if not session.query(PersonResource).filter(PersonResource.session_id == session_id, 
                                                PersonResource.person_id == person_id, 
                                                PersonResource.resource_id == resource_id).all():
        b_success = False
        message = 'Failure (sell now): %s has no %s' % (name, resource_type)

        return b_success, message


    seller_quantity = (session.query(PersonResource.quantity)
                              .filter(PersonResource.session_id == session_id,
                                      PersonResource.person_id == person_id,
                                      PersonResource.resource_id == resource_id)).one()[0]

    # Get the number of itmes available in the buy_orders for that resource
    num_product = (session.query(func.coalesce(func.sum(BuyOrder.quantity_available), 0))
                          .filter(BuyOrder.session_id == session_id, BuyOrder.resource_id == resource_id)).one()[0]


    if seller_quantity < quantity:
        b_success = False
        message = 'Failure (sell now): seller %s does not have enough quantity %d of resource %s' %(name, quantity, resource_type)

        return b_success, message


    if quantity > num_product:
        b_success = False
        message = 'Failure (sell now): not enough %s in the buy_orders' % resource_type

        return b_success, message


    buy_orders = get_buy_orders(session_id, resource_id)

    running_quantity = 0
    running_cost = 0

    buy_idx = 0
    while running_quantity < quantity:

        curr_quantity = buy_orders[buy_idx]['quantity']
        curr_quantity_available = buy_orders[buy_idx]['quantity_available']
        curr_price = buy_orders[buy_idx]['price']
        curr_buyer = buy_orders[buy_idx]['person_id']
        curr_buy_order_id = buy_orders[buy_idx]['id']

        if curr_quantity_available + running_quantity <= quantity:
            used_quantity = curr_quantity_available
        else:
            used_quantity = quantity - running_quantity

        cost = curr_price * used_quantity
        running_quantity += used_quantity
        running_cost += cost

        process_transaction(session_id=session_id, resource_id=resource_id,
                            seller_id=person_id, buyer_id=curr_buyer,
                            transaction_price=curr_price, transaction_quantity=used_quantity,
                            sell_order_id=None, buy_order_id=curr_buy_order_id)

        buy_idx += 1


    # Make transactions between existing orders if possible
    transact_buy_and_sell_orders(session_id, resource_id)


    b_success = True
    message = 'Success (sell now): %s sells %d %s for cost %.2f' % (name, quantity, resource_type, running_cost)



    return b_success, message





def get_assets(session_key, name):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    cash = None
    resource_list = None


    if not session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():
        b_success = False
        message = 'Failure (assets): %s does not exist' % name

        return b_success, message, cash, resource_list


    cash = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().cash

    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id


    # Get resources from person name and sort by resource type
    query = (session.query(Resource.type, PersonResource.quantity).join(Resource, PersonResource.resource_id == Resource.id)
                    .filter(PersonResource.session_id == session_id, 
                            PersonResource.person_id == person_id, 
                            PersonResource.quantity > 0)
                    .order_by(Resource.type)).all()

    resource_list = [dict(x._mapping) for x in query]


    b_success = True
    message = 'Success (assets): got assets for %s' % name


    return b_success, message, cash, resource_list



def get_orders_toplevel(session_key, resource_type, name=None, b_quantity_available=None, b_buy_orders=None):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    order_list = None
    person_id = None

    if name:
        if not session.query(Person).filter(Person.session_id == session_id, Person.name == name).all():
            b_success = False
            message = 'Failure (market): %s does not exist' % name

            return b_success, message, order_list

        person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id


    if not session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        b_success = False
        message = 'Failure (market): resource type %s does not exist' % resource_type

        return b_success, message, order_list


    resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id


    if b_buy_orders:
        order_list = get_buy_orders(session_id, resource_id, person_id, b_quantity_available=b_quantity_available)
    else:
        order_list = get_sell_orders(session_id, resource_id, person_id, b_quantity_available=b_quantity_available)


    b_success = True
    message = 'Success (market): returned order data for %s' % resource_type

    return b_success, message, order_list



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



def cancel_sell_order(session_key, sell_id):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    person_id = session.query(SellOrder).filter(SellOrder.session_id == session_id, SellOrder.id == sell_id).one().person_id
    resource_id = session.query(SellOrder).filter(SellOrder.session_id == session_id, SellOrder.id == sell_id).one().resource_id
    quantity = session.query(SellOrder).filter(SellOrder.session_id == session_id, SellOrder.id == sell_id).one().quantity


    # Set quantity to zero in sale row
    obj = session.query(SellOrder).filter(SellOrder.session_id == session_id, SellOrder.id == sell_id).one()
    obj.quantity = 0
    obj.quantity_available = 0
    session.commit()

    # Calculate quantity_available for each sell_order ordered by price (low to high)
    calculate_quantity_available_for_sell_order(session_id, person_id, resource_id)

    b_success = True
    message = 'SUCCESS (cancel sell order): sale %d canceled' % sell_id

    return b_success, message



def cancel_buy_order(session_key, buy_id):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    person_id = session.query(BuyOrder).filter(BuyOrder.session_id == session_id, BuyOrder.id == buy_id).one().person_id
    resource_id = session.query(BuyOrder).filter(BuyOrder.session_id == session_id, BuyOrder.id == buy_id).one().resource_id
    quantity = session.query(BuyOrder).filter(BuyOrder.session_id == session_id, BuyOrder.id == buy_id).one().quantity


    # Set quantity to zero in sale row
    obj = session.query(BuyOrder).filter(BuyOrder.session_id == session_id, BuyOrder.id == buy_id).one()
    obj.quantity = 0
    obj.quantity_available = 0
    session.commit()

    # Calculate quantity_available for each buy_order ordered by price (high to low)
    calculate_quantity_available_for_buy_order(session_id, person_id, resource_id)

    b_success = True
    message = 'SUCCESS (cancel buy order): buy order %d canceled' % buy_id

    return b_success, message



def deposit_or_withdraw(session_key, name, b_deposit, dollars):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id
    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id

    if not b_deposit:

        # withdraw
        buyer_cash = session.query(Person).filter(Person.session_id == session_id, Person.id == person_id).one().cash

        if buyer_cash < dollars:
            b_success = False
            message = 'Failure (deposit): %s has not enough cash to withdraw %.2f' %(name, dollars)
            return b_success, message

        dollars = -1 * dollars

    pay_or_charge_person(session_id, person_id, dollars)

    action_str = 'deposit' if b_deposit else 'withdraw'

    b_success = True
    message = 'Success (deposit): %s %.2f with account %s' %(action_str, dollars, name)

    return b_success, message



def give_or_take_resource(session_key, name, resource_type, b_deposit, quantity):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id
    person_id = session.query(Person).filter(Person.session_id == session_id, Person.name == name).one().id
    resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

    if not b_deposit:

        # check that person has resource
        if not session.query(PersonResource).filter(PersonResource.session_id == session_id,
                                                    PersonResource.person_id == person_id,
                                                    PersonResource.resource_id == resource_id
                                                    ).all():
            b_success = False
            message = 'Failure (give): %s has no %s to withdraw' %(name, resource_type)
            return b_success, message


        # withdraw
        available_quantity = session.query(PersonResource).filter(PersonResource.session_id == session_id,
                                                                  PersonResource.person_id == person_id,
                                                                  PersonResource.resource_id == resource_id).one().quantity

        if available_quantity < quantity:
            b_success = False
            message = 'Failure (give): %s has not enough %s to withdraw %d' %(name, resource_type, quantity)
            return b_success, message

        quantity = -1 * quantity

    give_or_take_product(session_id, person_id, resource_id, quantity)

    action_str = 'deposit' if b_deposit else 'withdraw'

    b_success = True
    message = 'Success (give): %s %d %s with account %s' %(action_str, quantity, resource_type, name)

    return b_success, message


def new_resource(session_key, resource_type):

    session_id = session.query(Session).filter(Session.session_key == session_key).one().id

    if session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).all():
        resource_id = session.query(Resource).filter(Resource.session_id == session_id, Resource.type == resource_type).one().id

        b_success = False
        message = 'Failure (new_resource): %s already exists in resource table' %resource_type

        return b_success, message, resource_id


    new_resource = Resource(session_id=session_id, type=resource_type)
    session.add(new_resource)
    session.commit()

    resource_id = new_resource.id

    b_success = True
    message = 'Success (new_resource): %s added to resource table' %resource_type


    return b_success, message, resource_id



def create_session(session_key):

    if session.query(Session).filter(Session.session_key == session_key).all():
        session_id = session.query(Session).filter(Session.session_key == session_key).one().id

        b_success = True
        message = 'Success (session): session key %s already exists' %session_key

        return b_success, message, session_id


    new_session = Session(session_key=session_key)
    session.add(new_session)
    session.commit()

    session_id = new_session.id

    b_success = True
    message = 'Success (session): session key %s created' %session_key

    return b_success, message, session_id





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

        b_success, message, person_id = create_person(session_key, name, cash, resource_dict)

        return_data = {
                        'name': name,
                        'person_id': person_id
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405



@app.route('/sell_order', methods=['POST'])
def api_sell_order():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        name = data['name']
        resource_type = data['resource_type']
        quantity = data['quantity']
        price = data['price']

        b_success, message, order_id = sell_order(session_key, name, resource_type, quantity, price)

        return_data = {
                        'name': name,
                        'order_id': order_id,
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/buy_order', methods=['POST'])
def api_buy_order():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        name = data['name']
        resource_type = data['resource_type']
        quantity = data['quantity']
        price = data['price']

        b_success, message, order_id = buy_order(session_key, name, resource_type, quantity, price)

        return_data = {
                        'name': name,
                        'order_id': order_id
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/buy_now', methods=['POST'])
def api_buy_now():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        name = data['name']
        resource_type = data['resource_type']
        quantity = data['quantity']

        b_success, message = buy_now(session_key, name, resource_type, quantity)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/sell_now', methods=['POST'])
def api_sell_now():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        name = data['name']
        resource_type = data['resource_type']
        quantity = data['quantity']

        b_success, message = sell_now(session_key, name, resource_type, quantity)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405



@app.route('/get_price', methods=['GET'])
def api_get_price():
    if request.method == 'GET':

        quantity = 1
        b_sell_price = True

        session_key = request.args.get('session_key')
        resource_type = request.args.get('resource_type')
        if 'quantity' in request.args:
            quantity = int(request.args.get('quantity'))
        if 'b_sell_price' in request.args:
            b_sell_price = request.args.get('b_sell_price')
            b_sell_price = string_to_bool(b_sell_price)


        b_success, message, price = get_price_toplevel(session_key, resource_type, quantity, b_sell_price=b_sell_price)

        return_data = {
                        'resource_type': resource_type,
                        'price': price
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
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

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405




@app.route('/get_orders', methods=['GET'])
def api_get_orders():
    if request.method == 'GET':

        name = None
        b_quantity_available = None
        b_buy_orders = None

        session_key = request.args.get('session_key')
        resource_type = request.args.get('resource_type')
        if 'name' in request.args:
            name = request.args.get('name')
        if 'b_quantity_available' in request.args:
            b_quantity_available = request.args.get('b_quantity_available')
            b_quantity_available = string_to_bool(b_quantity_available)
        if 'b_buy_orders' in request.args:
            b_buy_orders = request.args.get('b_buy_orders')
            b_buy_orders = string_to_bool(b_buy_orders)


        b_success, message, orders_list = get_orders_toplevel(session_key, resource_type, name, b_quantity_available, b_buy_orders)

        return_data = {
                        'resource_type': resource_type,
                        'orders_list': orders_list
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
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

        response = {'message': message, 'data': return_data, 'b_success': b_success}
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


        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/cancel_sell_order', methods=['POST'])
def api_cancel_sell_order():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        sell_id = data['sell_id']


        b_success, message = cancel_sell_order(session_key, sell_id)


        return_data = {
                        'sell_id': sell_id
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405



@app.route('/cancel_buy_order', methods=['POST'])
def api_cancel_buy_order():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        buy_id = data['buy_id']


        b_success, message = cancel_buy_order(session_key, buy_id)


        return_data = {
                        'buy_id': buy_id
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405



@app.route('/deposit_or_withdraw', methods=['POST'])
def api_deposit_or_withdraw():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        name = data['name']
        b_deposit = data['b_deposit']
        dollars = data['dollars']

        b_success, message = deposit_or_withdraw(session_key, name, b_deposit, dollars)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
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
        b_deposit = data['b_deposit']
        quantity = data['quantity']

        b_success, message = give_or_take_resource(session_key, name, resource_type, b_deposit, quantity)

        return_data = {
                        'name': name
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/new_resource', methods=['POST'])
def api_new_resource():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']
        resource_type = data['resource_type']

        b_success, message, resource_id = new_resource(session_key, resource_type)

        return_data = {
                        'resource_type': resource_type,
                        'resource_id': resource_id
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405


@app.route('/create_session', methods=['POST'])
def api_create_session():
    if request.method == 'POST':
        data = request.get_json()  # Get JSON data from the request body

        session_key = data['session_key']

        b_success, message, session_id = create_session(session_key)

        return_data = {
                        'session_key': session_key,
                        'session_id': session_id
                        }

        response = {'message': message, 'data': return_data, 'b_success': b_success}
        return jsonify(response), 201  # Return a JSON response with status code 201
    else:
        return 'Method not allowed', 405




def main():
    app.run(host='0.0.0.0', port=8000, debug=True)




if __name__ == '__main__':
    main()



