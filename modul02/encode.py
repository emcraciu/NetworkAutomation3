number_a =  ord('a')
print(number_a)

character_97 =  chr(97)
print(character_97)

character_254 =  chr(254)
print(character_254)

enc = 1000 ^ 496
print(enc)
dec = enc ^ 496
print(dec)

# 1 0 1 0
# 0 0 1 0
# 1 0 0 0

text = "Hello Python"
key = 7
enc = []

for letter in text:
    c = chr(ord(letter) ^ key)
    enc.append(c)

enc_test = ''.join(enc)
print(enc_test)

dec = []
for letter in enc_test:
    d = chr(ord(letter) ^ key)
    dec.append(d)
dec_test = ''.join(dec)
print(dec_test)
