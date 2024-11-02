#!/usr/bin/python3
#coded by gabriel

import hashlib
import os
import binascii
import requests
import ecdsa
import base58
import PySimpleGUI as sg
from json import (load as jsonload, dump as jsondump)
from os import path
import json

def gerar_chave_privada():
    return binascii.hexlify(os.urandom(32)).decode('utf-8')

def chave_privada_para_WIF(chave_privada):
    var80 = "80" + str(chave_privada) 
    var = hashlib.sha256(binascii.unhexlify(hashlib.sha256(binascii.unhexlify(var80)).hexdigest())).hexdigest()
    return str(base58.b58encode(binascii.unhexlify(str(var80) + str(var[0:8]))), 'utf-8')

def chave_privada_para_chave_publica(chave_privada):
    assinatura = ecdsa.SigningKey.from_string(binascii.unhexlify(chave_privada), curve=ecdsa.SECP256k1)
    return ('04' + binascii.hexlify(assinatura.verifying_key.to_string()).decode('utf-8'))

def chave_publica_para_endereco(chave_publica):
    alfabeto = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    contagem = 0
    val = 0
    var = hashlib.new('ripemd160')
    var.update(hashlib.sha256(binascii.unhexlify(chave_publica.encode())).digest())
    doublehash = hashlib.sha256(hashlib.sha256(binascii.unhexlify(('00' + var.hexdigest()).encode())).digest()).hexdigest()
    endereco = '00' + var.hexdigest() + doublehash[0:8]
    
    for char in endereco:
        if (char != '0'):
            break
        contagem += 1
    contagem = contagem // 2
    n = int(endereco, 16)
    saida = []
    while (n > 0):
        n, resto = divmod(n, 58)
        saida.append(alfabeto[resto])
    while (val < contagem):
        saida.append(alfabeto[0])
        val += 1
    return ''.join(saida[::-1])

def obter_saldo(endereco):
    try:
        resposta = requests.get("https://api.blockcypher.com/v1/btc/main/addrs/" + str(endereco) + "/balance")
        return float(resposta.json()['balance']) 
    except:
        return -1

ARQUIVO_CONFIG = path.join(path.dirname(__file__), r'configuracao.cfg')
CONFIGURACAO_PADRAO = {'tema': sg.theme()}
CHAVES_CONFIGURACAO_PARA_ELEMENTOS = {'tema': '-TEMA-'}

def carregar_configuracao(arquivo_config, configuracao_padrao):
    try:
        with open(arquivo_config, 'r') as f:
            configuracao = jsonload(f)
    except Exception as e:
        sg.popup_quick_message(f'Exceção {e}', 'Arquivo de configuração não encontrado... criando um novo', keep_on_top=True, background_color='red', text_color='white')
        configuracao = configuracao_padrao
        salvar_configuracao(arquivo_config, configuracao, None)
    return configuracao

def salvar_configuracao(arquivo_config, configuracao, valores):
    if valores:      
        for chave in CHAVES_CONFIGURACAO_PARA_ELEMENTOS:  
            try:
                configuracao[chave] = valores[CHAVES_CONFIGURACAO_PARA_ELEMENTOS[chave]]
            except Exception as e:
                print(f'Problema ao atualizar a configuração a partir dos valores da janela. Chave = {chave}')

    with open(arquivo_config, 'w') as f:
        jsondump(configuracao, f)

    sg.popup('Configuração salva')

def criar_janela_configuracao(configuracao):
    sg.theme(configuracao['tema'])

    def RotuloTexto(texto): return sg.Text(texto+':', justification='r', size=(15,1))

    layout = [  [sg.Text('Configuração', font='Any 15')],
                [RotuloTexto('Tema'), sg.Combo(sg.theme_list(), size=(20, 20), key='-TEMA-')],
                [sg.Button('Salvar'), sg.Button('Sair')]  ]

    janela = sg.Window('Configuração', layout, keep_on_top=True, finalize=True)

    for chave in CHAVES_CONFIGURACAO_PARA_ELEMENTOS:
        try:
            janela[CHAVES_CONFIGURACAO_PARA_ELEMENTOS[chave]].update(value=configuracao[chave])
        except Exception as e:
            print(f'Problema ao atualizar a janela PySimpleGUI a partir da configuração. Chave = {chave}')

    return janela

