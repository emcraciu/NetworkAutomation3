# Exercise 2 - read module3 first
# Create function that will take as input a cart of items and shops where the products can be purchased. Function will return a dict with shop name where the specified cart items and quantities have the smallest total cost and the total cost in that shop
#
# cart = {'apple': 10, 'plums': 15, 'bananas': 5}
#
# shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
# shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
# shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}
#
# shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}
# Info:
# in the cart the value represents the number or units of that item
# in shop_X the value represents the cost per unit of a specific item
# Considerations:
# cart can have items that are not in some shops and in this case shop needs to be excluded
# shops can have large number of items compared to the cart so optimise your for loops

cart = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}
cart_shops = shops.copy()

def create_dict_of_useful_shops():
    global shops
    global cart
    global cart_shops
    for item in cart:
        shops = cart_shops.copy()
        for shop in shops.items():
            if item not in shop[1].keys():
                cart_shops.pop(shop[0])
                continue


def find_least_expensive_shop():
    global cart_shops
    min_total = 9999999999
    min_shop = None
    for item in cart_shops.items():
        sum_item = (cart['apple'] * item[1]['apple'] +
                    cart['plums'] * item[1]['plums'] +
                    cart['bananas'] * item[1]['bananas'])
        if sum_item < min_total:
            min_total = sum_item
            min_shop = item[0]
    return min_shop, min_total


if __name__ == '__main__':
    create_dict_of_useful_shops()
    min_shop, min_total = find_least_expensive_shop()
    print(min_shop, min_total)
