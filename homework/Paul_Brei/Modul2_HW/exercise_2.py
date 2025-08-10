
final_result={}
# cart={}
# n = int(input("Enter the number of entries: "))
# cart = {input("Enter product: "): float(input("Enter number of products to be purchased: ")) for _ in range(n)}
# shops={}
# n = int(input("Enter the number of shops: "))
# shops = {input("Enter shop key: "): input("Enter shop name: ") for _ in range(n)}

cart = {'apples': 10, 'plums': 15, 'bananas': 5}
shops = {'pro': 'shop_P', 'lil': 'shop_L', 'kau': 'shop_K'}

print("initial cart and shops: ", cart, shops)

price_lists={
    'shop_K' : {'apples': 1.2, 'plums': 4, 'bananas': 5.5},
    'shop_P' : {'apples': 1.3, 'plums': 3, 'bananas': 8},
    'shop_F' : {'apples': 1.3, 'plums': 3},
    'shop_L' : {'apples': 1.4, 'plums': 2, 'bananas': 10}
}


def shopping_func(cart, shops, price_lists):
    valid_shops = {}
    res={}

    for shop_key, shop_name in shops.items():
        items_present = True

        for item in cart:
            if item not in price_lists[shop_name]:
                items_present = False
                #print("break")
                break

        if items_present:
            total_cost = 0.0
            for item, quantity in cart.items():
                total_cost += price_lists[shop_name][item] * quantity
                #print(total_cost)
            valid_shops[shop_key] = total_cost

    cheapest_shop=next(iter(valid_shops))
    min_cost=valid_shops[cheapest_shop]

    for valid_shop_name, cost in valid_shops.items():
        if cost< min_cost:
            min_cost=cost
            cheapest_shop=valid_shop_name

    res.update({shops[cheapest_shop]:min_cost})
    return res

print(shopping_func(cart,shops,price_lists))
