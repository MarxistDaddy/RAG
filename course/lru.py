from functools import lru_cache

def fib(n):
    if n < 2:
        return n
    
    print(n)
    return fib(n - 1) + fib(n - 2)



fib = lru_cache(maxsize=None)(fib) 


print("without lru")
print(fib(9))

print("\nwith lru")
print(fib(9))
print(fib(9))
print(fib(9))
print(fib(9))






