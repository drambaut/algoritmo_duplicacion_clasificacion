import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "outputs";
const outputPath = `${outputDir}/propuestas_prueba_plantilla_pnd.xlsx`;

const headers = [
  "radicado", "fecha", "ipcliente", "dpto_codi", "muni_codi", "localizacion", "sexo", "orientacion", "discapacidad", "participacion", "instancia", "organizacion", "infpoblacional",
  "eje1_presenta", "eje1_tema", "eje1_propuesta", "eje1_dpto", "eje1_mcpio", "eje1_poblacion", "eje1_resultado",
  "eje2_presenta", "eje2_tema", "eje2_propuesta", "eje2_dpto", "eje2_mcpio", "eje2_poblacion", "eje2_resultado",
  "eje3_presenta", "eje3_tema", "eje3_propuesta", "eje3_dpto", "eje3_mcpio", "eje3_poblacion", "eje3_resultado",
  "eje4_presenta", "eje4_tema", "eje4_propuesta", "eje4_dpto", "eje4_mcpio", "eje4_poblacion", "eje4_resultado",
  "eje5_presenta", "eje5_tema", "eje5_propuesta", "eje5_dpto", "eje5_mcpio", "eje5_poblacion", "eje5_resultado",
  "eje6_presenta", "eje6_tema", "eje6_propuesta", "eje6_dpto", "eje6_mcpio", "eje6_poblacion", "eje6_resultado",
  "eje7_presenta", "eje7_tema", "eje7_propuesta", "eje7_dpto", "eje7_mcpio", "eje7_poblacion", "eje7_resultado",
  "eje8_presenta", "eje8_eje", "eje8_tema", "eje8_propuesta", "eje8_dpto", "eje8_mcpio", "eje8_poblacion", "eje8_resultado",
];

function row(values) {
  return headers.map((header) => values[header] ?? "");
}

function base(radicado) {
  return {
    radicado,
    fecha: new Date("2026-10-17T00:00:00"),
    dpto_codi: 15,
    muni_codi: 22,
    localizacion: "Rural",
    participacion: "Individual",
  };
}

const rows = [
  row({
    ...base("TEST-001"), eje1_presenta: "Si", eje1_tema: "Movilidad rural",
    eje1_propuesta: "Arreglar las vias veredales y los puentes de Almeida", eje1_dpto: 15, eje1_mcpio: 22,
    eje1_poblacion: "Poblacion general", eje1_resultado: "Mejorar la conectividad rural a 2030",
  }),
  row({
    ...base("TEST-002"), eje1_presenta: "Si", eje1_tema: "Movilidad rural",
    eje1_propuesta: "Mejorar las vias y puentes veredales de Almeida", eje1_dpto: 15, eje1_mcpio: 22,
    eje1_poblacion: "Poblacion general", eje1_resultado: "Mejorar la conectividad rural a 2030",
  }),
  row({
    ...base("TEST-003"), eje1_presenta: "Si", eje1_tema: "Movilidad rural",
    eje1_propuesta: "Arreglar vias veredlales y puentes de Almeida", eje1_dpto: 15, eje1_mcpio: 22,
    eje1_poblacion: "Poblacion general", eje1_resultado: "Mejorar la conectividad rural a 2030",
  }),
  row({
    ...base("TEST-004"), muni_codi: 1, localizacion: "Urbana", eje1_presenta: "Si", eje1_tema: "Movilidad rural",
    eje1_propuesta: "Arreglar las vias veredales y los puentes de Almeida", eje1_dpto: 15, eje1_mcpio: 1,
    eje1_poblacion: "Poblacion general", eje1_resultado: "Mejorar la conectividad rural a 2030",
  }),
  row({
    ...base("TEST-005"), eje2_presenta: "Si", eje2_tema: "Alumbrado publico",
    eje2_propuesta: "Instalar luminarias solares en los parques publicos", eje2_dpto: 15, eje2_mcpio: 22,
    eje2_poblacion: "Poblacion general", eje2_resultado: "Aumentar la seguridad en espacios publicos",
  }),
  row({
    ...base("TEST-006"), eje2_presenta: "Si", eje2_tema: "Alumbrado publico",
    eje2_propuesta: "Instalar luminarias solares en parques publicos de Almeida", eje2_dpto: 15, eje2_mcpio: 22,
    eje2_poblacion: "Poblacion general", eje2_resultado: "Aumentar la seguridad en espacios publicos",
  }),
  row({
    ...base("TEST-007"), eje3_presenta: "Si", eje3_tema: "Salud materna",
    eje3_propuesta: "Dotar el centro de salud con equipos de atencion materna", eje3_dpto: 15, eje3_mcpio: 22,
    eje3_poblacion: "Poblacion general", eje3_resultado: "Reducir la mortalidad materna",
  }),
  row({
    ...base("TEST-008"), eje3_presenta: "Si", eje3_tema: "Recreacion",
    eje3_propuesta: "Construir una cancha cubierta para jovenes", eje3_dpto: 15, eje3_mcpio: 22,
    eje3_poblacion: "Poblacion general", eje3_resultado: "Incrementar la actividad fisica",
  }),
  row({
    ...base("TEST-009"), eje1_presenta: "Si", eje1_tema: "Movilidad rural",
    eje1_propuesta: "Reparar caminos rurales para mejorar el transporte", eje1_dpto: 15, eje1_mcpio: 22,
    eje1_poblacion: "Poblacion general", eje1_resultado: "Mejorar la conectividad rural a 2030",
    eje2_presenta: "Si", eje2_tema: "Alumbrado publico",
    eje2_propuesta: "Instalar luminarias solares en los parques publicos", eje2_dpto: 15, eje2_mcpio: 22,
    eje2_poblacion: "Poblacion general", eje2_resultado: "Aumentar la seguridad en espacios publicos",
  }),
];

