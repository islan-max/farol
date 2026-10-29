// Acessibilidade do site: axe (WCAG 2.2 AA) nos temas claro e escuro, reflow a 200% e teclado.
// Uso: node scripts/build_site.py (via uv) e depois `npm run test:a11y` dentro de site/.
// Localmente: FAROL_BROWSER=msedge. Na CI o Chromium do Playwright é instalado.
import AxeBuilder from "@axe-core/playwright";
import assert from "node:assert/strict";
import { createServer } from "node:http";
import { readdirSync, readFileSync, statSync } from "node:fs";
import { extname, join, normalize, resolve } from "node:path";
import { after, before, describe, test } from "node:test";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";

const RAIZ = resolve(fileURLToPath(new URL("../../_site", import.meta.url)));
const TIPOS = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css",
  ".js": "text/javascript",
  ".json": "application/json",
  ".svg": "image/svg+xml",
  ".wasm": "application/wasm",
  ".woff2": "font/woff2",
  ".xml": "application/xml",
  ".txt": "text/plain",
};
const ESQUEMAS = ["dark", "light"];
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa", "best-practice"];

function paginas(dir = RAIZ, base = "") {
  return readdirSync(dir).flatMap((nome) => {
    const caminho = join(dir, nome);
    if (statSync(caminho).isDirectory()) return nome === "assets" ? [] : paginas(caminho, `${base}${nome}/`);
    return nome.endsWith(".html") ? [`${base}${nome}`] : [];
  });
}

let servidor, origem, navegador;

