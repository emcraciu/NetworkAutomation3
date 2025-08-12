# function for first 100 prime numbers

def prime():
    prime_counter = 0
    nrs = 3
    result_in_function = [1, 2]

    while (prime_counter <= 100):
        for i in range(2, nrs // 2 + 1):
            if not nrs % i:
                break
        else:
            prime_counter += 1
            result_in_function.append(nrs)
        nrs += 1

    return result_in_function


# returnati primele 100 de numere prime
print(50 * "*")

def is_prime(num):
    if num < 2:
        return False
    if num == 2:
        return True
    for i in range(2, int(num ** 0.5) + 1):
        if num % i == 0:
            return False
    return True


def first_100_primes():
    primes = []
    j = 0
    while len(primes) < 100:
        if is_prime(j):
            primes.append(j)
        j += 1
    return primes


print(primes_100 := first_100_primes())

# print(__name__)
if __name__ == '__main__':
    result = prime()
    print(result)
