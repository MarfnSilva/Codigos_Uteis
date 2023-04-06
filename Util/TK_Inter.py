from requests import *
from time import *
from tkinter import *

# get()
# sleep()
def printar():
    # print("Deu certo")
    texto["text"] = 'Deu Certo'

janela = Tk()
janela.title("Titulo Teste")
janela.geometry("250x250")

teste = Label(janela, text="teste de texto")
teste.grid(column=0, row=0, padx=10, pady=10)

botao = Button(janela, text="Click Aqui", command=printar)
botao.grid(column=0, row=1)

texto = Label(janela, text="")
texto.grid(column=0, row=2)

janela.mainloop()