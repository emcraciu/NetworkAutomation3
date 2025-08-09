print("#### Exercise 2 ########")


def cheapest_shop(cart, shops):
     best=None
     best_cost=100000000000000000000000
     for n,m in shops.items():
         if all(item in m for item in cart):#verifica daca magazinul are toate produsele
            sum_ = 0
            for i,j in cart.items():
                sum_+=m[i]*j
            if sum_<best_cost:
                best_cost=sum_
                best=n
     if best is None:
         return f"Niciun magazin nu are toate produsele din coș"
     else:
         return f"{best}: {best_cost}"

cart = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

result = cheapest_shop(cart, shops)
print(result)