import fire

def greet(name = "world", capital = False):
    g = f"Hello, {name}"
    if capital:
        print(g.capitalize())
    else:
        print(g)








def main():
    fire.Fire(greet)


if __name__ == "__main__":
    main()
