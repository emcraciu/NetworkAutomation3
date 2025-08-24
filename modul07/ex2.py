# filter words with len > specified

text  = "Hello Python. This: is; converted text."

def get_long_words(text_var: str, length) -> list:
    return list(
        filter(
            lambda x: len(x) > length,
            map(lambda _: _.strip(",.;:"), text.split()),
        )
    )

print(get_long_words(text, 3))