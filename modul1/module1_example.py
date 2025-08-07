#create triangle

r_slash="/"
l_slash="\\"
top="^"
base="_"
newline="\n"
space=" "

print(space, space, space, top, space, space, space)
print(space, space, r_slash, space, l_slash, space, space)
print(space, r_slash, space, space, space, l_slash, space)
print(r_slash, base, base, base, base, base, l_slash)

str_top=f"{space}{space}{top}{space}{space}{newline}"
str_1=f"{space}{r_slash}{space}{l_slash}{space}{newline}"
base=f"{r_slash}{base}{base}{base}{l_slash}{newline}"

final_str=f"{str_top}{str_1}{base}"
print(final_str)


#la alegere