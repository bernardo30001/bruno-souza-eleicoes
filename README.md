# Bruno Souza · Atlas eleitoral

Dashboard em português, responsivo, com cinco candidaturas oficiais (2012, 2016, 2018, 2022 e 2026), mapas municipais, votação por bairro do local de votação em Florianópolis, comparações e cenários condicionais.

## Acesso público

[Abra o dashboard](https://bernardo30001.github.io/bruno-souza-eleicoes/). O site não exige login.

A publicação no GitHub Pages é atualizada automaticamente a cada envio para `main`, após a validação das bases e do JavaScript. A pasta publicada é `dist/`.

## Abrir

Abra `dist/index.html` no navegador. Os dados, a geometria e os scripts são locais; não é preciso instalar bibliotecas ou configurar chaves. Também é possível servir `dist/` com qualquer servidor estático.

## Entregáveis

- `dist/index.html`: dashboard funcional.
- `dist/base-tratada.json`: dados utilizados nas visualizações.
- `dist/municipalities.csv`, `dist/neighborhoods.csv`, `dist/locations.csv`: tabelas completas. A interface também exporta o recorte filtrado.
- `dist/secoes.json`: resultados por seção com vínculo territorial e fonte.
- `dist/fontes.json`: links e hashes das fontes oficiais.
- `dist/metodologia.md`: denominadores, agregações, cobertura, diferenças e limitações.
- `dist/achados.md`: achados efetivamente sustentados pelos dados.
- `dist/auditoria.json`, `dist/mudancas-cadastrais.json`: rastreabilidade das conferências.
- `research/validacao-final.json`: resultado da validação executada.

## Reproduzir a base

Apenas Python 3 e sua biblioteca padrão são necessários:

```sh
python3 scripts/build_data.py
python3 scripts/validate.py
node --check dist/app.js
```

Os insumos reduzidos em `research/inputs/*.json.gz` e os 295 arquivos oficiais de municípios de 2026 em `research/2026-municipios/*.json.gz` preservam a fotografia consultada. O agregador lê JSON ou gzip automaticamente. As fontes completas de TSE continuam disponíveis pelos links e hashes do manifesto, sem conservar vários gigabytes de CSVs de outras candidaturas.

`fetch_official.py tipo:ano` lê o diretório central dos ZIPs oficiais por HTTP Range, extrai o membro de Santa Catarina (ou o cadastro nacional de locais quando não há separação por UF), verifica tamanho e CRC e registra SHA-256. `prepare_inputs.py` reduz os arquivos históricos; `prepare_party.py` preserva evidências partidárias e de destinação. `prepare_2026.py` decodifica boletins já baixados, verificando hashes contra o manifesto. Não executam inferência de votos nem geocodificação.

## Limitações principais

- Percentuais locais por bairro de 2012 e 2018 indisponíveis por denominadores não reconciliados. Os votos de Bruno fecham integralmente.
- 99 votos em 2022 e 233 em 2026 ficam em Não classificado, sem perda no total.
- Pontos do cadastro, sem malha histórica de bairros validada. Coordenadas retrospectivas têm limitação temporal explícita.
- Cenários são condicionais, sem probabilidades, previsão de vitória ou simulação de cadeiras.

Dados consultados em 07/10/2026. Sem atualização automática.
