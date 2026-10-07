# Bruno Souza — histórico eleitoral e metodologia

Fotografia dos dados consultados em **07/10/2026**, no fuso America/Sao_Paulo. O dashboard é estático: uma nova consulta exige baixar e conferir as fontes novamente.

## Identidade e universo pesquisado

Bruno André de Souza, nascido em 20/08/1984, identificado por nome completo (normalizado apenas quanto a acentos/caixa), data de nascimento e sequencial do registro oficial TSE. Não confundido com homônimos ou com outros candidatos de nome Bruno.

Foram examinados os arquivos de candidaturas de Santa Catarina de todos os anos pares de 2004 a 2026. Foram encontradas cinco candidaturas: 2012, 2016, 2018, 2022 e 2026. Nenhuma correspondência nos arquivos SC de 2004, 2006, 2008, 2010, 2014, 2020 e 2024. A ausência nesses arquivos não equivale a certidão nacional de inexistência de registro, nem a uma busca em todos os arquivos de eleições suplementares.

| Ano | Cargo | Partido | Número | Votos | Resultado no registro oficial |
|---|---|---|---|---:|---|
| 2012 | Vereador de Florianópolis | PSD | 55500 | 1.491 | Suplente |
| 2016 | Vereador de Florianópolis | PSB | 40030 | 3.326 | Eleito por QP |
| 2018 | Deputado estadual de SC | PSB | 40030 | 32.512 | Eleito por QP |
| 2022 | Deputado federal de SC | NOVO | 3020 | 86.568 | Suplente |
| 2026 | Deputado estadual de SC | PL | 22722 | 40.327 | Eleito por QP |

Fonte: arquivos `consulta_cand`, `votacao_candidato_munzona` do TSE e, em 2026, resultado unificado oficial. O manifesto `fontes.json` possui links, membros extraídos, datas de consulta e hashes dos arquivos originais utilizados. Cada eleição também conserva a data de geração da fonte em `sourceUpdatedAt`.

Em 2026, o arquivo oficial de 04/10/2026, 21:56:42, informa totalização final (`and=f`) e 17.326 de 17.326 seções totalizadas. Não se apresenta dado parcial como consolidado. Totalização final é a situação da fotografia consultada; não impede revisão judicial posterior.

## Totais e denominadores

1. Votos do candidato: votos nominais válidos, somados por município/zona no cargo e primeiro turno correspondentes. Em 2026: campo `vap`, com destinação “Válido”.
2. Válidos locais: votos nominais válidos + total de votos de legenda válidos (incluindo conversões de nominais em legenda).
3. Participação local = votos do candidato / válidos locais × 100.
4. Contribuição ao total = votos do candidato no território / total da candidatura na circunscrição × 100. Em cards de bairros, a contribuição à capital é identificada separadamente.
5. Comparecimento = comparecentes / eleitorado. Taxa de válidos = válidos do cargo / comparecimento. Votos brancos, nulos, anulados e anulados sub judice não entram nos válidos.
6. Nulos técnicos são incluídos no total de nulos oficial; não são somados novamente.

**Particularidade de 2012:** `QT_TOTAL_VOTOS_VALIDOS` repete os votos nominais (220.003), enquanto os componentes e a base partidária registram também 16.537 votos de legenda. O denominador correto adotado é 236.540 = 220.003 + 16.537, que reconcilia com comparecimento, brancos e nulos. A diferença do campo histórico está preservada na auditoria (`legacyTotalFieldDifference`).

**Particularidade de 2026:** `pvapn` publicado pelo TSE é baseado em `vvc` (votos concorrentes, incluindo sub judice). Este painel usa `vv` (válidos, nominal + legenda). Por isso percentuais com mais casas podem diferir do campo percentual do site TSE.

## Agregação por bairro em Florianópolis

Indicador: **votos por bairro do local de votação**. Não é bairro de residência do eleitor.

Chave de correspondência: ano/eleição + primeiro turno + código de município TSE 81051 + zona + seção. Cada pleito usa seu próprio arquivo `eleitorado_local_votacao_ANO`, nunca o cadastro atual para classificar votos antigos.

