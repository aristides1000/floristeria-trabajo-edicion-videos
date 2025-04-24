#def numerospares(arreg):
#    
#    pares = [num for num in arreg if num % 2 == 0]
#    return pares
#
#
# 
#arreg = [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12]
#resultado = numerospares(arreg)
#print(f"Los números pares son: {resultado}")


def numeros_pares_sin_modulo(arreg):

    pares = [num for num in arreg if round(num / 2) * 2 == round(num)]
    return pares


arreg = [1, 2, 3, 4, 5, 6, 7, 8, 9,10,11,12]
resultado = numeros_pares_sin_modulo(arreg)
print(f"Los números pares son: {resultado}")

