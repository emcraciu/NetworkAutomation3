# create encoder that transforms a > b, b > c .... and all spaces to '\n'

"Hello Pithon. This is converted text."

# import x
def encode(s: str) -> str:
    return ''.join(map(lambda ch: '\n' if ch == ' ' else chr(ord(ch) + 1), s))

text = "Hello Pithon. This is converted text"
print(encode(text))

