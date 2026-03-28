contagem = 0

print('\n' + '>'*30)
while True:
    telefonou = str(input(' Você telefonou pra vítima? '))
    if telefonou in ['sim']:
             
        contagem +=1
    break
else:
    print('Resposta inválida. Digite apenas "sim" ou "não".')   


print('\n' + '>'*30)
while True:

    esteve = input(' Esteve no local do crime?  ')
    if esteve.isalpha():
        if esteve in ['sim']:
            contagem +=1
            break
    else:
        print('Resposta inválida. Digite apenas "sim" ou "não".')   
print('<'*30)

print('\n' + '>'*30)
mora = input(' Mora perto da vítima? ')
if mora in ['sim']:
    contagem +=1
print('<'*30)

print('\n' + '>'*30)
devia = input(' Devia para a vítima? ')
if devia in ['sim']:
    contagem +=1
print('<'*30)

print('\n' + '>'*30)
trabalhou = input(' Já trabalhou com a vítima? ')
if trabalhou in ['sim']:
    contagem +=1
print('<'*30)

if contagem == 5:
    print( 'ASSASSINO!')
elif contagem >= 3:
    print( 'CÚMPLICE! ')
elif contagem == 2:
    print( ' SUSPEITO! ')
else:
    print(' INOCENTE! ')