const workbook = Workbook.create();
const cut = workbook.worksheets.add("corte");
cut.showGridLines = false;
cut.getRange("A1:BR10").values = [headers, ...rows];
cut.getRange("A1:BR1").format = {
  fill: "#005A9C",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
};
cut.getRange("A2:BR10").format = {
  font: { name: "Arial", size: 10, color: "#1F2933" },
  verticalAlignment: "center",
};
cut.getRange("A1:BR10").format.borders = { preset: "outside", style: "thin", color: "#B8C8D6" };
cut.getRange("B2:B10").format.numberFormat = "yyyy-mm-dd";
cut.getRange("A:A").format.columnWidth = 15;
cut.getRange("B:B").format.columnWidth = 12;
cut.getRange("C:M").format.columnWidth = 13;
for (const start of ["N", "U", "AB", "AI", "AP", "AW", "BD", "BK"]) {
  cut.getRange(`${start}:${start}`).format.columnWidth = 12;
}
for (const column of ["P", "W", "AD", "AK", "AR", "AY", "BF", "BN"]) {
  cut.getRange(`${column}:${column}`).format.columnWidth = 38;
}
for (const column of ["T", "AA", "AH", "AO", "AV", "BC", "BJ", "BR"]) {
  cut.getRange(`${column}:${column}`).format.columnWidth = 30;
}
cut.getRange("A1:BR10").format.wrapText = true;
cut.getRange("A1:BR10").format.autofitRows();
cut.getRange("A1:BR1").format.rowHeight = 42;
cut.freezePanes.freezeRows(1);
cut.tables.add("A1:BR10", true, "CortePrueba");

const guide = workbook.worksheets.add("Guia de prueba");
guide.showGridLines = false;
guide.getRange("A1:D1").merge();
guide.getRange("A1").values = [["Propuestas sintéticas para probar la detección de duplicidad"]];
guide.getRange("A1:D1").format = {
  font: { name: "Arial", size: 14, bold: true, color: "#1F2933" },
  verticalAlignment: "center",
};
guide.getRange("A3:D3").values = [["Caso", "Radicados", "Comportamiento esperado", "Motivo"]];
guide.getRange("A4:D8").values = [
  ["Duplicado con redacción distinta", "TEST-001 y TEST-002", "Alerta alta", "Mismo municipio y bloque. Comparten vías, puentes y resultado esperado."],
  ["Error de digitación", "TEST-001 y TEST-003", "Alerta alta", "La palabra veredales aparece con una letra omitida."],
  ["Municipio distinto", "TEST-001 y TEST-004", "No se comparan", "La propuesta es igual, pero cambia el municipio."],
  ["Alumbrado", "TEST-005, TEST-006 y TEST-009", "Alerta alta", "TEST-005 y TEST-009 son iguales. TEST-006 es una variante cercana."],
  ["Propuestas sin duplicidad", "TEST-007 y TEST-008", "Sin alerta", "Necesidades distintas en bloques distintos."],
];
guide.getRange("A3:D3").format = {
  fill: "#005A9C",
  font: { name: "Arial", size: 10, bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
guide.getRange("A4:D8").format = { font: { name: "Arial", size: 10, color: "#1F2933" }, wrapText: true, verticalAlignment: "top" };
guide.getRange("A3:D8").format.borders = { preset: "all", style: "thin", color: "#D9E2EA" };
guide.getRange("A:A").format.columnWidth = 26;
guide.getRange("B:B").format.columnWidth = 30;
guide.getRange("C:C").format.columnWidth = 28;
guide.getRange("D:D").format.columnWidth = 60;
guide.getRange("A1:D8").format.autofitRows();

workbook.recalculate();
await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const check = await workbook.inspect({
  kind: "table",
  range: "corte!A1:BR10",
  include: "values",
  tableMaxRows: 10,
  tableMaxCols: 70,
});
console.log(check.ndjson);
const preview = await workbook.render({ sheetName: "Guia de prueba", range: "A1:D8", scale: 1.5, format: "png" });
await fs.writeFile(`${outputDir}/propuestas_prueba_guia.png`, new Uint8Array(await preview.arrayBuffer()));
console.log(outputPath);
