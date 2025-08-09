def determine_cheapest_shop(cart, shops):
    cart_items = set(cart.keys()) #to search fast our products with issubset method of set
    cheapest_cost = float('inf') #to store the cheapest cost found
    cheapest_name = '' #the name for the cheapest shop

    #we scan every shop for our items
    for shop_name, shop_variable in shops.items():
        if not cart_items.issubset(shop_variable.keys()):
            continue #if we don't have all the needed items we move on to the next shop

        total_cost = 0.0
        for item, quantity in cart.items():
            total_cost += quantity * shop_variable[item]
            if total_cost > cheapest_cost:
                break #if we have already a bigger cost we move on

        if total_cost < cheapest_cost:
            cheapest_cost = total_cost
            cheapest_name = shop_name

    return {cheapest_name: cheapest_cost}

cart = {'apple': 10, 'plums': 15, 'bananas': 5}
shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}
shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

print(determine_cheapest_shop(cart, shops))
