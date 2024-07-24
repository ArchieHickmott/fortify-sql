class a:
    test = 1

def my_cool_func(**kwargs):
    for name, arg in kwargs.items():
        getattr(a, name)
        
my_cool_func(test=True)