before(async () => {
  servidor = createServer((req, res) => {
    // O Pages serve o site em /farol/; a página 404 usa caminhos absolutos com esse prefixo.
    const url = new URL(req.url, "http://x").pathname.replace(/^\/farol\//, "/");
    const alvo = normalize(decodeURIComponent(url)).replace(/^[/\\]+/, "");
    const arquivo = join(RAIZ, alvo || "index.html");
    let conteudo;
    try {
      if (!arquivo.startsWith(RAIZ)) throw new Error("fora da raiz");
      conteudo = readFileSync(arquivo);
    } catch {
      res.writeHead(404).end();
      return;
    }
    res.writeHead(200, { "content-type": TIPOS[extname(arquivo)] ?? "application/octet-stream" });
    res.end(conteudo);
  });
  await new Promise((ok) => servidor.listen(0, "127.0.0.1", ok));
  origem = `http://127.0.0.1:${servidor.address().port}`;
  navegador = await chromium.launch({ channel: process.env.FAROL_BROWSER || undefined });
});

after(async () => {
  await navegador?.close();
  servidor?.close();
});

async function abrir(pagina, esquema, largura = 1280) {
  const ctx = await navegador.newContext({ colorScheme: esquema, viewport: { width: largura, height: 900 } });
  const p = await ctx.newPage();
  const erros = [];
  p.on("pageerror", (e) => erros.push(String(e)));
  p.on("console", (m) => m.type() === "error" && erros.push(m.text()));
  await p.goto(`${origem}/${pagina}`);
  return { ctx, p, erros };
}

async function rodarExemplo(p) {
  await p.click("#exemplo");
  await p.click("#revisar");
  await p.waitForSelector("#resultado article", { timeout: 20000 });
}

function resumo(violacoes) {
  return violacoes.map((v) => `${v.id}: ${v.help} (${v.nodes.map((n) => n.target.join(" ")).join(" | ")})`).join("\n");
}

describe("axe, WCAG 2.2 AA", () => {
  for (const esquema of ESQUEMAS) {
    for (const pagina of paginas()) {
      test(`${pagina} (${esquema})`, async () => {
        const { ctx, p, erros } = await abrir(pagina, esquema);
        const r = await new AxeBuilder({ page: p }).withTags(TAGS).analyze();
        await ctx.close();
        assert.equal(r.violations.length, 0, resumo(r.violations));
        assert.deepEqual(erros, [], "erros no console");
      });
    }
    test(`teste.html com resultados (${esquema})`, async () => {
      const { ctx, p } = await abrir("teste.html", esquema);
      await rodarExemplo(p);
      const r = await new AxeBuilder({ page: p }).withTags(TAGS).analyze();
      await ctx.close();
      assert.equal(r.violations.length, 0, resumo(r.violations));
    });
  }
});

describe("reflow (200% de zoom equivale a 640 px; 400%, a 320 px)", () => {
  for (const largura of [640, 320]) {
    for (const pagina of ["index.html", "teste.html", "usar.html", "licoes/index.html", "licoes/E722.html"]) {
      test(`${pagina} sem rolagem horizontal a ${largura}px`, async () => {
        const { ctx, p } = await abrir(pagina, "dark", largura);
        if (pagina === "teste.html") await rodarExemplo(p);
        const [rolagem, janela] = await p.evaluate(() => [document.documentElement.scrollWidth, innerWidth]);
        await ctx.close();
        assert.ok(rolagem <= janela, `scrollWidth ${rolagem} > ${janela}`);
      });
    }
  }
});

describe("teclado", () => {
  test("o primeiro Tab leva ao link 'Pular para o conteúdo', que funciona", async () => {
    const { ctx, p } = await abrir("index.html", "dark");
    await p.keyboard.press("Tab");
    assert.equal(await p.evaluate(() => document.activeElement.textContent), "Pular para o conteúdo");
    await p.keyboard.press("Enter");
    assert.equal(await p.evaluate(() => document.activeElement.id), "conteudo");
    await ctx.close();
  });

  for (const esquema of ESQUEMAS) {
    test(`todo elemento que recebe foco mostra o foco (${esquema})`, async () => {
      const { ctx, p } = await abrir("teste.html", esquema);
      for (let i = 0; i < 12; i++) {
        await p.keyboard.press("Tab");
        const visivel = await p.evaluate(() => {
          const e = document.activeElement;
          if (!e || e === document.body) return null;
          const c = getComputedStyle(e);
          return { nome: e.tagName + (e.id ? `#${e.id}` : ""), ok: c.outlineStyle !== "none" && parseFloat(c.outlineWidth) >= 2 };
        });
        if (visivel) assert.ok(visivel.ok, `${visivel.nome} sem indicador de foco`);
      }
      await ctx.close();
    });
  }

  test("dá para revisar só com o teclado e o foco vai para os resultados", async () => {
    const { ctx, p } = await abrir("teste.html", "dark");
    await p.focus("#codigo");
    await p.keyboard.type("try:\n    x = 1\nexcept:\n    pass\n");
    await p.keyboard.press("Tab"); // Revisar
    assert.equal(await p.evaluate(() => document.activeElement.id), "revisar");
    await p.keyboard.press("Enter");
    await p.waitForSelector("#resultado h2", { timeout: 20000 });
    assert.equal(await p.evaluate(() => document.activeElement.tagName), "H2");
    assert.match(await p.textContent("#resultado h2"), /apontamento/);
    await ctx.close();
  });

  test("campo vazio avisa em vez de falhar em silêncio", async () => {
    const { ctx, p } = await abrir("teste.html", "dark");
    await p.click("#revisar");
    assert.match(await p.textContent("#status"), /Cole um trecho/);
    assert.equal(await p.evaluate(() => document.activeElement.id), "codigo");
    await ctx.close();
  });
});

describe("conteúdo, links e privacidade", () => {
  test("toda página tem idioma, título único, descrição, canonical e um só h1", async () => {
    const titulos = new Set();
    for (const pagina of paginas()) {
      const { ctx, p } = await abrir(pagina, "dark");
      const d = await p.evaluate(() => ({
        lang: document.documentElement.lang,
        titulo: document.title,
        descricao: document.querySelector('meta[name="description"]')?.content ?? "",
        canonical: document.querySelector('link[rel="canonical"]')?.href ?? "",
        h1: document.querySelectorAll("h1").length,
      }));
      await ctx.close();
      assert.equal(d.lang, "pt-BR", pagina);
      assert.ok(d.titulo.length > 5 && !titulos.has(d.titulo), `${pagina}: título vazio ou repetido`);
      titulos.add(d.titulo);
      assert.ok(d.descricao.length >= 30, `${pagina}: descrição curta`);
      assert.ok(d.canonical.startsWith("https://islan-max.github.io/farol/"), `${pagina}: canonical`);
      assert.equal(d.h1, 1, `${pagina}: precisa de exatamente um h1`);
    }
  });

  test("todo link interno aponta para uma página ou arquivo que existe", async () => {
    for (const pagina of paginas().filter((p) => p !== "404.html")) {
      const { ctx, p } = await abrir(pagina, "dark");
      const hrefs = await p.evaluate(() =>
        [...document.querySelectorAll("a[href]")].map((a) => a.href).filter((h) => h.startsWith(location.origin)),
      );
      for (const h of new Set(hrefs)) {
        const resposta = await p.request.get(h.split("#")[0]);
        assert.equal(resposta.status(), 200, `${pagina} → ${h}`);
      }
      await ctx.close();
    }
  });

  test("nenhuma requisição sai do próprio site e não há cookies nem armazenamento", async () => {
    const { ctx, p } = await abrir("index.html", "dark");
    const externas = [];
    p.on("request", (r) => !r.url().startsWith(origem) && externas.push(r.url()));
    await p.goto(`${origem}/teste.html`);
    await rodarExemplo(p);
    const [cookies, local, sessao] = await p.evaluate(() => [document.cookie, localStorage.length, sessionStorage.length]);
    await ctx.close();
    assert.deepEqual(externas, []);
    assert.equal(cookies, "");
    assert.equal(local + sessao, 0);
  });
});
