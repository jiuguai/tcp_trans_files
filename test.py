

size = 100
cur_size = 21
per = cur_size/size
process_count = 20



print("-" * (int(process_count * per)))

print("[{}{}]".format("-"*5, " "*20))
print("{:.2%}".format(per))