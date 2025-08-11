
def cheapest_shop(cart, shops):

    cheapest_shop_name = None
    cheapest_total = float('inf')

    for name, price_list in shops.items():
        total = 0.0
        missing_item = False
        for item, qty in cart.items():
            price = price_list.get(item)
            if price is None:
                missing_item = True
                break
            total += qty * price
        if not missing_item and total < cheapest_total:
            cheapest_shop_name = name
            cheapest_total = total
    return {"shop": cheapest_shop_name, "total": cheapest_total}



cart = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

print(cheapest_shop(cart, shops))