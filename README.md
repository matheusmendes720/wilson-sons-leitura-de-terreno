# Wilson Sons — Leitura de terreno e proposta de 90 dias

> **Publicado em 27/11/2026 (v1.1):** `https://matheusmendes720.github.io/wilson-sons-leitura-de-terreno/`
> — **13/13 URLs a 200** verificadas. Esta pasta é a cópia local do que está publicado; a v1.1 republica o
> HTML corrigido e regenera os **14 PDFs A4** do zero (ver `anex/LEIA-ME.md` §9).

Site estático, sem JavaScript, sem web fonts e sem pedidos externos. Abre com duplo clique ou
publica directamente no GitHub Pages.

## Publicar no GitHub Pages (2 minutos)

1. Cria um repositório novo (pode ser privado — o GitHub Pages pago serve repositórios privados;
   no plano gratuito o repositório tem de ser público).
2. Carrega o conteúdo desta pasta para a raiz do repositório:

   ```bash
   cd site-wilson-sons
   git init
   git add .
   git commit -m "Leitura de terreno — proposta 90 dias"
   git branch -M main
   git remote add origin https://github.com/<TEU-USUARIO>/<TEU-REPO>.git
   git push -u origin main
   ```

3. No repositório: **Settings → Pages → Source → Deploy from a branch → `main` / `(root)` → Save**.
4. Em 1–2 minutos fica disponível em `https://<TEU-USUARIO>.github.io/<TEU-REPO>/`.

## Estrutura

```
index.html              capa e a história (leitura de 30 s)          — 8 p. A4
para-encaminhar.html    resumo executivo autónomo (reencaminhável)     — 2 p. A4
diagnostico.html        as seis costuras de processo e dados pós-M&A   — 6 p. A4
plano.html              a proposta de 90 dias e o produto              — 5 p. A4
evidencia.html          os dados, os gráficos e os limites             — 6 p. A4
metodo.html             a demonstração: legislação como regra de negócio— 5 p. A4
pdf-impressao/          as mesmas seis páginas, já em A4              (32 folhas)
assets/style.css        folha de estilo (tokens do design system, claro + black)
assets/img/             gráficos e diagramas, pares claro/preto (12 ficheiros)
assets/*.pdf,*.py,*.md  anexo, motor de regras, testes e catálogo
```

## Notas de leitura

- **Três profundidades.** A capa é lida em 30 s; o diagnóstico e a proposta em 3 min; o método e a
  evidência em 15 min. O `para-encaminhar.html` é a página de entrada para quem não te conhece.
- **Tema**: segue a preferência do sistema (claro/preto). Para fixar o preto, acrescenta
  `data-theme="black"` ao `<html>`. As regras escuras só existem em `@media screen` e em
  `html[data-theme="black"]` — **imprimir dá sempre a versão clara**.
- **Impressão**: cada página imprime limpa em A4 (Ctrl/Cmd+P), e o ficheiro `pdf-impressao/` já tem
  as seis em PDF. `para-encaminhar.html` foi feito para ser impresso e reencaminhado.
- **Zero tracking**: não há analytics, nem cookies, nem recursos externos. Quem abrir a página
  vê exactamente o que vês tu.

## O que ficou de fora, e porquê

Três ficheiros de imagem dos materiais anteriores **não** entram neste bundle, de propósito:

| Excluído | Motivo |
|---|---|
| `fig-1-8` (posições de TI por eixos) | contém uma leitura interna sobre a permanência das equipas |
| `02-quadrante-de-cenarios-de-ti` | a mesma leitura interna, noutra forma |
| `03-mapa-de-dominos-e-palavras-chave` | referencia o braço logístico do grupo |

O diagrama de stack e o diagrama do capex foram **regerados sem nomes de pessoas e sem esse
conteúdo** (ver `diagramas_site.py`). As versões originais continuam a existir nos ficheiros de
trabalho, fora do bundle.
