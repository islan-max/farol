export function somar(lista) {
  var total = 0;
  for (var i = 0; i < lista.length; i++) {
    if (lista[i] == 0) { continue; }
    total += lista[i];
  }
  return total;
}
