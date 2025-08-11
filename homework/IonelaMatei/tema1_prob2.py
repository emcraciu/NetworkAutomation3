'''
    ## Exercise 2 - read module3 first

    Create function that will take as input a cart of items and shops where the products can be purchased.
    Function will return a dict with shop name where the specified cart items and quantities
    fave the smallest total cost and the total cost in that shop

    ```python
    cart = {'apple': 10, 'plums': 15, 'bananas': 5}

    shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5} #aici este pretul produsului
    shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
    shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

    shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

    ```
    #### Info:
    - in the cart the value represents the number or units of that item
    - in shop_X the value represents the cost per unit of a specific item

    ### Considerations:
    - cart can have items that are not in some shops and in this case shop needs to be excluded
    - shops can have large number of items compared to the cart so optimise your for loops


    '''


def best_choice(cart, shops):
    best_shop = None
    min_pret = None
    for store_name, store_prices in shops.items():
        if not all(item in store_prices for item in cart):
            continue
        total = 0
        for item, cantitate in cart.items():
            total = total + store_prices[item] * cantitate
        if min_pret is None or total < min_pret:
            min_pret = total
            best_shop = store_name
    if best_shop is not None:
        return {best_shop: min_pret}
    else:
        return None


cart = {}  # initial nu exista nimic in cosul de cumparaturi
while True:
    produs = input("Introduceti produsul pe care doriti sa-l achizitionati: ")
    if produs in cart:
        actualizare = input("Produsul exista deja in cosul de cumparaturi ! Doriti sa actualizati cantitatea? da/nu: ")
        if actualizare.lower() == 'da':
            try:
                cantitate = int(input("Introduceti noua cantitate a produslui: "))
                cart[produs] = cantitate
            except ValueError:
                print("Cantitatea trebuie sa fie un numar valid !")
                continue
        else:
            print("Produsul existent in cos a ramas nemodificat !")
    else:
        try:
            cantitate = int(input("Introduceti cantitatea produslui: "))
            cart[produs] = cantitate
            print("Produsul a fost adaugat in cos !")
        except ValueError:
            print("Cantitatea trebuie sa fie un numar valid !")
            continue
    alegere = input("Doriti sa mai adaugati alte produse in cos? da/nu: ")
    if alegere.lower() == 'nu':
        break
print("Cosul de cumparaturi este:", cart)

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}
shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

rezultat = best_choice(cart, shops)
if rezultat:
    print("Magazinul cu cele mai bune preturi si costul total:", rezultat)
else:
    print("Nu exista niciun magazin care sa aiba toate produsele din cos !")
