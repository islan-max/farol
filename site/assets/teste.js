// "Teste agora": roda o ruff (WebAssembly) no navegador. O código digitado nunca sai da página.
import init, { PositionEncoding, Workspace } from "./vendor/ruff/ruff_wasm.js";

const $ = (id) => document.getElementById(id);
const campo = $("codigo");
const status = $("status");
const resultado = $("resultado");

const EXEMPLO = `import os
import json


def adicionar(item, itens=[]):
    itens.append(item)
    return itens


def carregar(caminho):
    password = "abc123"
    try:
        return open(caminho).read()
    except:
        pass


def descricao(x):
    if x == None:
        return f"vazio"
    l = x
    return l
`;

let oficina = null;
let licoes = null;

function avisar(texto, erro = false) {
  status.textContent = texto;
  status.classList.toggle("erro", erro);
}

const pronto = (async () => {
  try {
    const [resposta] = await Promise.all([fetch("licoes.json"), init()]);
    if (!resposta.ok) throw new Error(`licoes.json: ${resposta.status}`);
    licoes = await resposta.json();
    // Mesmas regras do Farol: só as que têm lição escrita.
    oficina = new Workspace(
      { lint: { select: Object.keys(licoes) } },
      PositionEncoding.Utf16,
    );
  } catch (erro) {
    console.error(erro);
    oficina = null;
  }
})();

function agrupar(diagnosticos) {
  const grupos = new Map();
  for (const d of diagnosticos) {
    const sintaxe = d.code === null || d.code === "invalid-syntax";
    if (sintaxe && [...grupos.keys()].some((k) => k === "sintaxe")) continue; // só o primeiro
    const chave = sintaxe ? "sintaxe" : d.code;
    if (!grupos.has(chave)) grupos.set(chave, []);
    grupos.get(chave).push(d);
  }
  return [...grupos.entries()]
    .map(([chave, itens]) => ({ chave, itens: itens.sort((a, b) => a.start_location.row - b.start_location.row) }))
    .sort((a, b) => (a.chave.startsWith("S") ? 0 : 1) - (b.chave.startsWith("S") ? 0 : 1) || a.itens[0].start_location.row - b.itens[0].start_location.row);
}

function el(tag, props = {}, ...filhos) {
  const e = document.createElement(tag);
  Object.assign(e, props);
  e.append(...filhos);
  return e;
}

function cartao(grupo, linhas) {
  const primeiro = grupo.itens[0];
  const lc = licoes[grupo.chave];
  const linhaNum = primeiro.start_location.row;
  const art = el("article", { className: "cartao" });
  art.append(el("p", { className: "onde" }, `Linha ${linhaNum}`));
  art.append(el("pre", { className: "linha-do-usuario", tabIndex: 0 }, linhas[linhaNum - 1] ?? ""));
  if (!lc) {
    art.append(el("h3", {}, grupo.chave === "sintaxe" ? "Erro de sintaxe" : grupo.chave));
    art.append(el("p", {}, `A ferramenta disse (em inglês): ${primeiro.message}`));
    return art;
  }
  const corpo = el("div");
  corpo.innerHTML = lc.html; // HTML gerado no build a partir das lições (texto escapado lá)
  art.append(corpo);
  if (grupo.itens.length > 1) {
    const outras = grupo.itens.slice(1).map((d) => d.start_location.row);
    art.append(el("p", { className: "suave" }, `Também aparece nas linhas: ${outras.join(", ")}.`));
  }
  return art;
}

async function revisar() {
  const texto = campo.value;
  if (!texto.trim()) {
    avisar("Cole um trecho de Python primeiro.", true);
    campo.focus();
    return;
  }
  avisar("Carregando o analisador (cerca de 3 MB, só na primeira vez)…");
  await pronto;
  if (!oficina) {
    avisar(
      "Não consegui carregar o analisador neste navegador. Use a CLI ou a Action: veja “Como usar”.",
      true,
    );
    return;
  }
  const grupos = agrupar(oficina.check(texto));
  const linhas = texto.split("\n");
  resultado.replaceChildren();
  const total = grupos.reduce((n, g) => n + g.itens.length, 0);
  const titulo = el(
    "h2",
    { tabIndex: -1 },
    total === 0
      ? "Nenhum apontamento. Bom trabalho!"
      : `${total} apontamento${total > 1 ? "s" : ""} em ${grupos.length} regra${grupos.length > 1 ? "s" : ""}`,
  );
  resultado.append(titulo);
  if (total > 0) {
    resultado.append(
      el("p", { className: "suave" }, "Num PR de verdade, o Farol comenta só as linhas que você alterou."),
    );
    for (const g of grupos) resultado.append(cartao(g, linhas));
  }
  avisar("");
  titulo.focus();
}

$("revisar").addEventListener("click", revisar);
$("exemplo").addEventListener("click", () => {
  campo.value = EXEMPLO;
  avisar("Exemplo carregado. Agora é só revisar.");
  campo.focus();
});
