# Catálogo de regras — fluxo de importação (demonstração)

> **Gerado automaticamente a partir de `regras.py`.** O catálogo é a mesma coisa que o motor executa — não há manutenção paralela, logo não há divergência possível entre o que se documenta e o que se aplica.

Cada regra tem: um identificador, um enunciado, a norma que a sustenta, a vigência dessa norma, e o que a regra **decide**. O motor devolve, por operação, a decisão e a norma que a sustenta.

| Regra | Pergunta que responde | Norma | Estado da norma | O que decide |
|---|---|---|---|---|
| **R01** | Qual documento de registo é válido nesta data | PC-165-2024; CRONO-DI-2026 | `PC-165-2024` vigente desde 2024-09-19 · `CRONO-DI-2026` vigente desde 2026-11-13 | ver `r01_documento_obrigatorio` |
| **R02** | É permitido registar a declaração antes da chegada da carga | PC-165-2024 | `PC-165-2024` vigente desde 2024-09-19 | ver `r02_antecipacao` |
| **R03** | Prazo de saída da mercadoria registada antecipadamente | PC-165-2024 | `PC-165-2024` vigente desde 2024-09-19 | ver `r03_prazo_saida` |
| **R04** | Retificação da declaração e o seu efeito sobre o desembaraço | IN-680-2006 | `IN-680-2006` vigente desde 2006-10-02 | ver `r04_retificacao` |
| **R05** | Requisitos de efectividade do registo | PC-77-2018 | `PC-77-2018` **revogada** em 2024-09-19 por Portaria Coana nº 165/2024 | ver `r05_effectividade_do_registro` |
| **R06** | A NCM escolhida vigia na data do registo | GECEX-272-2021 | `GECEX-272-2021` vigente desde 2021-11-19 | ver `r06_classificacao_fiscal` |
| **R07** | Layout do documento fiscal de IBS/CBS na importação | AC-4-2026 | `AC-4-2026` vigente desde 2026-07-30 | ver `r07_layout_fiscal_cbs_ibs` |
| **R08** | A norma de referência da regra ainda está vigente | PC-77-2018 / PC-165-2024 | `PC-77-2018` **revogada** em 2024-09-19 por Portaria Coana nº 165/2024 · `PC-165-2024` vigente desde 2024-09-19 | ver `r08_norma_de_referencia_desatualizada` |

## As decisões que o motor sabe tomar

| Resultado | Significado |
|---|---|
| `BLOQUEIA` | a operação não pode prosseguir nestas condições |
| `REVISAR` | há excepção ou hipótese que o motor não decide sozinho — e isso é declarado, não escondido |
| `PERMITE` | a regra está satisfeita |

## Normas usadas (todas verificadas na fonte)

| Norma | Publicada | Vigência | Fonte |
|---|---|---|---|
| `PC-77-2018` — Portaria Coana nº 77/2018 — DUIMP (projeto-piloto do NPI) | 2018-09-26 | revogada em 2024-09-19 por Portaria Coana nº 165/2024 | [http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=95195](http://normas.receita.fazenda.gov.br/sijut2consulta/link.action?idAto=95195) |
| `PC-165-2024` — Portaria Coana nº 165/2024 — registo da Duimp e cronograma de obrigatoriedade | 2024-09-19 | vigente desde 2024-09-19 | [https://www.gov.br/siscomex/pt-br/legislacao/receita-federal](https://www.gov.br/siscomex/pt-br/legislacao/receita-federal) |
| `PC-70-2022` — Portaria Coana nº 70/2022 — despacho antecipado e retificação após a chegada | 2022-03-31 | vigente desde 2022-03-31 | [https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/despacho-de-importacao/topicos-1/conceitos-e-definicoes/despacho-de-importacao/Introducao](https://www.gov.br/receitafederal/pt-br/assuntos/aduana-e-comercio-exterior/manuais/despacho-de-importacao/topicos-1/conceitos-e-definicoes/despacho-de-importacao/Introducao) |
| `IN-680-2006` — Instrução Normativa SRF nº 680/2006 — despacho aduaneiro de importação | 2006-10-02 | vigente desde 2006-10-02 | [https://www.gov.br/receitafederal/pt-br/assuntos/aduana/todos-os-servicos-aduaneiros](https://www.gov.br/receitafederal/pt-br/assuntos/aduana/todos-os-servicos-aduaneiros) |
| `SIS-020-2026` — Comunicado Siscomex Importação nº 020/2026 — cronograma de desligamento da DI | 2026-01-01 | vigente desde 2026-01-01 | [https://www.gov.br/siscomex/pt-br/noticias/noticias-siscomex-importacao/Comunicados/importacao-no-2026-020/](https://www.gov.br/siscomex/pt-br/noticias/noticias-siscomex-importacao/Comunicados/importacao-no-2026-020/) |
| `CRONO-DI-2026` — Cronograma de desligamento de DI e DSI-e (v30, 13/11/2026) — desligamento final em 10/12/2026 | 2026-11-13 | vigente desde 2026-11-13 | [https://www.gov.br/siscomex/pt-br/programa-portal-unico/cronograma-de-desligamento-di](https://www.gov.br/siscomex/pt-br/programa-portal-unico/cronograma-de-desligamento-di) |
| `AC-4-2026` — Ato Conjunto RFB/CGIBS nº 4/2026 — documentos fiscais de IBS e CBS na importação | 2026-07-30 | vigente desde 2026-07-30 | [https://cgibs.gov.br/atos-tecnicos-conjuntos](https://cgibs.gov.br/atos-tecnicos-conjuntos) |
| `ATC-11-2026` — Ato Técnico Conjunto RFB/SUANA/CGIBS nº 11/2026 — documentação técnica da Duimp | 2026-11-10 | vigente desde 2026-11-12 | [https://cgibs.gov.br/atos-tecnicos-conjuntos](https://cgibs.gov.br/atos-tecnicos-conjuntos) |
| `GECEX-272-2021` — Resolução Gecex nº 272/2021 — Nomenclatura Comum do Mercosul (NCM) e TEC | 2021-11-19 | vigente desde 2021-11-19 | [https://www.gov.br/mdic/pt-br/assuntos/camex/resolucoes/gecex/resolucoes](https://www.gov.br/mdic/pt-br/assuntos/camex/resolucoes/gecex/resolucoes) |

## Por que isto é a demonstração

A vaga de Analista Aduaneiro pede *«proficiência acerca da legislação federal como regra de negócio»*. Isto é exactamente isso: um conjunto de regras versionadas, ligadas a normas com data, testadas nos casos de fronteira, e executadas por código — não por memória.

E tem uma data no fim: **a DI desliga a 10/12/2026**. O documento de registo que toda a cadeia usava muda de nome em 24 dias, e a documentação técnica da Duimp foi aprovada por um Ato Técnico Conjunto de **10/11/2026** — há seis dias. Qualquer operação, base de dados e regra que não accompanies essa mudança quebra em December.

É esse o trabalho que a expansão do Tecon Salvador vai pedir: não 'usar o sistema', mas **fazer a regra virar sistema**, e mudar a regra quando ela muda.