Os arquivos de 2012/2016 foram gerados retrospectivamente em 15/04/2024; 2018, em 13/05/2024; 2022, em 30/09/2024. O atributo AA_ELEICAO e a data do pleito definem a eleição a que se refere cada registro. A geração retrospectiva não é confundida com a data da eleição nem prova precisão histórica das coordenadas.

Os votos de 2012–2022 vêm de `votacao_secao` oficial. O formato legado de 2012 não tem cabeçalho e é tratado separadamente pelo extrator. Em 2026, os 1.207 boletins principais de Florianópolis foram decodificados de arquivos oficiais, conferindo SHA-256, fase oficial, município, zona, seção e cargo. As seções agregadas entram somente no resultado da seção principal, sem duplicação.

Se o código do local no resultado difere do cadastro retrospectivo, busca-se o código original em outros registros do próprio arquivo do ano. A classificação só é recuperada quando a correspondência de bairro é inequívoca. Sem essa correspondência, os votos ficam em **Não classificado**. O dashboard não atribui o bairro atual ao local antigo.

Foram registradas 8 divergências de códigos entre resultado e cadastro em 2022, e 20 em 2026. O arquivo de auditoria informa a resolução por seção. Os nomes do cadastro são mantidos sem fundir bairros por interpretação; para pareamento em comparações, normalizam-se apenas caixa e acentos.

## Conferências e cobertura

| Ano | Votos de Bruno na capital | Seções com resultado | Diferença de votos bairros × capital | Cobertura de classificação por votos | Não classificados | Diferença reconstruída dos válidos por seção |
|---|---:|---:|---:|---:|---:|---:|
| 2012 | 1.491 | 861 | 0 | 100,00% | 0 | −495 |
| 2016 | 3.326 | 981 | 0 | 100,00% | 0 | 0 |
| 2018 | 13.198 | 1.000 | 0 | 100,00% | 0 | −368 |
| 2022 | 23.914 | 1.102 | 0 | 99,59% | 99 | 0 |
| 2026 | 18.267 | 1.207 | 0 | 98,72% | 233 | 0 |

Os totais municipais são extraídos da base oficial TSE e agregados na circunscrição. Em 2026, a soma de 295 municípios foi conferida também contra um arquivo de totalização estadual independente, em todos os indicadores (não apenas o candidato). Para 2012–2022, o total estadual/municipal é a agregação da base oficial por zona; a conferência independente por seção foi feita em Florianópolis. Não se apresenta essa soma histórica como uma conferência com um segundo arquivo estadual independente.

Nas cinco eleições, votos por seção → local → bairro → Florianópolis coincidem exatamente. A soma inclui registros não classificados. Há verificação de chaves únicas e da correspondência de todos os municípios estaduais com a malha IBGE.

**Percentuais por bairro/local em 2012 e 2018 ficam indisponíveis.** Em 2012, a destinação de 495 votos de outra candidatura não pode ser reconstruída com segurança a partir das fotografias consultadas; em 2018, a diferença de 368 votos corresponde ao total de conversões em legenda que não pôde ser atribuído com segurança às seções. Não se distribuem essas diferenças proporcionalmente. As participações municipais continuam disponíveis, pois os denominadores municipais oficiais estão reconciliados. Em 2016, a consulta de candidatura confirma os 1.419 votos convertidos em legenda da candidatura 31111; em 2022, os 15 votos de legenda anulados da sigla 29 são excluídos.

Nos arquivos por seção, `validVotesVerified` informa se o denominador foi reconciliado. Denominadores não verificados são `null`; a reconstrução fica em campo explicitamente identificado. Nulos brutos de seções históricas não são confundidos com os totais finais revisados.

## Cartografia

Malha municipal oficial: API de malhas do IBGE, UF 42, formato GeoJSON, qualidade intermediária, consultada em 07/10/2026. Código IBGE ligado ao código TSE por configuração oficial de municípios. A mesma malha atual é usada nas comparações; não se afirma que os polígonos reproduzem cada versão histórica dos limites.

Não foi validada uma delimitação oficial dos bairros de Florianópolis compatível com cada eleição. Por isso o mapa de bairros apresenta **pontos dos locais de votação e tabela de agregação**, sem criar polígonos ou interpolar votos por área. Coordenadas vêm apenas do arquivo TSE do respectivo ano. Valores sentinela, ausentes ou fora da faixa geográfica de verificação são omitidos. A posição histórica exata não é garantida pelas bases retrospectivas.

