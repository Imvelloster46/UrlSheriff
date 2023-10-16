import socket
from tkinter import *
from tkinter import scrolledtext
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


# Função para executar a varredura
def executar_varredura():
    # Limpa a área de resultados
    txt.delete('1.0', END)

    # Obtém a URL inserida pelo usuário
    url = entry.get()

    try:
        # Faz uma requisição GET para a URL
        resposta_http = requests.get(url)
        resposta_http.raise_for_status()  # Lança uma exceção para erros HTTP
        texto_html = resposta_http.text

        # Parceia o HTML da página usando o BeautifulSoup
        soup = BeautifulSoup(texto_html, 'html.parser')

        # Procura por links que poderiam ser vulneráveis a ataques de força bruta
        for link in soup.find_all('a'):
            # Verifica se o link parece ser uma área restrita
            if 'admin' in link.get('href'):
                txt.insert(INSERT, f'Potencial área administrativa encontrada: {link.get("href")}\n')

        # Verifica se a página possui um formulário de login
        formulario = soup.find('form')
        if formulario:
            txt.insert(INSERT, 'Formulário de login encontrado.\n')

        # Exibe a quantidade total de imagens e os URLs das imagens
        imagens = soup.find_all('img')
        txt.insert(INSERT, f'\nTotal de imagens encontradas: {len(imagens)}\n')
        for img in imagens:
            txt.insert(INSERT, f'URL da imagem: {urljoin(url, img["src"])}\n')

        # Exibe links externos
        links_externos = set()
        for link in soup.find_all('a', href=True):
            link_absoluto = urljoin(url, link['href'])
            if urlparse(link_absoluto).netloc != urlparse(url).netloc:
                links_externos.add(link_absoluto)
        if links_externos:
            txt.insert(INSERT, '\nLinks externos encontrados:\n')
            for link in links_externos:
                txt.insert(INSERT, f'{link}\n')

    except requests.exceptions.RequestException as e:
        txt.insert(INSERT, f'Erro ao acessar a URL: {e}\n')


def verificar_portas_abertas(url):
    # Obtem o nome do host a partir da URL
    host = urlparse(url).hostname

    # Lista de portas para verificar
    portas_alvo = [80, 443, 8080]

    # Tenta se conectar a cada porta
    for porta in portas_alvo:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1)

            resultado = s.connect_ex((host, porta))

            if resultado == 0:
                txt.insert(INSERT, f'A porta {porta} está aberta\n')
            else:
                txt.insert(INSERT, f'A porta {porta} está fechada\n')

            s.close()

        except Exception as ex:
            txt.insert(INSERT, f'Erro ao verificar a porta {porta}: {ex}\n')

# Função para limpar os resultados na área de texto
def impar_resultados():
    txt.delete('1.0', END)


# Cria a janela principal
janela = Tk()

# Configura a janela
janela.title('Ferramenta de Varredura de Sites')
janela.geometry('800x600')

# Cria um rótulo para a entrada da URL
lbl1 = Label(janela, text='Insira a URL do site a ser verificado:')
lbl1.grid(row=0, column=0, padx=10, pady=10)

# Cria uma entrada para a URL do site
entry = Entry(janela, width=40)
entry.grid(row=0, column=1, padx=10, pady=10)

# Cria um botão para iniciar a varredura
btn_executar = Button(janela, text='Executar', command=executar_varredura)
btn_executar.grid(row=0, column=2, padx=10, pady=10)

# Cria um botão para limpar os resultados
btn_limpar = Button(janela, text='Limpar Resultados', command=limpar_resultados)
btn_limpar.grid(row=0, column=3, padx=10, pady=10)

# Cria uma área de texto para exibir os resultados
txt = scrolledtext.ScrolledText(janela, wrap=WORD)
txt.grid(row=1, column=0, columnspan=4, padx=10, pady=10)

# Loop principal da janela
janela.mainloop()