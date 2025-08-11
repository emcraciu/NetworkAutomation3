def find_cheapest_shop(cart: dict, shops: dict) -> dict:
    if not cart:
        return {'shop': None, 'total': 0.0}

    best_shop = None
    best_total = float('inf')

    for shop_name, price_map in shops.items():
        total = 0.0
        for item, qty in cart.items():
            price = price_map.get(item)
            if price is None:
                break
            total += qty * price
        else:

            if total < best_total:
                best_total = total
                best_shop = shop_name

    if best_shop is None:
        return {'shop': None, 'total': None}

    return {'shop': best_shop, 'total': round(best_total, 2)}



cart = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

print(find_cheapest_shop(cart, shops))

