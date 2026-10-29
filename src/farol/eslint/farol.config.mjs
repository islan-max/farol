// Regras fixas do Farol para JavaScript e TypeScript. O ESLint do repositório revisado é ignorado:
// o Farol decide as regras. Só entram regras que têm lição escrita em src/farol/licoes/javascript.
import tseslint from "typescript-eslint";

// Variáveis e imports sobrando, sim; parâmetros não (callbacks como (req, res, next) são normais),
// e nomes começando com "_" são "não usado de propósito".
const naoUsadas = { args: "none", varsIgnorePattern: "^_", caughtErrorsIgnorePattern: "^_" };

const regras = {
  eqeqeq: ["error", "always"],
  "no-var": "error",
  "no-eval": "error",
  "no-empty": "error",
  "prefer-const": "error",
  "no-dupe-keys": "error",
  "no-fallthrough": "error",
  "no-unreachable": "error",
};

export default [
  {
    files: ["**/*.{js,mjs,cjs,jsx}"],
    languageOptions: { ecmaVersion: "latest", sourceType: "module", parserOptions: { ecmaFeatures: { jsx: true } } },
    rules: { ...regras, "no-unused-vars": ["error", naoUsadas] },
  },
  {
    // Só o parser e regras sem informação de tipo: não precisa de tsconfig e nada é executado.
    files: ["**/*.{ts,tsx,mts,cts}"],
    languageOptions: { parser: tseslint.parser, parserOptions: { ecmaFeatures: { jsx: true } } },
    plugins: { "@typescript-eslint": tseslint.plugin },
    rules: {
      ...regras,
      "@typescript-eslint/no-unused-vars": ["error", naoUsadas],
      "@typescript-eslint/no-explicit-any": "error",
    },
  },
  { linterOptions: { reportUnusedDisableDirectives: "off" } },
];
