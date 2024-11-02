
Este projeto é uma ferramenta para gerar chaves privadas de Bitcoin e verificar se essas chaves correspondem a endereços com saldo. Se um endereço com saldo positivo for encontrado, as informações são salvas em um arquivo de texto.

## O que é Bitcoin?

Bitcoin é uma criptomoeda descentralizada que permite transações diretas entre usuários sem a necessidade de intermediários, como bancos. Cada usuário possui uma chave privada, que é essencial para acessar e controlar os Bitcoins em sua carteira.

## Funcionamento do Programa

Este programa utiliza um algoritmo de força bruta que opera da seguinte forma:

1. **Geração de Chaves Privadas**: O programa gera continuamente chaves privadas Bitcoin aleatórias. Essas chaves são representadas como strings hexadecimais de 32 bytes, utilizando a função `os.urandom()` para garantir a segurança criptográfica.

2. **Conversão em Chaves Públicas**: Cada chave privada gerada é convertida em sua respectiva chave pública utilizando o módulo `ecdsa` do Python. A chave pública é fundamental para derivar o endereço Bitcoin.

3. **Geração de Endereços Bitcoin**: A chave pública é então transformada em um endereço Bitcoin usando as bibliotecas `binascii` e `hashlib`. Esse endereço é o que pode ser compartilhado com outros usuários para receber pagamentos.

4. **Verificação de Saldo**: O programa consulta um serviço de API online para verificar se o endereço gerado possui algum saldo. Se um endereço com saldo for encontrado, o programa registra a chave privada, a chave pública e o endereço no arquivo `encontrados.txt` no disco rígido do usuário.

### Considerações sobre Chaves Privadas

Uma chave privada é um número secreto que permite o gasto de Bitcoins. Se uma carteira possui Bitcoins, a chave privada correspondente concede controle total sobre essa carteira, permitindo que o proprietário utilize o saldo disponível. Devido à natureza aleatória das chaves privadas, não é possível saber quais chaves estão associadas a carteiras com saldo e quais estão vazias. Portanto, o programa tenta encontrar chaves privadas que se correlacionem a carteiras com saldo positivo, explorando aleatoriamente as possibilidades.

## Pré-requisitos

Para rodar o código, você precisará ter o seguinte:

- **Python 3**: Certifique-se de que o Python 3 esteja instalado em sua máquina.
- **Bibliotecas Necessárias**: O código utiliza algumas bibliotecas que podem ser instaladas via pip.
- Recomendo rodar em uma VPS.

## Instalação

1. **Clone o repositório**:
   ```bash
   git clone git@github.com:BrzGab/Bitcoin-Brute-Force.git
   cd Bitcoin-Brute-Force
   pip3 install -r requirements.txt
   python3 btc-bruteforce-v1.py
