var total: number = 0;
export function somar(lista: number[], frete: number) {
  for (var i = 0; i < lista.length; i++) {
    if (lista[i] == 0) { continue; }
    total += lista[i];
  }
  try { return eval("total"); } catch (e) {}
}
