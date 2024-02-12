# SORTBOT

## Bot para sorteios no instagram

### PRÉ REQUISITOS
- [Python](https://www.python.org/downloads/)

### COMO FUNCIONA
O bot vai na postagem do sorteio, curti o post (se especificado), segue as pessoas com os
usuários passados no arquivo "to_follow.txt", e faz uma determinada % de comentários. É realizado
1 comentário de 2 a 4 minutos mencionando um numero determinado de amigos.

### COMO USAR

1. Clone este repositório
   ```bash
   git clone https://github.com/LeandroDeJesus-S/sortbot.git
   ```
2. Vá para o diretório
   ```bash
   cd sortbot
   ```
3. Instale as dependências
   ```bash
   pip install -r requirements.txt
   ```
4. Crie um arquivo chamado 'to_follow.txt' e coloque o nome de usuário (sem @) das pessoas, um por linha.
   ```txt
   usuario1
   usuario2
   ...
   ```

5. Execute o arquivo sortbot.py
   ```bash
   python sortbot.py
   ```
6. Preencha as informações pedidas na interface gráfica e clique no botão "Pronto"