A cor representa faixas fixas (votos ou percentual local), iguais nos dois mapas comparativos. Branco representa zero; hachura, dado ausente; cinza liso, território fora do filtro ou não aplicável. Votações para vereador não se aplicam a municípios diferentes de Florianópolis. Nos mapas de locais, tamanho do ponto também diferencia volume; nomes e valores exatos aparecem ao passar o cursor/tocar ou na tabela.

Grande Florianópolis é um **recorte operacional explícito de 9 municípios**, constante ao longo da série: Águas Mornas, Antônio Carlos, Biguaçu, Florianópolis, Governador Celso Ramos, Palhoça, Santo Amaro da Imperatriz, São José e São Pedro de Alcântara. Não se afirma equivalência com todas as definições legais ou estatísticas da região metropolitana. A capital integra esse conjunto; as linhas não devem ser somadas quando ele estiver apresentado inteiro.

## Evolução e interpretação

Crescimento absoluto = votos finais − iniciais. Crescimento percentual = (finais / iniciais − 1) × 100. Não se divide por base zero. Variação de participação é medida em pontos percentuais, com o denominador do mesmo cargo e território em cada ano.

Prioridade: vereador 2012 × 2016 e deputado estadual 2018 × 2026. Em comparações entre cargos, usa-se recorte territorial comum; quando houver vereador, limita-se à capital. Bases iniciais inferiores a 100 votos são sinalizadas. Bairros com nomes iguais não são automaticamente territórios historicamente equivalentes; composição de locais, nomes e endereços são comparados e eventuais diferenças sinalizadas. O arquivo `mudancas-cadastrais.json` documenta diferenças; não prova uma mudança física quando apenas o nome mudou.

Concentração top 5/10 usa o total do filtro ativo. Quantidade para 50%/80% usa a menor quantidade de territórios, ordenados por votos, que atinge o limiar. Município com votação significa votos > 0; zero é mantido e não confundido com ausência.

Mudanças agregadas não demonstram fidelidade, transferência individual de votos nem causalidade. Crescimento de votos entre cargos não é evidência suficiente de crescimento proporcional do apoio.

## Cenários

Resultados históricos são observados; cenários são simulações condicionais. Fórmula: eleitorado × comparecimento/100 × proporção de válidos/100 × participação do candidato/100. Cada premissa é editável em cada cenário. A referência é a eleição/território selecionados; busca textual não altera a circunscrição da simulação.

Inicialmente são usados 80%, 100% e 120% da participação observada. Esses fatores são escolhas ilustrativas, não intervalos de confiança ou probabilidades. A análise de sensibilidade mantém as demais premissas do cenário intermediário e varia apenas a participação. Não há estimativa de cadeiras, vitória ou desempenho partidário.

## Arquivos e reprodução

- `base-tratada.json`: base utilizada pela interface, inclusive geometria e fontes.
- `municipalities.csv`, `neighborhoods.csv`, `locations.csv`: tabelas completas, UTF-8 com BOM, separador ponto e vírgula. Campos vazios são ausentes/não aplicáveis; zero é valor observado.
- `secoes.json`: seção, local, bairro atribuído, votos e rastreabilidade.
- `auditoria.json`: cobertura, divergências, localizações e reconciliações.
- `fontes.json`: URLs, datas, SHA-256 dos membros originais do TSE.
- `mudancas-cadastrais.json`: diferenças de cadastro entre pares de eleições.
- Pasta `scripts`: coleta parcial dos ZIPs oficiais, redução de insumos, decodificação dos boletins, agregação e validação.
- Pasta `research`: insumos públicos preservados em JSON compactado e fotografias oficiais. `build_data.py` lê JSON normal ou `.json.gz`.

Executar `python3 scripts/build_data.py` e `python3 scripts/validate.py` na pasta do projeto. Para renovar os dados, baixar novamente as fontes usando `fetch_official.py`, preparar os insumos históricos e partidários, atualizar os arquivos unificados e boletins de 2026, executar a agregação e revisar a auditoria antes de publicar. Os hashes preservam a fotografia desta entrega; uma atualização das fontes pode alterar os resultados e requer nova validação.