def criar_janela_principal(configuracao):
    sg.theme(configuracao['tema'])

    menu_def = [['&Menu', ['&Configuração', 'S&air']]]

    layout = [[sg.Menu(menu_def)],
              [sg.Text('Número de endereços testados até agora ... ', size=(30,1), font=('Comic sans ms', 10)),
               sg.Text('', size=(30,1), font=('Comic sans ms', 10), key='_TENTATIVAS_')],
              [sg.Text('Número de saldos positivos ... ', size=(30,1), font=('Comic sans ms', 10)),
               sg.Text('', size=(30,1), font=('Comic sans ms', 10), key='_SUCESSOS_')],
              [sg.Text('')],
              [sg.Output(size=(87, 20), font=('Comic sans ms', 8), key='out')],
              [sg.Button('Iniciar/Parar', font=('Comic sans ms', 10))]]

    return sg.Window('BTC Hack v2',
                     layout=layout,
                     default_element_size=(9,1))

def main():
    janela, configuracao = None, carregar_configuracao(ARQUIVO_CONFIG, CONFIGURACAO_PADRAO)
    processo = False
    tentativas = 0
    sucessos = 0
    while True:
        if janela is None:
            janela = criar_janela_principal(configuracao)
        evento, valores = janela.Read(timeout=10)
        janela.Element('_TENTATIVAS_').Update(str(tentativas))
        janela.Element('_SUCESSOS_').Update(str(sucessos))
        if evento in (None, 'Sair'):
            break
        elif evento == 'Iniciar/Parar':
            processo = not processo
            tentativas += 1
        if processo:
            chave_privada = gerar_chave_privada()
            chave_publica = chave_privada_para_chave_publica(chave_privada)
            endereco = chave_publica_para_endereco(chave_publica)
            dados = (chave_privada, endereco)
            saldo = obter_saldo(dados[1])
            tentativas += 1
            chave_privada = dados[0]
            endereco = dados[1]
            if (saldo == 0.00000000):
                print("Endereço: " + "{:<34}".format(str(endereco)) + "\n" +
                      "Chave privada: " + str(chave_privada) + "\n" +
                      "Chave privada WIF: " + str(chave_privada_para_WIF(chave_privada)) + "\n" +
                      "Chave pública: " + str(chave_privada_para_chave_publica(chave_privada)).upper() + "\n" +
                      "Saldo: " + str(saldo) + "\n\n")
            elif (saldo > 0.00000000):
                sucessos += 1
                with open("encontrados.txt", "a") as arquivo:
                    arquivo.write("Endereço: " + str(endereco) + "\n" +
                                  "Chave privada: " + str(chave_privada) + "\n" +
                                  "Chave privada WIF: " + str(chave_privada_para_WIF(chave_privada)) + "\n" +
                                  "Chave pública: " + str(chave_privada_para_chave_publica(chave_privada)).upper() + "\n" +
                                  "Saldo: " + str(saldo) + "\n\n")
                print("Endereço: " + "{:<34}".format(str(endereco)) + "\n" +
                      "Chave privada: " + str(chave_privada) + "\n" +
                      "Chave privada WIF: " + str(chave_privada_para_WIF(chave_privada)) + "\n" +
                      "Chave pública: " + str(chave_privada_para_chave_publica(chave_privada)).upper() + "\n" +
                      "Saldo: " + str(saldo) + "\n\n")
            
        elif evento == 'Configuração':
            evento, valores = criar_janela_configuracao(configuracao).read(close=True)
            if evento == 'Salvar':
                janela.close()
                janela = None
                salvar_configuracao(ARQUIVO_CONFIG, configuracao, valores)

    janela.Close()
    
main()
