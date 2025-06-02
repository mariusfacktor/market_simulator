
# relative import
import sys
from pypi_package.src.marketsandbox import marketsandbox as ms

# import marketsandbox as ms


def example():
    # make a session key which can be any string you choose
    SK = 'hamster'
    ms.create_session(session_key=SK)

    # create a resource called carrot and a person called Ham Solo who starts with $200
    ms.create_resource(session_key=SK, resource_type='carrot')
    ms.create_person(session_key=SK, name='Ham Solo', money=200.00)

    # give Ham Solo 30 carrots to start
    ms.deliver_resource(session_key=SK, name='Ham Solo', resource_type='carrot', quantity=30)

    # Ham Solo wants to sell 10 carrots for $1.25 each
    ms.sell_limit_order(session_key=SK, name='Ham Solo', resource_type='carrot', quantity=10, price=1.25)

    # Get the lowest price for sale on the market
    ask_price = ms.get_ask_price(session_key=SK, resource_type='carrot')

    print(ask_price) # -> 1.25



def test_all():
    session_key = 'bagel'

    nameA = 'Blake Johnson'
    nameB = 'Janice Hobbs'

    resourceA = 'apple'

    # session_key = ms.create_session(session_key=session_key)

    # resource_id = ms.create_resource(session_key=session_key, resource_type=resourceA)

    # person_id = ms.create_person(session_key=session_key, name=nameA, money=200.00, resource_dict={resourceA: 120})
    # person_id = ms.create_person(session_key=session_key, name=nameB, money=1500.00)


    # sell_id = ms.sell_limit_order(session_key=session_key, name=nameA, resource_type=resourceA, quantity=8, price=2.50)

    # buy_id = ms.buy_limit_order(session_key=session_key, name=nameB, resource_type=resourceA, quantity=4, price=1.14)

    # b_success = ms.buy_market_order(session_key=session_key, name=nameB, resource_type=resourceA, quantity=3)

    # ask_price = ms.get_ask_price(session_key=session_key, resource_type=resourceA, quantity=3)

    # bid_price = ms.get_bid_price(session_key=session_key, resource_type=resourceA, quantity=1)


    # b_success = ms.deposit(session_key=session_key, name=nameA, money=10.20)

    # b_success = ms.withdraw(session_key=session_key, name=nameB, money=5.30)

    # b_success = ms.deliver_resource(session_key=session_key, name=nameB, resource_type=resourceA, quantity=1)

    # b_success = ms.receive_resource(session_key=session_key, name=nameA, resource_type=resourceA, quantity=3)

    # cash, resource_dict = ms.get_assets(session_key=session_key, name=nameA)

    people_list = ms.get_people(session_key=session_key)

    resource_list = ms.get_resources(session_key=session_key)



    # b_success = ms.cancel_sell_limit_order(session_key=session_key, order_id=sell_id)

    # b_success = ms.cancel_buy_limit_order(session_key=session_key, order_id=buy_id)


    sell_orders = ms.get_sell_limit_orders(session_key=session_key, resource_type=resourceA)

    buy_orders = ms.get_buy_limit_orders(session_key=session_key, resource_type=resourceA)

    supply_price_list, supply_quantity_list, \
    demand_price_list, demand_quantity_list = ms.get_supply_and_demand_chart_data(session_key=session_key, resource_type=resourceA)


    print(people_list)



def main():

    test_all()
    # example()
    

if __name__ == '__main__':
    main()

