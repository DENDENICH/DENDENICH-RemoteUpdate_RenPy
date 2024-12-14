import os


print(f'Текущая дериктория os.getcwd(): \n\t{os.getcwd()}')

path = os.path.abspath(__file__).replace(
    old=os.path.basename(__file__),
    new=''
    )

print(f'Текущая дериктория abspath: \n\t{path}')