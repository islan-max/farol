// Regras fixas do Farol para JavaScript e TypeScript. O ESLint do repositório revisado é ignorado:
// o Farol decide as regras. Só entram regras que têm lição escrita em src/farol/licoes/javascript.
import tseslint from "typescript-eslint";

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
    rules: { ...regras, "no-unused-vars": "error" },
  },
  {
    // Só o parser e regras sem informação de tipo: não precisa de tsconfig e nada é executado.
    files: ["**/*.{ts,tsx,mts,cts}"],
    languageOptions: { parser: tseslint.parser, parserOptions: { ecmaFeatures: { jsx: true } } },
    plugins: { "@typescript-eslint": tseslint.plugin },
    rules: {
      ...regras,
      "@typescript-eslint/no-unused-vars": "error",
      "@typescript-eslint/no-explicit-any": "error",
    },
  },
  { linterOptions: { reportUnusedDisableDirectives: "off" } },
];
