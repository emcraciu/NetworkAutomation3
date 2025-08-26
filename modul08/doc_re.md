# Module8: Regular Expressions with the `re` Module

## 1. Introduction
Regular expressions (regex) are a powerful tool for pattern matching and text processing.  
Python provides the built-in **`re`** module to work with regex efficiently.

Common use cases:
- Validating input (emails, phone numbers).  
- Searching for substrings.  
- Replacing patterns in text.  
- Extracting structured data from logs or files.  

---

## 2. Basic Functions in `re`

### `re.match()`
Matches a pattern **only at the beginning** of a string.
```python
import re

pattern = r"Hello"
text = "Hello World"

match = re.match(pattern, text)
if match:
    print("Matched:", match.group())
```

### `re.search()`
Searches for the **first occurrence** of the pattern anywhere in the string.
```python
import re

pattern = r"World"
text = "Hello World"

result = re.search(pattern, text)
if result:
    print("Found:", result.group())
```

### `re.findall()`
Finds **all matches** of the pattern and returns them as a list.
```python
import re

pattern = r"\d+"  # one or more digits
text = "There are 24 apples and 7 oranges."

print(re.findall(pattern, text))  # ['24', '7']
```

### `re.sub()`
Replaces matches with another string.
```python
import re

pattern = r"apples"
text = "I like apples."

new_text = re.sub(pattern, "oranges", text)
print(new_text)
```

---

## 3. Using Groups and Captures
Regex groups allow extracting parts of a match.

```python
import re

pattern = r"(\d+)-(\w+)"
text = "123-abc"

match = re.search(pattern, text)
if match:
    print("Full match:", match.group(0))
    print("First group:", match.group(1))
    print("Second group:", match.group(2))
```

---

## 4. Compiling Patterns
For repeated use, compile regex patterns for efficiency.

```python
import re

pattern = re.compile(r"\b\w+\b")  # matches words
text = "Python regex is powerful."

for m in pattern.finditer(text):
    print("Word:", m.group())
```

---

## 5. Practical Examples

### Validate Email Address
```python
import re

pattern = r"^[\w.-]+@[\w.-]+\.\w+$"
emails = ["user@example.com", "invalid-email", "hello@world.org"]

for email in emails:
    if re.match(pattern, email):
        print(email, "is valid")
    else:
        print(email, "is invalid")
```

### Extract IP Addresses from Text
```python
import re

pattern = r"(\d{1,3}\.){3}\d{1,3}"
log = "Ping results: 192.168.1.1 OK, 10.0.0.5 Fail"

print(re.findall(pattern, log))
```

---

## 6. Conclusion
The `re` module makes it possible to handle text matching and extraction tasks elegantly.  
With practice, regex becomes an essential tool for **data cleaning, parsing logs, and validation tasks**.

---

## 7. References
- Python Docs: [re module](https://docs.python.org/3/library/re.html)  
- Real Python: [Regex Tutorial](https://realpython.com/regex-python/)  
- Regex101 (interactive tool): [https://regex101.com/](https://regex101.com/)  
