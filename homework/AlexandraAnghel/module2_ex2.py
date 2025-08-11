def choose_shop(cart, shops):
    best_shop = None
    best_total = None
    for shop_name, price_map in shops.items():
        missing = False
        for item in cart:
            if item not in price_map:
                missing = True
                break
        if missing:
            continue
        total = 0.0
        for item, qty in cart.items():
            total += price_map[item] * qty
        if best_total is None or total < best_total:
            best_total = total
            best_shop = shop_name
    if best_shop is None:
        return None
    return {"shop": best_shop, "total": round(best_total, 2)}


if __name__ == "__main__":
    cart = {'apple': 10, 'plums': 15, 'bananas': 5}
    shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
    shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
    shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}
    shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}
    result = choose_shop(cart, shops)
    print(result)
