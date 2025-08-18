def ieftin(cos, shops):
    best = None
    produse = set(cos.keys())

    for nume, pret in shops.items():
        if not produse.issubset(pret.keys()):
            continue

        total = 0.0
        for item, qty in cos.items():
            total += qty * float(pret[item])

        if best is None or total < best[1]:
            best = (nume, total)

    return {} if best is None else {best[0]: best[1]}

cos = {'apple': 10, 'plums': 15, 'bananas': 5}

shop_K = {'apple': 1.2, 'plums': 4, 'bananas': 5.5}
shop_P = {'apple': 1.3, 'plums': 3, 'bananas': 8}
shop_L = {'apple': 1.4, 'plums': 2, 'bananas': 10}

shops = {'pro': shop_P, 'lil': shop_L, 'kau': shop_K}

print(ieftin(cos, shops))
