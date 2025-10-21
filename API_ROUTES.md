# Rotas da API - QualiCam

## Diferença entre Clientes

### Cliente Existente
- **Rotas**: `/chapas`, `/retalhos`, `/health`, etc.
- **Propósito**: Sistema de controle de estoque existente
- **Estrutura**: Usa campos como `id_chapa`, `area_disponivel`, `preco_compra_m2`

### App QualiCam
- **Rotas**: `/app/chapas`, `/app/retalhos`, `/app/health`, etc.
- **Propósito**: App móvel para escaneamento de QR Code
- **Estrutura**: Usa campos como `id`, `tamanho`, `preco`, `nomeMaterial`

## Rotas Específicas do App QualiCam

### 1. Verificação de Saúde
```
GET /app/health
```
**Resposta:**
```json
{
  "status": "ok",
  "message": "Servidor QualiCam funcionando"
}
```

### 2. Buscar Chapa por ID
```
GET /app/chapas/{id}
```
**Resposta:**
```json
{
  "id": "12345",
  "nomeMaterial": "Mármore Branco",
  "fornecedor": "Fornecedor ABC",
  "tamanho": 2.5,
  "preco": 150.00,
  "localizacao": "Prateleira A1"
}
```

### 3. Criar Nova Chapa
```
POST /app/chapas
```
**Body:**
```json
{
  "id": "12345",
  "nomeMaterial": "Mármore Branco",
  "fornecedor": "Fornecedor ABC",
  "tamanho": 2.5,
  "preco": 150.00,
  "localizacao": "Prateleira A1"
}
```

### 4. Atualizar Chapa
```
PUT /app/chapas/{id}
```
**Body:**
```json
{
  "nomeMaterial": "Mármore Branco",
  "fornecedor": "Fornecedor ABC",
  "tamanho": 2.0,
  "preco": 160.00,
  "localizacao": "Prateleira B2"
}
```

### 5. Remover Chapa
```
DELETE /app/chapas/{id}
```

### 6. Criar Retalho
```
POST /app/retalhos
```
**Body:**
```json
{
  "id": "12345",
  "nomeMaterial": "Mármore Branco",
  "fornecedor": "Fornecedor ABC",
  "tamanho": 1.0,
  "preco": 150.00,
  "localizacao": "Área Retalhos"
}
```

### 7. Listar Chapas
```
GET /app/chapas
```

### 8. Listar Retalhos
```
GET /app/retalhos
```

## Mapeamento de Campos

| App QualiCam | Banco de Dados | Descrição |
|--------------|----------------|-----------|
| `id` | `id_chapa` | ID único da chapa |
| `nomeMaterial` | `nome_material` | Nome do material |
| `fornecedor` | `fornecedor` | Fornecedor |
| `tamanho` | `area_disponivel` | Tamanho em m² |
| `preco` | `preco_compra_m2` | Preço por m² |
| `localizacao` | `localizacao` | Localização física |

## Códigos de Status HTTP

- `200` - Sucesso
- `201` - Criado com sucesso
- `400` - Dados inválidos
- `404` - Não encontrado
- `409` - Conflito (já existe)
- `500` - Erro interno do servidor

