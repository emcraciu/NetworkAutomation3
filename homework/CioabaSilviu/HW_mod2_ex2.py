def cheapest_shop(cart: dict[str, float], shops: dict[str, dict[str, float]]) -> dict | None:
    if not cart:
        return None

    cart_items = set(cart.keys())
    best_name, best_total = None, float("inf")

    for shop_name, price_map in shops.items():
        # skip shops that don't have all required items
        if not cart_items.issubset(price_map.keys()):
            continue

        # calculate total cost
        total = sum(cart[item] * price_map[item] for item in cart_items)

        if total < best_total:
            best_total = total
            best_name = shop_name

    if best_name is None:
        return None  # no shop can supply all items

    return {"shop": best_name, "total": round(best_total, 2)}


if __name__ == "__main__":
    cart = {'apple': 10, 'plums': 15, 'bananas': 5}

    shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
    shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
    shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

    shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

    result = cheapest_shop(cart, shops)
    print(result)
