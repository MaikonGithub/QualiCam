# QualiCam - Sistema de Controle de Estoque de Marmoraria

Sistema completo para controle de estoque de marmoraria com escaneamento de QR Code.

## Funcionalidades

### Aplicativo Android
- **Tela Inicial**: Configuração de IP/porta do servidor e indicador de conectividade
- **Câmera**: Escaneamento de QR Code para identificação de chapas
- **Adicionar Chapa**: Formulário para cadastro de novas chapas
- **Editar Chapa**: Edição de chapas existentes
- **Transformar em Retalho**: Conversão de chapas para retalhos

### Servidor Python
- API REST para gerenciamento de chapas e retalhos
- Banco de dados SQLite
- Endpoints para CRUD completo

## Instalação e Execução

### Servidor Python

1. Instale as dependências:
```bash
pip install -r requirements.txt
```

2. Execute o servidor:
```bash
python server.py
```

O servidor será executado em `http://0.0.0.0:8000`

### Aplicativo Android

1. Abra o projeto no Android Studio
2. Sincronize as dependências
3. Execute no dispositivo ou emulador

## Configuração

### No Aplicativo
1. Na tela inicial, configure o IP e porta do servidor (ex: `192.168.15.7:5000`)
2. Clique em "Salvar e Testar Conexão"
3. Aguarde a confirmação de conectividade
4. Clique em "Prosseguir para Câmera"

### No Servidor
- O servidor deve estar rodando na mesma rede local
- Use o IP da máquina onde o servidor está executando
- Porta padrão: 5000

## Fluxo de Uso

1. **Configuração**: Configure o IP do servidor na tela inicial
2. **Escaneamento**: Aponte a câmera para o QR Code da chapa
3. **Verificação**: O sistema verifica se a chapa já existe
4. **Ação**:
   - Se não existe: Abre formulário para adicionar nova chapa
   - Se existe: Abre formulário para editar chapa existente
5. **Transformação**: Opção para transformar chapa em retalho

## Estrutura do Banco de Dados

### Tabela `chapas`
- `id`: ID único da chapa (5 dígitos)
- `nome_material`: Nome do material
- `fornecedor`: Fornecedor
- `tamanho`: Tamanho em m²
- `preco`: Preço por m²
- `localizacao`: Localização física
- `data_criacao`: Data de criação
- `data_atualizacao`: Data da última atualização

### Tabela `retalhos`
- Mesma estrutura da tabela `chapas`
- Chapas transformadas em retalhos são movidas para esta tabela

## API Endpoints

### Rotas do Cliente Existente
- `GET /health` - Verificação de saúde do servidor
- `GET /chapas` - Listar chapas (cliente existente)
- `POST /chapas/adicionar` - Adicionar chapa (cliente existente)
- `POST /chapas/update-area` - Atualizar área da chapa
- `POST /chapas/transformar-retalho` - Transformar em retalho
- `GET /retalhos` - Listar retalhos (cliente existente)
- `GET /chapas/metragem-total` - Metragem total por material

### Rotas Específicas do App QualiCam (prefixo /app)
- `GET /app/health` - Verificação de saúde específica do app
- `GET /app/chapas/{id}` - Buscar chapa por ID
- `POST /app/chapas` - Criar nova chapa
- `PUT /app/chapas/{id}` - Atualizar chapa
- `DELETE /app/chapas/{id}` - Remover chapa
- `POST /app/retalhos` - Criar retalho
- `GET /app/chapas` - Listar todas as chapas
- `GET /app/retalhos` - Listar todos os retalhos

## Tecnologias Utilizadas

### Android
- Kotlin
- Jetpack Compose
- CameraX
- ML Kit (Barcode Scanning)
- Retrofit
- Navigation Compose
- DataStore

### Servidor
- Python
- Flask
- SQLite
- Flask-CORS

